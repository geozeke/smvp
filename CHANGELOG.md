# Changelog

All notable changes to smvp are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.4.7] - 2026-07-03

[Compare with 0.4.6](https://github.com/geozeke/smvp/compare/v0.4.6...v0.4.7)


### Removed

- Remove "dev" recipe from justfile (3a3930f)

### Dependencies

- DEPS-See commit msg for list (a9776b5)
- DEPS-See commit msg for list (0d325ae)

## [0.4.6] - 2026-06-12

[Compare with 0.4.5](https://github.com/geozeke/smvp/compare/v0.4.5...v0.4.6)


### Changed

- Re-shape tooling (41b2b2f)


- Limit code coverage to just sources (64b545f)

### Dependencies

- DEPS-See commit msg for list (4ca7e9c)
- DEPS-See commit msg for list (cf5e502)

## [0.4.5] - 2026-05-24

[Compare with 0.4.4](https://github.com/geozeke/smvp/compare/v0.4.4...v0.4.5)


### Changed

- Move project out of beta status (9990b90)
- Prevent latest tagging of beta builds (5a43a35)

### Documentation

- Remove maintainer notes (282b9d6)
- Remove the downloads badge (425dd52)

## [0.4.4] - 2026-05-22

[Compare with 0.4.3](https://github.com/geozeke/smvp/compare/v0.4.3...v0.4.4)


### Changed

- Housekeeping (#55) (6f07d4b)

## [0.4.3] - 2026-05-15

[Compare with 0.4.2](https://github.com/geozeke/smvp/compare/v0.4.2...v0.4.3)


### Changed

- Streamline changelogs (420fcac)


- Standardize changelogs (ef9bb33)
- Change tagging to use proper SemVer (33eeaa4)
- Streamline dependency updates (022aa18)

### Removed

- Remove "just rebase" recipe (3156ee7)

### Documentation

- Lint README.md (dbdd0e7)
- Remove first-person voice from README (68bd710)

### Dependencies

- Dependency Upgrades (02d9587)

## [0.4.2] - 2026-05-08

[Compare with 0.4.1](https://github.com/geozeke/smvp/compare/v0.4.1...v0.4.2)


### Changed

- Improve tagging and release workflow (ecb62ab)


- Add documentation consistency check (6ebe589)
- Set default codex model to 5.5 medium (e4f6730)

### Fixed

- Fix environment leak in justfile (883d170)
- Remove duplicates from changelogs (25c0589)

### Dependencies

- Bump ruff from 0.15.11 to 0.15.12 (a05e8ef)
- Bump mypy from 1.20.2 to 2.0.0 (2fb20f4)

## [0.4.1] - 2026-04-24

[Compare with 0.4.0](https://github.com/geozeke/smvp/compare/v0.4.0...v0.4.1)


### Added

- Ensure runtime is compatible with Windows (c72d640)
- Confirm support for Python 3.14 (34b6cc0)

### Changed

- Add new tests for Path change (e02194b)


- Conduct code review (9c9c48f)
- Add AGENTS rule to avoid cache directories (f4e8962)
- Make "bug" and "fix" equivalent (8aef306)
- Remove /run directory (617108d)
- Cleanup justfile (44df59d)
- Move logo to a local asset (e321163)
- Conduct metadata audit (44dac6a)
- Add truthiness to AGENTS.md (296c91a)
- Unfreeze syncing in justfile (3f57b04)

### Fixed

- Fix runtime.yml (e38bd90)

### Dependencies

- Bump mypy from 1.20.1 to 1.20.2 (6de3b68)
- Bump lxml from 6.0.4 to 6.1.0 in the uv group across 1 directory (e89c80f)

## [0.4.0] - 2026-04-20

[View release tag](https://github.com/geozeke/smvp/releases/tag/v0.4.0)


### Added

- Selectable content type (f237877)

### Changed

- Build codex tooling (3fbac8f)
- Add snake case requirement to AGENTS.md (63f69fd)
- Modernize changelog management (195ad58)
- Remove python 3.9 from pyproject.toml (ed7b7e2)


- Implement unit tests (a2c1cf7)


- Lint .gitignore (3d40dad)
- Add .gitignore instruction to AGENTS.md (ace1b71)
- Lint justfile (150aea5)
- Lint CHANGELOG (4a03e7a)
- Lint justfile (fa596ab)
- Lint justfile (092684c)
- Add support for code coverage (f90fe33)
- Lint justfile (b20ceb0)

### Fixed

- Improve html detection (309d25d)
- Fix justfile workflow for release (60a309d)

### Documentation

- Lint README file (ca3ddfc)
- Lint argparse messages (1149a8d)
- Lint LICENSE (ba19e45)
- Lint docstrings. (727ae3a)
- Add shields.io badges (e2b7a2f)
