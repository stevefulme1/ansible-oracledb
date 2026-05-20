#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: oracledb_role
short_description: Manage Oracle database roles
description:
  - Create or drop Oracle database roles.
  - Grant system and object privileges to roles.
version_added: "0.1.0"
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of the role.
    type: str
    required: true
  state:
    description:
      - Desired state of the role.
    type: str
    choices: [present, absent]
    default: present
  privileges:
    description:
      - List of system privileges to grant to the role.
      - Replaces all current privilege grants when specified.
    type: list
    elements: str
  roles:
    description:
      - List of roles to grant to this role.
    type: list
    elements: str
extends_documentation_fragment:
  - stevefulme1.oracledb.oracledb
"""

EXAMPLES = r"""
- name: Create a role with privileges
  stevefulme1.oracledb.oracledb_role:
    name: APP_READONLY
    privileges:
      - CREATE SESSION
      - SELECT ANY TABLE
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba

- name: Drop a role
  stevefulme1.oracledb.oracledb_role:
    name: APP_READONLY
    state: absent
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba
"""

RETURN = r"""
role:
  description: Name of the role affected.
  type: str
  returned: always
  sample: APP_READONLY
sql:
  description: SQL statements executed.
  type: list
  elements: str
  returned: changed
  sample: ["CREATE ROLE APP_READONLY", "GRANT CREATE SESSION TO APP_READONLY"]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.oracledb.plugins.module_utils.oracledb_client import (
    OracleDBClient,
    oracledb_argument_spec,
)


def role_exists(client, name):
    """Check if role exists in DBA_ROLES."""
    row = client.fetchone(
        "SELECT role FROM dba_roles WHERE role = :1", [name.upper()]
    )
    return row is not None


def get_role_sys_privs(client, name):
    """Get system privileges granted to a role."""
    rows = client.fetchall(
        "SELECT privilege FROM dba_sys_privs WHERE grantee = :1",
        [name.upper()],
    )
    return set(r[0] for r in rows)


def get_role_role_privs(client, name):
    """Get roles granted to a role."""
    rows = client.fetchall(
        "SELECT granted_role FROM dba_role_privs WHERE grantee = :1",
        [name.upper()],
    )
    return set(r[0] for r in rows)


def main():
    argument_spec = oracledb_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        privileges=dict(type="list", elements="str"),
        roles=dict(type="list", elements="str"),
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
        exists = role_exists(client, name)
        executed = []
        changed = False

        if state == "absent":
            if exists:
                sql = "DROP ROLE %s" % name
                if not module.check_mode:
                    client.execute(sql)
                executed.append(sql)
                changed = True
            module.exit_json(changed=changed, role=name, sql=executed)
            return

        # state == present
        if not exists:
            sql = "CREATE ROLE %s" % name
            if not module.check_mode:
                client.execute(sql)
            executed.append(sql)
            changed = True

        # Handle system privileges
        if module.params["privileges"] is not None:
            wanted = set(p.upper() for p in module.params["privileges"])
            current_privs = get_role_sys_privs(client, name) if exists else set()

            for priv in wanted - current_privs:
                sql = "GRANT %s TO %s" % (priv, name)
                if not module.check_mode:
                    client.execute(sql)
                executed.append(sql)
                changed = True

            for priv in current_privs - wanted:
                sql = "REVOKE %s FROM %s" % (priv, name)
                if not module.check_mode:
                    client.execute(sql)
                executed.append(sql)
                changed = True

        # Handle role grants
        if module.params["roles"] is not None:
            wanted_roles = set(r.upper() for r in module.params["roles"])
            current_roles = get_role_role_privs(client, name) if exists else set()

            for role in wanted_roles - current_roles:
                sql = "GRANT %s TO %s" % (role, name)
                if not module.check_mode:
                    client.execute(sql)
                executed.append(sql)
                changed = True

            for role in current_roles - wanted_roles:
                sql = "REVOKE %s FROM %s" % (role, name)
                if not module.check_mode:
                    client.execute(sql)
                executed.append(sql)
                changed = True

        result = dict(changed=changed, role=name)
        if executed:
            result["sql"] = executed
        module.exit_json(**result)
    finally:
        client.close()


if __name__ == "__main__":
    main()
