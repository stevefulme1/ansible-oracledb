#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: oracledb_user_info
short_description: Gather Oracle database user information
description:
  - Query DBA_USERS and DBA_ROLE_PRIVS for user metadata.
  - Returns account status, tablespaces, profile, and granted roles.
version_added: "0.1.0"
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of a specific user to query.
      - If omitted, all users are returned.
    type: str
extends_documentation_fragment:
  - stevefulme1.oracledb.oracledb
"""

EXAMPLES = r"""
- name: Get all user info
  stevefulme1.oracledb.oracledb_user_info:
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba
  register: user_info

- name: Get info for a specific user
  stevefulme1.oracledb.oracledb_user_info:
    name: APP_USER
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba
"""

RETURN = r"""
users:
  description: List of user details.
  type: list
  elements: dict
  returned: always
  contains:
    username:
      description: Username.
      type: str
    account_status:
      description: Account status (OPEN, LOCKED, EXPIRED, etc.).
      type: str
    default_tablespace:
      description: Default tablespace.
      type: str
    temporary_tablespace:
      description: Temporary tablespace.
      type: str
    profile:
      description: Assigned profile.
      type: str
    created:
      description: Account creation date.
      type: str
    roles:
      description: List of granted roles.
      type: list
      elements: str
  sample:
    - username: APP_USER
      account_status: OPEN
      default_tablespace: USERS
      temporary_tablespace: TEMP
      profile: DEFAULT
      created: "2024-01-15 10:30:00"
      roles:
        - CONNECT
        - RESOURCE
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
            "SELECT username, account_status, default_tablespace, "
            "temporary_tablespace, profile, "
            "TO_CHAR(created, 'YYYY-MM-DD HH24:MI:SS') "
            "FROM dba_users"
        )
        params = None
        if module.params["name"]:
            sql += " WHERE username = :1"
            params = [module.params["name"].upper()]

        rows = client.fetchall(sql, params)

        users = []
        for row in rows:
            uname = row[0]
            # Fetch roles
            role_rows = client.fetchall(
                "SELECT granted_role FROM dba_role_privs WHERE grantee = :1",
                [uname],
            )
            roles = [r[0] for r in role_rows]

            users.append(
                {
                    "username": row[0],
                    "account_status": row[1],
                    "default_tablespace": row[2],
                    "temporary_tablespace": row[3],
                    "profile": row[4],
                    "created": row[5],
                    "roles": roles,
                }
            )

        module.exit_json(changed=False, users=users)
    finally:
        client.close()


if __name__ == "__main__":
    main()
