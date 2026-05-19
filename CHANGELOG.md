# Changelog

## [2.1.1] - 2026-05-18

### Security
- Prevent credential leak in API request bodies — connection params (host, username, password, api_key, validate_certs) are now stripped before create/update payloads are sent to the remote API
- Add timeout=30 to all HTTP methods to prevent indefinite hangs
- Harden .gitignore to exclude secrets, credentials, and IDE artifacts

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
