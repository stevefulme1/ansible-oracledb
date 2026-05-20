#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: oracledb_parameter_info
short_description: Gather Oracle database parameter information
description:
  - Query V$PARAMETER for initialization parameter metadata.
  - Returns current values, defaults, and modifiability.
version_added: "0.1.0"
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of a specific parameter to query.
      - If omitted, all parameters are returned.
    type: str
  modified_only:
    description:
      - Only return parameters that have been modified from defaults.
    type: bool
    default: false
extends_documentation_fragment:
  - stevefulme1.oracledb.oracledb
"""

EXAMPLES = r"""
- name: Get all parameters
  stevefulme1.oracledb.oracledb_parameter_info:
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba

- name: Get only modified parameters
  stevefulme1.oracledb.oracledb_parameter_info:
    modified_only: true
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba

- name: Get a specific parameter
  stevefulme1.oracledb.oracledb_parameter_info:
    name: open_cursors
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba
"""

RETURN = r"""
parameters:
  description: List of parameter details.
  type: list
  elements: dict
  returned: always
  contains:
    name:
      description: Parameter name.
      type: str
    value:
      description: Current value.
      type: str
    isdefault:
      description: Whether the value is the default.
      type: str
    issys_modifiable:
      description: Whether parameter can be changed with ALTER SYSTEM.
      type: str
    description:
      description: Parameter description.
      type: str
  sample:
    - name: open_cursors
      value: "300"
      isdefault: "TRUE"
      issys_modifiable: IMMEDIATE
      description: "max # of open cursors per session"
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
        modified_only=dict(type="bool", default=False),
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
            "SELECT name, value, isdefault, issys_modifiable, description "
            "FROM v$parameter"
        )
        conditions = []
        params = []

        if module.params["name"]:
            conditions.append("name = :1")
            params.append(module.params["name"].lower())

        if module.params["modified_only"]:
            conditions.append("isdefault = 'FALSE'")

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        sql += " ORDER BY name"

        rows = client.fetchall(sql, params if params else None)

        parameters = []
        for row in rows:
            parameters.append(
                {
                    "name": row[0],
                    "value": row[1],
                    "isdefault": row[2],
                    "issys_modifiable": row[3],
                    "description": row[4],
                }
            )

        module.exit_json(changed=False, parameters=parameters)
    finally:
        client.close()


if __name__ == "__main__":
    main()
