#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: oracledb_tablespace_info
short_description: Gather Oracle tablespace information
description:
  - Query DBA_TABLESPACES and DBA_DATA_FILES for tablespace metadata.
  - Returns details including size, free space, and autoextend settings.
version_added: "0.1.0"
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of a specific tablespace to query.
      - If omitted, all tablespaces are returned.
    type: str
extends_documentation_fragment:
  - stevefulme1.oracledb.oracledb
"""

EXAMPLES = r"""
- name: Get all tablespace info
  stevefulme1.oracledb.oracledb_tablespace_info:
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba
  register: ts_info

- name: Get info for a specific tablespace
  stevefulme1.oracledb.oracledb_tablespace_info:
    name: USERS
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba
"""

RETURN = r"""
tablespaces:
  description: List of tablespace details.
  type: list
  elements: dict
  returned: always
  contains:
    tablespace_name:
      description: Name of the tablespace.
      type: str
    status:
      description: Status of the tablespace (ONLINE, OFFLINE, READ ONLY).
      type: str
    contents:
      description: Tablespace type (PERMANENT, TEMPORARY, UNDO).
      type: str
    bigfile:
      description: Whether it is a bigfile tablespace.
      type: str
    block_size:
      description: Block size in bytes.
      type: int
    datafiles:
      description: List of datafiles in the tablespace.
      type: list
      elements: dict
  sample:
    - tablespace_name: USERS
      status: ONLINE
      contents: PERMANENT
      bigfile: "NO"
      block_size: 8192
      datafiles:
        - file_name: "/u01/oradata/ORCL/users01.dbf"
          bytes: 5242880
          autoextensible: "YES"
          maxbytes: 34359721984
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
        # Fetch tablespaces
        ts_sql = (
            "SELECT tablespace_name, status, contents, bigfile, block_size "
            "FROM dba_tablespaces"
        )
        params = None
        if module.params["name"]:
            ts_sql += " WHERE tablespace_name = :1"
            params = [module.params["name"].upper()]

        ts_rows = client.fetchall(ts_sql, params)

        tablespaces = []
        for row in ts_rows:
            ts_name = row[0]
            # Fetch datafiles for this tablespace
            df_rows = client.fetchall(
                "SELECT file_name, bytes, autoextensible, maxbytes "
                "FROM dba_data_files WHERE tablespace_name = :1",
                [ts_name],
            )
            datafiles = [
                {
                    "file_name": df[0],
                    "bytes": df[1],
                    "autoextensible": df[2],
                    "maxbytes": df[3],
                }
                for df in df_rows
            ]

            tablespaces.append(
                {
                    "tablespace_name": row[0],
                    "status": row[1],
                    "contents": row[2],
                    "bigfile": row[3],
                    "block_size": row[4],
                    "datafiles": datafiles,
                }
            )

        module.exit_json(changed=False, tablespaces=tablespaces)
    finally:
        client.close()


if __name__ == "__main__":
    main()
