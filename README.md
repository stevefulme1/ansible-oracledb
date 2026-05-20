# stevefulme1.oracledb

Ansible Collection for Oracle Database -- tablespaces, users, Data Guard, RMAN, RAC, PDB/CDB, audit, and TDE.

**Status: Pre-release (0.1.0). Under active development.**

## Overview

This collection will provide modules for automating Oracle Database using real database drivers:

- **Database operations** -- via `oracledb` (python-oracledb) Python driver for SQL/PL-SQL
- **RMAN** -- via command-line RMAN interface
- **Listener** -- via `lsnrctl` command-line tool

Placeholder roles are included for common operational workflows.

## Requirements

- ansible-core >= 2.16
- Python >= 3.11

## Installation

```bash
ansible-galaxy collection install stevefulme1.oracledb
```

Or from source:

```bash
ansible-galaxy collection build
ansible-galaxy collection install stevefulme1-oracledb-0.1.0.tar.gz
```

## Included Content

### Modules

No modules yet. Modules will use:

- `oracledb` (python-oracledb, successor to cx_Oracle) for SQL/PL-SQL operations
- Command-line tools (RMAN, lsnrctl, srvctl) for infrastructure operations

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

## License

GPL-3.0-or-later

## Community

- [Contributing](CONTRIBUTING.md) - How to contribute to this project
- [Code of Conduct](CODE_OF_CONDUCT.md) - Ansible Community Code of Conduct
- [Security Policy](SECURITY.md) - How to report security vulnerabilities
