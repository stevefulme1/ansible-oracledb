#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: oracledb_dataguard_info
short_description: Gather Oracle Data Guard status information
description:
  - Query V$DATABASE, V$DATAGUARD_STATS, and V$ARCHIVE_DEST_STATUS for Data Guard metadata.
  - Returns database role, protection mode, transport and apply lag.
version_added: "0.1.0"
author:
  - Steve Fulmer (@stevefulme1)
extends_documentation_fragment:
  - stevefulme1.oracledb.oracledb
"""

EXAMPLES = r"""
- name: Get Data Guard status
  stevefulme1.oracledb.oracledb_dataguard_info:
    oracle_user: sys
    oracle_password: "{{ oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba
  register: dg_info

- name: Check if database is a standby
  ansible.builtin.debug:
    msg: "Database is standby"
  when: dg_info.database.database_role == 'PHYSICAL STANDBY'
"""

RETURN = r"""
database:
  description: Database-level Data Guard information from V$DATABASE.
  type: dict
  returned: always
  contains:
    name:
      description: Database name.
      type: str
    db_unique_name:
      description: Unique database name.
      type: str
    database_role:
      description: Database role (PRIMARY, PHYSICAL STANDBY, etc.).
      type: str
    protection_mode:
      description: Data protection mode.
      type: str
    protection_level:
      description: Current protection level.
      type: str
    switchover_status:
      description: Switchover readiness status.
      type: str
    force_logging:
      description: Whether force logging is enabled.
      type: str
  sample:
    name: ORCL
    db_unique_name: ORCL
    database_role: PRIMARY
    protection_mode: MAXIMUM PERFORMANCE
    protection_level: MAXIMUM PERFORMANCE
    switchover_status: TO STANDBY
    force_logging: "YES"
dataguard_stats:
  description: Data Guard statistics from V$DATAGUARD_STATS.
  type: list
  elements: dict
  returned: always
  contains:
    source_dbid:
      description: Source database ID.
      type: int
    name:
      description: Statistic name.
      type: str
    value:
      description: Statistic value.
      type: str
    time_computed:
      description: When the statistic was computed.
      type: str
  sample:
    - name: transport lag
      value: "+00 00:00:00"
      time_computed: "05/20/2026 12:00:00"
archive_dest_status:
  description: Archive destination status from V$ARCHIVE_DEST_STATUS.
  type: list
  elements: dict
  returned: always
  contains:
    dest_id:
      description: Destination ID.
      type: int
    dest_name:
      description: Destination name.
      type: str
    status:
      description: Destination status.
      type: str
    type:
      description: Destination type.
      type: str
    database_mode:
      description: Database mode at destination.
      type: str
    gap_status:
      description: Gap status.
      type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.oracledb.plugins.module_utils.oracledb_client import (
    OracleDBClient,
    oracledb_argument_spec,
)


def main():
    argument_spec = oracledb_argument_spec()

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[("oracle_service_name", "oracle_sid")],
        required_one_of=[("oracle_service_name", "oracle_sid")],
        supports_check_mode=True,
    )

    client = OracleDBClient(module)

    try:
        # V$DATABASE
        db_row = client.fetchone(
            "SELECT name, db_unique_name, database_role, protection_mode, "
            "protection_level, switchover_status, force_logging "
            "FROM v$database"
        )
        database = {}
        if db_row:
            database = {
                "name": db_row[0],
                "db_unique_name": db_row[1],
                "database_role": db_row[2],
                "protection_mode": db_row[3],
                "protection_level": db_row[4],
                "switchover_status": db_row[5],
                "force_logging": db_row[6],
            }

        # V$DATAGUARD_STATS
        dg_rows = client.fetchall(
            "SELECT source_dbid, name, value, "
            "TO_CHAR(time_computed, 'MM/DD/YYYY HH24:MI:SS') "
            "FROM v$dataguard_stats"
        )
        dg_stats = [
            {
                "source_dbid": r[0],
                "name": r[1],
                "value": r[2],
                "time_computed": r[3],
            }
            for r in dg_rows
        ]

        # V$ARCHIVE_DEST_STATUS
        ad_rows = client.fetchall(
            "SELECT dest_id, dest_name, status, type, "
            "database_mode, gap_status "
            "FROM v$archive_dest_status "
            "WHERE status != 'INACTIVE'"
        )
        archive_dests = [
            {
                "dest_id": r[0],
                "dest_name": r[1],
                "status": r[2],
                "type": r[3],
                "database_mode": r[4],
                "gap_status": r[5],
            }
            for r in ad_rows
        ]

        module.exit_json(
            changed=False,
            database=database,
            dataguard_stats=dg_stats,
            archive_dest_status=archive_dests,
        )
    finally:
        client.close()


if __name__ == "__main__":
    main()
