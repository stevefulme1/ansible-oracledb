# Changelog

## [0.2.0] - 2026-05-20

### Added
- `oracledb_tablespace` module -- create, alter, drop Oracle tablespaces via SQL DDL
- `oracledb_tablespace_info` module -- gather tablespace info from DBA_TABLESPACES and DBA_DATA_FILES
- `oracledb_user` module -- create, alter, drop users with role management via DBA_USERS
- `oracledb_user_info` module -- gather user info from DBA_USERS and DBA_ROLE_PRIVS
- `oracledb_role` module -- create, drop roles with system privilege grants via DBA_ROLES
- `oracledb_role_info` module -- gather role info from DBA_ROLES, DBA_SYS_PRIVS, DBA_ROLE_PRIVS
- `oracledb_pdb` module -- create, open, close, drop pluggable databases via V$PDBS
- `oracledb_pdb_info` module -- gather PDB info from V$PDBS and CDB_PDBS
- `oracledb_parameter` module -- set/reset init parameters via ALTER SYSTEM and V$PARAMETER
- `oracledb_parameter_info` module -- gather parameter info from V$PARAMETER
- `oracledb_dataguard_info` module -- Data Guard status from V$DATABASE, V$DATAGUARD_STATS, V$ARCHIVE_DEST_STATUS
- `oracledb_rman_backup` module -- RMAN backups (full, incremental, archivelog, spfile, controlfile)
- `oracledb_query` module -- execute arbitrary SQL (SELECT, DML, DDL)
- `oracledb_client` module_utils -- python-oracledb connection wrapper with SID/service_name, thick/thin mode
- `oracledb` doc_fragment -- shared Oracle connection parameters for all modules

## [0.1.0] - 2026-05-20

### Removed
- Deleted 56 fabricated modules that used fake REST API endpoints instead of real oracledb SQL operations
- Deleted fabricated api_client.py module_utils (generic REST wrapper)
- Deleted fabricated oracledb_inventory dynamic inventory plugin
- Deleted fabricated EDA event source plugins (aq_consumer, oci_events, oem_webhook)
- Deleted associated unit tests for removed modules

### Retained
- 10 placeholder roles for common Oracle Database operational workflows
- Collection scaffolding (LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, MAINTAINERS)
- CI/CD workflow configuration

### Notes
- Version reset to 0.1.0 to reflect pre-release status
- Future modules will use oracledb (python-oracledb) for SQL/PL-SQL operations
