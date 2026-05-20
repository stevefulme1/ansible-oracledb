#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: oracledb_role_info
short_description: Gather Oracle database role information
description:
  - Query DBA_ROLES, DBA_SYS_PRIVS, and DBA_ROLE_PRIVS for role metadata.
  - Returns role details including granted privileges.
version_added: "0.1.0"
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of a specific role to query.
      - If omitted, all roles are returned.
    type: str
extends_documentation_fragment:
  - stevefulme1.oracledb.oracledb
"""

EXAMPLES = r"""
- name: Get all roles
  stevefulme1.oracledb.oracledb_role_info:
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba

- name: Get info for a specific role
  stevefulme1.oracledb.oracledb_role_info:
    name: DBA
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba
"""

RETURN = r"""
roles:
  description: List of role details.
  type: list
  elements: dict
  returned: always
  contains:
    role:
      description: Role name.
      type: str
    authentication_type:
      description: Authentication type (NONE, PASSWORD, etc.).
      type: str
    system_privileges:
      description: List of system privileges granted to the role.
      type: list
      elements: str
    granted_roles:
      description: List of roles granted to the role.
      type: list
      elements: str
  sample:
    - role: DBA
      authentication_type: NONE
      system_privileges:
        - CREATE SESSION
        - ALTER SYSTEM
      granted_roles:
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
        sql = "SELECT role, authentication_type FROM dba_roles"
        params = None
        if module.params["name"]:
            sql += " WHERE role = :1"
            params = [module.params["name"].upper()]

        rows = client.fetchall(sql, params)

        roles = []
        for row in rows:
            role_name = row[0]

            # System privileges
            priv_rows = client.fetchall(
                "SELECT privilege FROM dba_sys_privs WHERE grantee = :1",
                [role_name],
            )
            sys_privs = [p[0] for p in priv_rows]

            # Granted roles
            role_rows = client.fetchall(
                "SELECT granted_role FROM dba_role_privs WHERE grantee = :1",
                [role_name],
            )
            granted_roles = [r[0] for r in role_rows]

            roles.append(
                {
                    "role": row[0],
                    "authentication_type": row[1],
                    "system_privileges": sys_privs,
                    "granted_roles": granted_roles,
                }
            )

        module.exit_json(changed=False, roles=roles)
    finally:
        client.close()


if __name__ == "__main__":
    main()
