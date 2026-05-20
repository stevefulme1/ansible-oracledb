#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: oracledb_parameter
short_description: Manage Oracle database parameters
description:
  - Set or reset Oracle database initialization parameters.
  - Uses ALTER SYSTEM SET/RESET via python-oracledb driver.
version_added: "0.1.0"
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of the initialization parameter.
    type: str
    required: true
  value:
    description:
      - Value to set the parameter to.
      - Required when O(state=present).
    type: str
  state:
    description:
      - V(present) sets the parameter value.
      - V(absent) resets the parameter to its default.
    type: str
    choices: [present, absent]
    default: present
  scope:
    description:
      - Scope for the parameter change.
      - V(memory) changes only the running instance.
      - V(spfile) changes only the SPFILE (requires restart).
      - V(both) changes both memory and SPFILE.
    type: str
    choices: [memory, spfile, both]
    default: both
extends_documentation_fragment:
  - stevefulme1.oracledb.oracledb
"""

EXAMPLES = r"""
- name: Set a parameter
  stevefulme1.oracledb.oracledb_parameter:
    name: open_cursors
    value: "500"
    scope: both
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba

- name: Reset a parameter to default
  stevefulme1.oracledb.oracledb_parameter:
    name: open_cursors
    state: absent
    scope: spfile
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba
"""

RETURN = r"""
parameter:
  description: Name of the parameter affected.
  type: str
  returned: always
  sample: open_cursors
previous_value:
  description: Previous value of the parameter.
  type: str
  returned: when changed
  sample: "300"
sql:
  description: SQL statement executed.
  type: str
  returned: changed
  sample: "ALTER SYSTEM SET open_cursors = 500 SCOPE=BOTH"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.oracledb.plugins.module_utils.oracledb_client import (
    OracleDBClient,
    oracledb_argument_spec,
)


def get_parameter(client, name):
    """Fetch parameter from V$PARAMETER."""
    row = client.fetchone(
        "SELECT name, value, isdefault, issys_modifiable "
        "FROM v$parameter WHERE name = :1",
        [name.lower()],
    )
    if row:
        return {
            "name": row[0],
            "value": row[1],
            "isdefault": row[2],
            "issys_modifiable": row[3],
        }
    return None


def main():
    argument_spec = oracledb_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        value=dict(type="str"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        scope=dict(
            type="str", choices=["memory", "spfile", "both"], default="both"
        ),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("oracle_service_name", "oracle_sid")],
        required_one_of=[("oracle_service_name", "oracle_sid")],
        required_if=[("state", "present", ("value",))],
        supports_check_mode=True,
    )

    client = OracleDBClient(module)
    name = module.params["name"].lower()
    state = module.params["state"]
    value = module.params.get("value")
    scope = module.params["scope"].upper()

    try:
        current = get_parameter(client, name)
        if not current:
            module.fail_json(msg="Parameter '%s' not found in V$PARAMETER." % name)

        if state == "present":
            if current["value"] == value:
                module.exit_json(changed=False, parameter=name)
                return

            sql = "ALTER SYSTEM SET %s = '%s' SCOPE=%s" % (name, value, scope)
            if not module.check_mode:
                client.execute(sql)
            module.exit_json(
                changed=True,
                parameter=name,
                previous_value=current["value"],
                sql=sql,
            )
        else:
            # state == absent -> reset
            sql = "ALTER SYSTEM RESET %s SCOPE=%s" % (name, scope)
            if not module.check_mode:
                client.execute(sql)
            module.exit_json(
                changed=True,
                parameter=name,
                previous_value=current["value"],
                sql=sql,
            )
    finally:
        client.close()


if __name__ == "__main__":
    main()
