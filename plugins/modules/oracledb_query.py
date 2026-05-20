#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: oracledb_query
short_description: Execute arbitrary SQL against Oracle database
description:
  - Execute SQL queries or DML/DDL statements against an Oracle database.
  - Returns query results for SELECT statements.
  - Reports rows affected for DML statements.
  - This is an action module for ad-hoc SQL execution.
version_added: "0.1.0"
author:
  - Steve Fulmer (@stevefulme1)
options:
  query:
    description:
      - SQL statement to execute.
      - For multiple statements, use a list.
    type: raw
    required: true
  params:
    description:
      - Bind parameters for the query.
      - Can be a list for positional binds or dict for named binds.
    type: raw
  autocommit:
    description:
      - Whether to automatically commit after DML statements.
    type: bool
    default: true
extends_documentation_fragment:
  - stevefulme1.oracledb.oracledb
"""

EXAMPLES = r"""
- name: Run a SELECT query
  stevefulme1.oracledb.oracledb_query:
    query: "SELECT username, account_status FROM dba_users WHERE username = :1"
    params:
      - APP_USER
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba
  register: result

- name: Run multiple statements
  stevefulme1.oracledb.oracledb_query:
    query:
      - "INSERT INTO audit_log (message) VALUES (:1)"
      - "UPDATE counters SET val = val + 1 WHERE name = :1"
    params:
      - audit_entry
    oracle_user: app_user
    oracle_password: "{{ app_password }}"
    oracle_service_name: ORCL

- name: Run DDL
  stevefulme1.oracledb.oracledb_query:
    query: "CREATE INDEX idx_users_email ON users(email)"
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba
"""

RETURN = r"""
results:
  description: Query results for SELECT statements.
  type: list
  elements: dict
  returned: when query is a SELECT
  sample:
    - username: APP_USER
      account_status: OPEN
columns:
  description: Column names from the query result.
  type: list
  elements: str
  returned: when query is a SELECT
  sample: ["username", "account_status"]
rowcount:
  description: Number of rows affected by DML statements.
  type: int
  returned: when query is DML
  sample: 1
query_count:
  description: Number of queries executed.
  type: int
  returned: always
  sample: 1
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.oracledb.plugins.module_utils.oracledb_client import (
    OracleDBClient,
    oracledb_argument_spec,
)


def main():
    argument_spec = oracledb_argument_spec()
    argument_spec.update(
        query=dict(type="raw", required=True),
        params=dict(type="raw"),
        autocommit=dict(type="bool", default=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("oracle_service_name", "oracle_sid")],
        required_one_of=[("oracle_service_name", "oracle_sid")],
        supports_check_mode=True,
    )

    client = OracleDBClient(module)
    query = module.params["query"]
    params = module.params.get("params")
    autocommit = module.params["autocommit"]

    # Normalize to list of queries
    if isinstance(query, str):
        queries = [query]
    elif isinstance(query, list):
        queries = query
    else:
        module.fail_json(msg="query must be a string or list of strings.")

    try:
        result = dict(query_count=len(queries))
        total_rowcount = 0

        for sql in queries:
            sql_stripped = sql.strip().rstrip(";")

            if module.check_mode:
                result["changed"] = True
                module.exit_json(**result)
                return

            cursor = client.execute(sql_stripped, params)

            if cursor.description:
                # SELECT query
                columns = [col[0].lower() for col in cursor.description]
                rows = cursor.fetchall()
                result["columns"] = columns
                result["results"] = [dict(zip(columns, row)) for row in rows]
                result["changed"] = False
            else:
                # DML/DDL
                total_rowcount += cursor.rowcount
                result["changed"] = True

        if total_rowcount > 0:
            result["rowcount"] = total_rowcount

        if autocommit and result.get("changed", False):
            client.commit()

        module.exit_json(**result)
    finally:
        client.close()


if __name__ == "__main__":
    main()
