#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: oracledb_user
short_description: Manage Oracle database users
description:
  - Create, alter, or drop Oracle database users.
  - Grant or revoke roles from users.
  - Manage default and temporary tablespaces.
version_added: "0.1.0"
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Username to manage.
    type: str
    required: true
  state:
    description:
      - Desired state of the user.
    type: str
    choices: [present, absent, locked, unlocked]
    default: present
  password:
    description:
      - Password for the user.
      - Required when creating a new user.
    type: str
  default_tablespace:
    description:
      - Default tablespace for the user.
    type: str
  temporary_tablespace:
    description:
      - Temporary tablespace for the user.
    type: str
  profile:
    description:
      - Profile to assign to the user.
    type: str
  roles:
    description:
      - List of roles to grant to the user.
      - Replaces all current role grants when specified.
    type: list
    elements: str
  quota:
    description:
      - Tablespace quotas as a dictionary.
      - Keys are tablespace names, values are quota sizes (for example V(unlimited), V(100M)).
    type: dict
extends_documentation_fragment:
  - stevefulme1.oracledb.oracledb
"""

EXAMPLES = r"""
- name: Create a user with roles
  stevefulme1.oracledb.oracledb_user:
    name: app_user
    password: "{{ app_password }}"
    default_tablespace: USERS
    temporary_tablespace: TEMP
    roles:
      - CONNECT
      - RESOURCE
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba

- name: Lock a user account
  stevefulme1.oracledb.oracledb_user:
    name: app_user
    state: locked
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba

- name: Drop a user
  stevefulme1.oracledb.oracledb_user:
    name: app_user
    state: absent
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba
"""

RETURN = r"""
user:
  description: Name of the user affected.
  type: str
  returned: always
  sample: APP_USER
sql:
  description: SQL statements executed.
  type: list
  elements: str
  returned: changed
  sample: ["CREATE USER app_user IDENTIFIED BY *** DEFAULT TABLESPACE USERS"]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.oracledb.plugins.module_utils.oracledb_client import (
    OracleDBClient,
    oracledb_argument_spec,
)


def get_user(client, name):
    """Fetch user info from DBA_USERS."""
    row = client.fetchone(
        "SELECT username, account_status, default_tablespace, "
        "temporary_tablespace, profile "
        "FROM dba_users WHERE username = :1",
        [name.upper()],
    )
    if row:
        return {
            "username": row[0],
            "account_status": row[1],
            "default_tablespace": row[2],
            "temporary_tablespace": row[3],
            "profile": row[4],
        }
    return None


def get_user_roles(client, name):
    """Fetch granted roles from DBA_ROLE_PRIVS."""
    rows = client.fetchall(
        "SELECT granted_role FROM dba_role_privs WHERE grantee = :1",
        [name.upper()],
    )
    return [r[0] for r in rows]


def main():
    argument_spec = oracledb_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        state=dict(
            type="str",
            choices=["present", "absent", "locked", "unlocked"],
            default="present",
        ),
        password=dict(type="str", no_log=True),
        default_tablespace=dict(type="str"),
        temporary_tablespace=dict(type="str"),
        profile=dict(type="str"),
        roles=dict(type="list", elements="str"),
        quota=dict(type="dict"),
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
        current = get_user(client, name)
        executed = []
        changed = False

        if state == "absent":
            if current:
                sql = "DROP USER %s CASCADE" % name
                if not module.check_mode:
                    client.execute(sql)
                executed.append(sql)
                changed = True
            module.exit_json(changed=changed, user=name, sql=executed)
            return

        if state in ("locked", "unlocked"):
            if not current:
                module.fail_json(msg="User %s does not exist." % name)
            lock_sql = "ALTER USER %s ACCOUNT %s" % (
                name,
                "LOCK" if state == "locked" else "UNLOCK",
            )
            is_locked = "LOCKED" in (current.get("account_status") or "")
            if (state == "locked" and not is_locked) or (
                state == "unlocked" and is_locked
            ):
                if not module.check_mode:
                    client.execute(lock_sql)
                executed.append(lock_sql)
                changed = True
            module.exit_json(changed=changed, user=name, sql=executed)
            return

        # state == present
        if not current:
            # Create user
            password = module.params["password"]
            if not password:
                module.fail_json(msg="password is required when creating a user.")
            parts = ["CREATE USER %s IDENTIFIED BY \"%s\"" % (name, password)]
            if module.params["default_tablespace"]:
                parts.append(
                    "DEFAULT TABLESPACE %s" % module.params["default_tablespace"]
                )
            if module.params["temporary_tablespace"]:
                parts.append(
                    "TEMPORARY TABLESPACE %s"
                    % module.params["temporary_tablespace"]
                )
            if module.params["profile"]:
                parts.append("PROFILE %s" % module.params["profile"])
            sql = " ".join(parts)
            if not module.check_mode:
                client.execute(sql)
            # Mask password in output
            executed.append(sql.replace(password, "***"))
            changed = True
        else:
            # Alter existing user
            if module.params["password"]:
                sql = 'ALTER USER %s IDENTIFIED BY "%s"' % (
                    name,
                    module.params["password"],
                )
                if not module.check_mode:
                    client.execute(sql)
                executed.append(
                    sql.replace(module.params["password"], "***")
                )
                changed = True
            if (
                module.params["default_tablespace"]
                and module.params["default_tablespace"].upper()
                != current["default_tablespace"]
            ):
                sql = "ALTER USER %s DEFAULT TABLESPACE %s" % (
                    name,
                    module.params["default_tablespace"],
                )
                if not module.check_mode:
                    client.execute(sql)
                executed.append(sql)
                changed = True
            if (
                module.params["temporary_tablespace"]
                and module.params["temporary_tablespace"].upper()
                != current["temporary_tablespace"]
            ):
                sql = "ALTER USER %s TEMPORARY TABLESPACE %s" % (
                    name,
                    module.params["temporary_tablespace"],
                )
                if not module.check_mode:
                    client.execute(sql)
                executed.append(sql)
                changed = True
            if (
                module.params["profile"]
                and module.params["profile"].upper() != current["profile"]
            ):
                sql = "ALTER USER %s PROFILE %s" % (
                    name,
                    module.params["profile"],
                )
                if not module.check_mode:
                    client.execute(sql)
                executed.append(sql)
                changed = True

        # Handle quotas
        if module.params["quota"]:
            for ts, quota_val in module.params["quota"].items():
                sql = "ALTER USER %s QUOTA %s ON %s" % (
                    name,
                    quota_val,
                    ts.upper(),
                )
                if not module.check_mode:
                    client.execute(sql)
                executed.append(sql)
                changed = True

        # Handle roles
        if module.params["roles"] is not None:
            wanted = set(r.upper() for r in module.params["roles"])
            current_roles = set(get_user_roles(client, name))

            to_grant = wanted - current_roles
            to_revoke = current_roles - wanted

            for role in to_grant:
                sql = "GRANT %s TO %s" % (role, name)
                if not module.check_mode:
                    client.execute(sql)
                executed.append(sql)
                changed = True

            for role in to_revoke:
                sql = "REVOKE %s FROM %s" % (role, name)
                if not module.check_mode:
                    client.execute(sql)
                executed.append(sql)
                changed = True

        result = dict(changed=changed, user=name)
        if executed:
            result["sql"] = executed
        module.exit_json(**result)
    finally:
        client.close()


if __name__ == "__main__":
    main()
