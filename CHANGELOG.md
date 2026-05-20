# Changelog

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
