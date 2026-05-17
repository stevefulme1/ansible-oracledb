# Changelog

## [2.0.0] - 2026-05-17

### Added
- Idempotency: get-before-write with state comparison in 28 modules
- Pagination support (limit/offset/max_results) for all 28 info modules
- EDA event filter plugin
- Comprehensive test suites for 15 Oracle DB modules
- Pre-commit and linting configuration
- Sanity tests for ansible-core 2.16/2.17/2.18/2.20

### Fixed
- Pylint unhashable-member false positives resolved
- Stale sanity ignore files removed
- Role README files added for Galaxy compliance
- Galaxy import validation issues resolved
- CI failures resolved

## [1.2.0] - 2026-05-15

### Added
- 56 modules covering full Oracle Database platform
- 10 Day-2 operation roles
- EDA source plugins
- Dynamic inventory plugin

## [1.0.0] - 2026-05-15

### Added
- Initial release with tablespace, user, Data Guard, RMAN, RAC, PDB/CDB, audit, and TDE modules
- EDA via OEM webhooks and Oracle AQ
- Unit tests and CI pipeline
