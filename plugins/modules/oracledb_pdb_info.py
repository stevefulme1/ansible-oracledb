#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: oracledb_pdb_info
short_description: Gather Oracle pluggable database information
description:
  - Query V$PDBS and CDB_PDBS for pluggable database metadata.
  - Returns PDB details including open mode and status.
version_added: "0.1.0"
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of a specific PDB to query.
      - If omitted, all PDBs are returned.
    type: str
extends_documentation_fragment:
  - stevefulme1.oracledb.oracledb
"""

EXAMPLES = r"""
- name: Get all PDB info
  stevefulme1.oracledb.oracledb_pdb_info:
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: CDB
    oracle_mode: sysdba

- name: Get info for a specific PDB
  stevefulme1.oracledb.oracledb_pdb_info:
    name: PDB_APP
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: CDB
    oracle_mode: sysdba
"""

RETURN = r"""
pdbs:
  description: List of PDB details.
  type: list
  elements: dict
  returned: always
  contains:
    name:
      description: PDB name.
      type: str
    con_id:
      description: Container ID.
      type: int
    open_mode:
      description: Current open mode (READ WRITE, READ ONLY, MOUNTED).
      type: str
    restricted:
      description: Whether PDB is in restricted mode.
      type: str
    status:
      description: PDB status from CDB_PDBS.
      type: str
    creation_scn:
      description: SCN at which the PDB was created.
      type: int
  sample:
    - name: PDB_APP
      con_id: 3
      open_mode: READ WRITE
      restricted: "NO"
      status: NORMAL
      creation_scn: 1234567
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.oracledb.plugins.module_utils.oracledb_client import (
    OracleDBClient,
    oracledb_argument_spec,
)


def main():
    argument_spec = oracledb_argument_spec()
    argument_spec.update(
        name=dict(type="str"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("oracle_service_name", "oracle_sid")],
        required_one_of=[("oracle_service_name", "oracle_sid")],
        supports_check_mode=True,
    )

    client = OracleDBClient(module)

    try:
        sql = (
            "SELECT p.name, p.con_id, p.open_mode, p.restricted, "
            "c.status, c.creation_scn "
            "FROM v$pdbs p "
            "LEFT JOIN cdb_pdbs c ON p.con_id = c.con_id"
        )
        params = None
        if module.params["name"]:
            sql += " WHERE p.name = :1"
            params = [module.params["name"].upper()]

        rows = client.fetchall(sql, params)

        pdbs = []
        for row in rows:
            pdbs.append(
                {
                    "name": row[0],
                    "con_id": row[1],
                    "open_mode": row[2],
                    "restricted": row[3],
                    "status": row[4],
                    "creation_scn": row[5],
                }
            )

        module.exit_json(changed=False, pdbs=pdbs)
    finally:
        client.close()


if __name__ == "__main__":
    main()
