# stevefulme1.oracledb

Ansible Collection for Oracle Database -- tablespaces, users, Data Guard, RMAN, RAC, PDB/CDB, audit, TDE, and EDA via OEM webhooks and Oracle AQ.

## Overview

This collection provides **57 modules** for automating Oracle Database infrastructure, along with 10 operational roles, a dynamic inventory plugin, and CI/CD workflows.

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
ansible-galaxy collection install stevefulme1-oracledb-2.0.0.tar.gz
```

## Included Content

### Modules (57)

CRUD and info modules covering:

- **Tablespaces** -- create, resize, drop, autoextend
- **Users** -- create, alter, drop, grant privileges
- **Data Guard** -- primary/standby configuration, switchover, failover
- **RMAN** -- backup, restore, recovery catalog
- **RAC** -- cluster management, services, instances
- **PDB/CDB** -- pluggable database lifecycle
- **Audit** -- unified audit policies, audit trail
- **TDE** -- transparent data encryption, key management
- **Monitoring** -- AWR, ASH, alert log parsing

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

### Inventory Plugin

- `oracledb_inventory` -- Dynamic inventory from Oracle databases

## Usage

```yaml
- name: Create a tablespace
  stevefulme1.oracledb.oracledb_tablespace:
    host: "{{ oracle_host }}"
    username: "{{ oracle_user }}"
    password: "{{ oracle_pass }}"
    service_name: "{{ oracle_service }}"
    name: APP_DATA
    size: 500M
    autoextend: true
    state: present
```

## License

Apache-2.0
