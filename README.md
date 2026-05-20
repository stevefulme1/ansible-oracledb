# stevefulme1.oracledb

Ansible Collection for Oracle Database -- tablespaces, users, Data Guard, RMAN, RAC, PDB/CDB, audit, and TDE.

**Status: Pre-release (0.2.0). Under active development.**

## Overview

This collection provides modules for automating Oracle Database using real database drivers:

- **Database operations** -- via `oracledb` (python-oracledb) Python driver for SQL/PL-SQL
- **RMAN** -- via command-line RMAN interface
- **Listener** -- via `lsnrctl` command-line tool

## Requirements

- ansible-core >= 2.16
- Python >= 3.11
- python-oracledb >= 2.0.0

## Installation

```bash
ansible-galaxy collection install stevefulme1.oracledb
```

Or from source:

```bash
ansible-galaxy collection build
ansible-galaxy collection install stevefulme1-oracledb-0.2.0.tar.gz
```

## Included Content

### Modules (13)

| Module | Description |
|--------|-------------|
| `oracledb_tablespace` | Create, alter, or drop tablespaces |
| `oracledb_tablespace_info` | Gather tablespace information from DBA_TABLESPACES |
| `oracledb_user` | Create, alter, or drop users with role grants |
| `oracledb_user_info` | Gather user information from DBA_USERS |
| `oracledb_role` | Create or drop roles with privilege grants |
| `oracledb_role_info` | Gather role information from DBA_ROLES |
| `oracledb_pdb` | Create, open, close, or drop pluggable databases |
| `oracledb_pdb_info` | Gather PDB information from V$PDBS |
| `oracledb_parameter` | Set or reset initialization parameters |
| `oracledb_parameter_info` | Gather parameter information from V$PARAMETER |
| `oracledb_dataguard_info` | Gather Data Guard status from V$DATABASE and V$DATAGUARD_STATS |
| `oracledb_rman_backup` | Execute RMAN backups (full, incremental, archivelog) |
| `oracledb_query` | Execute arbitrary SQL queries and DML/DDL |

### Module Utils

| Utility | Description |
|---------|-------------|
| `oracledb_client` | python-oracledb connection wrapper with SID/service_name support and thick/thin mode |

### Doc Fragments

| Fragment | Description |
|----------|-------------|
| `oracledb` | Shared Oracle connection parameters (host, port, user, password, service_name, sid, mode) |

### Roles (10)

| Role | Description |
|------|-------------|
| `oracle_dataguard_setup` | Configure Data Guard |
| `oracle_disaster_recovery` | DR procedures and failover |
| `oracle_monitoring` | Set up monitoring and alerting |
| `oracle_patching` | Oracle patching procedures |
| `oracle_pdb_lifecycle` | PDB provisioning and management |
| `oracle_rac_setup` | RAC cluster configuration |
| `oracle_rman_backup_setup` | RMAN backup configuration |
| `oracle_security_hardening` | Security baseline configuration |
| `oracle_tablespace_management` | Tablespace lifecycle management |
| `oracle_user_management` | User and privilege management |

## Connection Parameters

All database modules share common connection parameters via the `stevefulme1.oracledb.oracledb` doc fragment:

```yaml
- name: Example with service name
  stevefulme1.oracledb.oracledb_tablespace_info:
    oracle_host: dbserver.example.com
    oracle_port: 1521
    oracle_user: sys
    oracle_password: "{{ vault_oracle_password }}"
    oracle_service_name: ORCL
    oracle_mode: sysdba

- name: Example with SID
  stevefulme1.oracledb.oracledb_tablespace_info:
    oracle_host: dbserver.example.com
    oracle_user: sys
    oracle_password: "{{ vault_oracle_password }}"
    oracle_sid: ORCL
    oracle_mode: sysdba
```

## License

GPL-3.0-or-later

## Community

- [Contributing](CONTRIBUTING.md) - How to contribute to this project
- [Code of Conduct](CODE_OF_CONDUCT.md) - Ansible Community Code of Conduct
- [Security Policy](SECURITY.md) - How to report security vulnerabilities
