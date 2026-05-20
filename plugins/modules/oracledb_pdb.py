#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: oracledb_pdb
short_description: Manage Oracle pluggable databases
description:
  - Create, open, close, or drop pluggable databases (PDBs) in a CDB.
  - Requires connection to the CDB root as SYSDBA.
version_added: "0.1.0"
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of the pluggable database.
    type: str
    required: true
  state:
    description:
      - Desired state of the PDB.
      - V(present) creates the PDB if it does not exist.
      - V(absent) drops the PDB.
      - V(open) opens the PDB for read-write access.
      - V(closed) closes the PDB.
    type: str
    choices: [present, absent, open, closed]
    default: present
  admin_user:
    description:
      - Admin username for the new PDB.
      - Required when creating a new PDB.
    type: str
  admin_password:
    description:
      - Admin password for the new PDB.
      - Required when creating a new PDB.
    type: str
  file_name_convert:
    description:
      - File name conversion pattern for the PDB datafiles.
      - Format is a comma-separated list of pairs like V(source1,target1,source2,target2).
    type: str
  save_state:
    description:
      - Whether to save the PDB open state so it auto-opens on CDB restart.
    type: bool
    default: false
  unplug_path:
    description:
      - XML file path for unplugging the PDB.
      - Only used when O(state=absent) to unplug instead of drop.
    type: str
extends_documentation_fragment:
  - stevefulme1.oracledb.oracledb
"""

EXAMPLES = r"""
- name: Create a PDB
  stevefulme1.oracledb.oracledb_pdb:
    name: pdb_app
    state: present
    admin_user: pdb_admin
    admin_password: "{{ pdb_admin_pass }}"
    file_name_convert: "/u01/oradata/CDB/pdbseed,/u01/oradata/CDB/pdb_app"
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: CDB
    oracle_mode: sysdba

- name: Open a PDB
  stevefulme1.oracledb.oracledb_pdb:
    name: pdb_app
    state: open
    save_state: true
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: CDB
    oracle_mode: sysdba

- name: Drop a PDB
  stevefulme1.oracledb.oracledb_pdb:
    name: pdb_app
    state: absent
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: CDB
    oracle_mode: sysdba
"""

RETURN = r"""
pdb:
  description: Name of the PDB affected.
  type: str
  returned: always
  sample: PDB_APP
sql:
  description: SQL statements executed.
  type: list
  elements: str
  returned: changed
  sample: ["CREATE PLUGGABLE DATABASE pdb_app ADMIN USER pdb_admin IDENTIFIED BY ***"]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.oracledb.plugins.module_utils.oracledb_client import (
    OracleDBClient,
    oracledb_argument_spec,
)


def get_pdb(client, name):
    """Get PDB info from V$PDBS."""
    row = client.fetchone(
        "SELECT name, open_mode FROM v$pdbs WHERE name = :1",
        [name.upper()],
    )
    if row:
        return {"name": row[0], "open_mode": row[1]}
    return None


def main():
    argument_spec = oracledb_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        state=dict(
            type="str",
            choices=["present", "absent", "open", "closed"],
            default="present",
        ),
        admin_user=dict(type="str"),
        admin_password=dict(type="str", no_log=True),
        file_name_convert=dict(type="str"),
        save_state=dict(type="bool", default=False),
        unplug_path=dict(type="str"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("oracle_service_name", "oracle_sid")],
        required_one_of=[("oracle_service_name", "oracle_sid")],
        supports_check_mode=True,
    )

    client = OracleDBClient(module)
    name = module.params["name"].upper()
    state = module.params["state"]

    try:
        current = get_pdb(client, name)
        executed = []
        changed = False

        if state == "absent":
            if current:
                # Close PDB first if open
                if current["open_mode"] != "MOUNTED":
                    sql = "ALTER PLUGGABLE DATABASE %s CLOSE IMMEDIATE" % name
                    if not module.check_mode:
                        client.execute(sql)
                    executed.append(sql)

                if module.params["unplug_path"]:
                    sql = "ALTER PLUGGABLE DATABASE %s UNPLUG INTO '%s'" % (
                        name,
                        module.params["unplug_path"],
                    )
                    if not module.check_mode:
                        client.execute(sql)
                    executed.append(sql)

                sql = (
                    "DROP PLUGGABLE DATABASE %s INCLUDING DATAFILES" % name
                )
                if not module.check_mode:
                    client.execute(sql)
                executed.append(sql)
                changed = True

        elif state == "present":
            if not current:
                admin_user = module.params["admin_user"]
                admin_password = module.params["admin_password"]
                if not admin_user or not admin_password:
                    module.fail_json(
                        msg="admin_user and admin_password are required "
                        "when creating a PDB."
                    )
                parts = [
                    "CREATE PLUGGABLE DATABASE %s" % name,
                    'ADMIN USER %s IDENTIFIED BY "%s"'
                    % (admin_user, admin_password),
                ]
                if module.params["file_name_convert"]:
                    parts.append(
                        "FILE_NAME_CONVERT = (%s)"
                        % module.params["file_name_convert"]
                    )
                sql = " ".join(parts)
                if not module.check_mode:
                    client.execute(sql)
                executed.append(sql.replace(admin_password, "***"))
                changed = True

        elif state == "open":
            if not current:
                module.fail_json(msg="PDB %s does not exist." % name)
            if current["open_mode"] != "READ WRITE":
                sql = "ALTER PLUGGABLE DATABASE %s OPEN" % name
                if not module.check_mode:
                    client.execute(sql)
                executed.append(sql)
                changed = True

                if module.params["save_state"]:
                    sql = "ALTER PLUGGABLE DATABASE %s SAVE STATE" % name
                    if not module.check_mode:
                        client.execute(sql)
                    executed.append(sql)

        elif state == "closed":
            if not current:
                module.fail_json(msg="PDB %s does not exist." % name)
            if current["open_mode"] != "MOUNTED":
                sql = "ALTER PLUGGABLE DATABASE %s CLOSE IMMEDIATE" % name
                if not module.check_mode:
                    client.execute(sql)
                executed.append(sql)
                changed = True

        result = dict(changed=changed, pdb=name)
        if executed:
            result["sql"] = executed
        module.exit_json(**result)
    finally:
        client.close()


if __name__ == "__main__":
    main()
