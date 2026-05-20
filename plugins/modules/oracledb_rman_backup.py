#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: oracledb_rman_backup
short_description: Run Oracle RMAN backups
description:
  - Execute RMAN backup commands via the rman command-line utility.
  - Supports full database, incremental, and archivelog backups.
version_added: "0.1.0"
author:
  - Steve Fulmer (@stevefulme1)
options:
  backup_type:
    description:
      - Type of RMAN backup to perform.
      - V(full) performs a full database backup.
      - V(incremental_0) performs a level 0 incremental backup.
      - V(incremental_1) performs a level 1 incremental backup.
      - V(archivelog) backs up archive logs.
      - V(spfile) backs up the SPFILE.
      - V(controlfile) backs up the control file.
    type: str
    choices: [full, incremental_0, incremental_1, archivelog, spfile, controlfile]
    default: full
  tag:
    description:
      - Tag for the backup set.
    type: str
  compressed:
    description:
      - Use compression for the backup.
    type: bool
    default: false
  format:
    description:
      - Custom format string for backup pieces.
      - Uses RMAN format specifiers like C<%d>, C<%T>, C<%U>.
    type: str
  oracle_home:
    description:
      - Path to ORACLE_HOME.
      - Required to locate the rman binary.
    type: str
    required: true
  oracle_sid_env:
    description:
      - ORACLE_SID environment variable for rman connection.
    type: str
    required: true
  catalog_connect:
    description:
      - RMAN catalog connection string.
      - If omitted, uses NOCATALOG.
    type: str
  rman_script:
    description:
      - Custom RMAN script to execute instead of the auto-generated command.
      - When specified, O(backup_type) and other backup options are ignored.
    type: str
"""

EXAMPLES = r"""
- name: Full database backup
  stevefulme1.oracledb.oracledb_rman_backup:
    backup_type: full
    tag: daily_full
    compressed: true
    oracle_home: /u01/app/oracle/product/19.3.0/dbhome_1
    oracle_sid_env: ORCL

- name: Incremental level 1 backup
  stevefulme1.oracledb.oracledb_rman_backup:
    backup_type: incremental_1
    tag: incr_level1
    oracle_home: /u01/app/oracle/product/19.3.0/dbhome_1
    oracle_sid_env: ORCL

- name: Archive log backup
  stevefulme1.oracledb.oracledb_rman_backup:
    backup_type: archivelog
    tag: archlog_backup
    oracle_home: /u01/app/oracle/product/19.3.0/dbhome_1
    oracle_sid_env: ORCL

- name: Custom RMAN script
  stevefulme1.oracledb.oracledb_rman_backup:
    rman_script: |
      BACKUP AS COMPRESSED BACKUPSET DATABASE PLUS ARCHIVELOG;
      DELETE NOPROMPT OBSOLETE;
    oracle_home: /u01/app/oracle/product/19.3.0/dbhome_1
    oracle_sid_env: ORCL
"""

RETURN = r"""
rman_command:
  description: The RMAN command that was executed.
  type: str
  returned: always
  sample: "BACKUP AS COMPRESSED BACKUPSET FULL TAG 'daily_full' DATABASE;"
stdout:
  description: Standard output from the RMAN command.
  type: str
  returned: always
stderr:
  description: Standard error from the RMAN command.
  type: str
  returned: always
rc:
  description: Return code from the RMAN command.
  type: int
  returned: always
  sample: 0
"""

import os

from ansible.module_utils.basic import AnsibleModule


def build_rman_command(module):
    """Build the RMAN backup command string."""
    backup_type = module.params["backup_type"]
    tag = module.params["tag"]
    compressed = module.params["compressed"]
    fmt = module.params.get("format")

    parts = ["BACKUP"]

    if compressed:
        parts.append("AS COMPRESSED BACKUPSET")

    if backup_type == "full":
        parts.append("FULL")
    elif backup_type == "incremental_0":
        parts.append("INCREMENTAL LEVEL 0")
    elif backup_type == "incremental_1":
        parts.append("INCREMENTAL LEVEL 1")

    if tag:
        parts.append("TAG '%s'" % tag)

    if fmt:
        parts.append("FORMAT '%s'" % fmt)

    if backup_type in ("full", "incremental_0", "incremental_1"):
        parts.append("DATABASE;")
    elif backup_type == "archivelog":
        parts.append("ARCHIVELOG ALL;")
    elif backup_type == "spfile":
        parts.append("SPFILE;")
    elif backup_type == "controlfile":
        parts.append("CURRENT CONTROLFILE;")

    return " ".join(parts)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            backup_type=dict(
                type="str",
                choices=[
                    "full",
                    "incremental_0",
                    "incremental_1",
                    "archivelog",
                    "spfile",
                    "controlfile",
                ],
                default="full",
            ),
            tag=dict(type="str"),
            compressed=dict(type="bool", default=False),
            format=dict(type="str"),
            oracle_home=dict(type="str", required=True),
            oracle_sid_env=dict(type="str", required=True),
            catalog_connect=dict(type="str"),
            rman_script=dict(type="str"),
        ),
        supports_check_mode=True,
    )

    oracle_home = module.params["oracle_home"]
    oracle_sid = module.params["oracle_sid_env"]
    catalog_connect = module.params.get("catalog_connect")
    rman_script = module.params.get("rman_script")

    rman_bin = os.path.join(oracle_home, "bin", "rman")

    if rman_script:
        rman_cmd = rman_script.strip()
    else:
        rman_cmd = build_rman_command(module)

    if module.check_mode:
        module.exit_json(changed=True, rman_command=rman_cmd, stdout="", stderr="", rc=0)
        return

    # Build rman CLI command
    target = "/"
    connect_args = "TARGET %s" % target
    if catalog_connect:
        connect_args += " CATALOG %s" % catalog_connect
    else:
        connect_args += " NOCATALOG"

    # Write RMAN script to temp file
    import tempfile

    script_content = "RUN {\n%s\n}\n" % rman_cmd
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".rman", delete=False
    ) as tmp:
        tmp.write(script_content)
        script_path = tmp.name

    try:
        env = os.environ.copy()
        env["ORACLE_HOME"] = oracle_home
        env["ORACLE_SID"] = oracle_sid
        env["PATH"] = os.path.join(oracle_home, "bin") + ":" + env.get("PATH", "")

        cmd = "%s %s @%s" % (rman_bin, connect_args, script_path)
        rc, stdout, stderr = module.run_command(cmd, environ_update=env)

        if rc != 0:
            module.fail_json(
                msg="RMAN backup failed with rc=%d" % rc,
                rman_command=rman_cmd,
                stdout=stdout,
                stderr=stderr,
                rc=rc,
            )

        module.exit_json(
            changed=True,
            rman_command=rman_cmd,
            stdout=stdout,
            stderr=stderr,
            rc=rc,
        )
    finally:
        try:
            os.unlink(script_path)
        except OSError:
            pass


if __name__ == "__main__":
    main()
