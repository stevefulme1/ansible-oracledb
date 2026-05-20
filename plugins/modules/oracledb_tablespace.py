#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: oracledb_tablespace
short_description: Manage Oracle tablespaces
description:
  - Create, alter, or drop Oracle tablespaces.
  - Supports permanent, temporary, and undo tablespace types.
  - Uses SQL DDL via python-oracledb driver.
version_added: "0.1.0"
author:
  - Steve Fulmer (@stevefulme1)
options:
  name:
    description:
      - Name of the tablespace.
    type: str
    required: true
  state:
    description:
      - Desired state of the tablespace.
    type: str
    choices: [present, absent]
    default: present
  tablespace_type:
    description:
      - Type of tablespace to create.
    type: str
    choices: [permanent, temporary, undo]
    default: permanent
  datafile:
    description:
      - Path for the datafile (or tempfile for temporary tablespaces).
      - Required when creating a new tablespace.
    type: str
  size:
    description:
      - Initial size of the datafile (for example V(100M), V(1G)).
    type: str
    default: 100M
  autoextend:
    description:
      - Enable autoextend on the datafile.
    type: bool
    default: true
  max_size:
    description:
      - Maximum size for autoextend (for example V(unlimited), V(10G)).
    type: str
    default: unlimited
  bigfile:
    description:
      - Create a bigfile tablespace.
    type: bool
    default: false
  online:
    description:
      - Whether the tablespace should be online.
      - Only applicable for existing tablespaces.
    type: bool
extends_documentation_fragment:
  - stevefulme1.oracledb.oracledb
"""

EXAMPLES = r"""
- name: Create a tablespace
  stevefulme1.oracledb.oracledb_tablespace:
    name: app_data
    datafile: /u01/oradata/ORCL/app_data01.dbf
    size: 500M
    autoextend: true
    max_size: 10G
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba

- name: Create a temporary tablespace
  stevefulme1.oracledb.oracledb_tablespace:
    name: app_temp
    tablespace_type: temporary
    datafile: /u01/oradata/ORCL/app_temp01.dbf
    size: 200M
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba

- name: Drop a tablespace
  stevefulme1.oracledb.oracledb_tablespace:
    name: app_data
    state: absent
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba
"""

RETURN = r"""
tablespace:
  description: Name of the tablespace affected.
  type: str
  returned: always
  sample: APP_DATA
sql:
  description: SQL statement(s) executed.
  type: list
  elements: str
  returned: changed
  sample: ["CREATE TABLESPACE app_data DATAFILE '/u01/oradata/ORCL/app_data01.dbf' SIZE 500M AUTOEXTEND ON MAXSIZE 10G"]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.oracledb.plugins.module_utils.oracledb_client import (
    OracleDBClient,
    oracledb_argument_spec,
)


def get_tablespace(client, name):
    """Fetch tablespace info from DBA_TABLESPACES."""
    row = client.fetchone(
        "SELECT tablespace_name, status, contents, bigfile "
        "FROM dba_tablespaces WHERE tablespace_name = :1",
        [name.upper()],
    )
    if row:
        return {
            "name": row[0],
            "status": row[1],
            "contents": row[2],
            "bigfile": row[3],
        }
    return None


def create_tablespace(module, client):
    """Create a tablespace."""
    name = module.params["name"].upper()
    ts_type = module.params["tablespace_type"]
    datafile = module.params["datafile"]
    size = module.params["size"]
    autoextend = module.params["autoextend"]
    max_size = module.params["max_size"]
    bigfile = module.params["bigfile"]

    if not datafile:
        module.fail_json(msg="datafile is required when creating a tablespace.")

    sql_parts = []

    if bigfile:
        sql_parts.append("CREATE BIGFILE")
    else:
        sql_parts.append("CREATE")

    if ts_type == "temporary":
        sql_parts.append("TEMPORARY TABLESPACE %s" % name)
        sql_parts.append("TEMPFILE '%s' SIZE %s" % (datafile, size))
    elif ts_type == "undo":
        sql_parts.append("UNDO TABLESPACE %s" % name)
        sql_parts.append("DATAFILE '%s' SIZE %s" % (datafile, size))
    else:
        sql_parts.append("TABLESPACE %s" % name)
        sql_parts.append("DATAFILE '%s' SIZE %s" % (datafile, size))

    if autoextend:
        sql_parts.append("AUTOEXTEND ON MAXSIZE %s" % max_size)

    sql = " ".join(sql_parts)
    executed = [sql]

    if not module.check_mode:
        client.execute(sql)

    return executed


def drop_tablespace(module, client, name):
    """Drop a tablespace."""
    sql = "DROP TABLESPACE %s INCLUDING CONTENTS AND DATAFILES" % name.upper()
    if not module.check_mode:
        client.execute(sql)
    return [sql]


def main():
    argument_spec = oracledb_argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        tablespace_type=dict(
            type="str",
            choices=["permanent", "temporary", "undo"],
            default="permanent",
        ),
        datafile=dict(type="str"),
        size=dict(type="str", default="100M"),
        autoextend=dict(type="bool", default=True),
        max_size=dict(type="str", default="unlimited"),
        bigfile=dict(type="bool", default=False),
        online=dict(type="bool"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("oracle_service_name", "oracle_sid")],
        required_one_of=[("oracle_service_name", "oracle_sid")],
        supports_check_mode=True,
    )

    client = OracleDBClient(module)
    name = module.params["name"]
    state = module.params["state"]

    try:
        current = get_tablespace(client, name)

        if state == "present":
            if current:
                changed = False
                executed = []
                # Handle online/offline toggle
                if module.params["online"] is not None:
                    want_online = module.params["online"]
                    is_online = current["status"] == "ONLINE"
                    if want_online and not is_online:
                        sql = "ALTER TABLESPACE %s ONLINE" % name.upper()
                        if not module.check_mode:
                            client.execute(sql)
                        executed.append(sql)
                        changed = True
                    elif not want_online and is_online:
                        sql = "ALTER TABLESPACE %s OFFLINE" % name.upper()
                        if not module.check_mode:
                            client.execute(sql)
                        executed.append(sql)
                        changed = True
                result = dict(
                    changed=changed,
                    tablespace=name.upper(),
                )
                if executed:
                    result["sql"] = executed
                module.exit_json(**result)
            else:
                executed = create_tablespace(module, client)
                module.exit_json(
                    changed=True,
                    tablespace=name.upper(),
                    sql=executed,
                )
        elif state == "absent":
            if current:
                executed = drop_tablespace(module, client, name)
                module.exit_json(
                    changed=True,
                    tablespace=name.upper(),
                    sql=executed,
                )
            else:
                module.exit_json(changed=False, tablespace=name.upper())
    finally:
        client.close()


if __name__ == "__main__":
    main()
