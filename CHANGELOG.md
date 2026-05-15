# CHANGELOG

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

<!--

Unreleased

## version_tag - YYYY-DD-mm

### Added

### Changed

### Removed

-->

## 0.6.0 - 2026-05-15

### Added

- Added support for QGIS 4 / Qt6 alongside existing QGIS 3 / Qt5 support
  (`supportsQt6=True`, `qgisMaximumVersion=4.99`)
- Added Pillow-based webp thumbnail fallback for Qt6 (Qt6 in QGIS 4 does
  not ship the webp image-format plugin); Pillow is an optional
  dependency
- Added "Clear cache" button in the plugin settings to wipe the cached
  resource list and downloaded thumbnails
- Added thumbnail download progress bar in the QGIS message bar during
  initial resource browser population
- Added uniform square-canvas icon rendering so list-view cells are the
  same size regardless of thumbnail aspect ratio
- Added clearer error message when adding a PyQt5-only processing script
  on Qt6 (instead of an opaque traceback)
- Added Qt6 / QGIS 4 integration test job to CI (`qgis/qgis:4.0`)
  alongside the existing Qt5 LTR job
- Added tests for the Qt6 webp fallback, cache helpers, `clear_cache`,
  and `ResourceItem._make_uniform_icon`
- Added Qt6 / QGIS 4 migration documentation under the contribution
  guide

### Changed

- Migrated all Qt enum usage to the fully-scoped form
  (`Qt.ItemDataRole.UserRole`, `QSizePolicy.Policy.Minimum`,
  `QNetworkReply.NetworkError.NoError`, etc.) so the codebase works on
  both PyQt5 and PyQt6
- Replaced `QRegExp` with `QRegularExpression` in filter proxy and
  resource browser (Qt6 dropped `QRegExp`)
- Bumped pre-commit `black` to 25.1.0 and `pyupgrade` to 3.21.2 for
  Python 3.14 compatibility

### Fixed

- Fixed `tr()` + f-string usage in new error branches; translations are
  now extractable by `pylupdate` via `tr("...").format(...)`
- Fixed `clear_cache` to count files recursively (`rglob`) so nested
  thumbnail files are reflected in the returned count
- Fixed `is_resource_thumbnail_cached` to accept the converted `.png`
  sibling as a cache hit when Qt cannot decode the original format
- Fixed re-entrancy risk in `populate_resources` by throttling
  `QgsApplication.processEvents()` to every 10 items plus a final flush
- Fixed list-view thumbnail-size slider on Qt6 by also updating
  `setGridSize` in `update_icon_size`

## 0.5.0 - 2025-12-25

### Added

- Added screenshot resource type support
- Added comprehensive test suite with mock API responses
- Added GUI behavior tests for resource browser
- Added tests for resource tree filtering, preview, and download functionality
- Added comprehensive tests for multiple subtypes support
- Set up development environment with virtual environment

### Changed

- Improved error handling for invalid QGIS Hub API responses
- Made resource URL clickable in API error messages
- Implemented support for multiple subtypes in API response handling
- Refactored normalize_resource_subtypes helper to reduce code duplication
- Save processing scripts in default folder and keep file on load error
- Configured CI/CD to run QGIS integration tests in Docker container
- Simplified test structure: moved all QGIS-dependent tests to tests/qgis/
- Enabled unit tests to run without QGIS via conditional imports

### Fixed

- Fixed datetime parsing for Python < 3.11 compatibility
- Fixed file dialog from appearing during download tests
- Fixed unit tests: Use real QIcon objects instead of MagicMock
- Fixed integration tests and added comprehensive testing documentation

## 0.4.1 - 2025-12-25

### Fixed

- Fixed bug when adding processing scripts to QGIS

## 0.4.0 - 2025-05-22

### Added

- Added support for 'Map' and 'Processing Scripts' resource type
- Implemented dynamic resource type handling for future-proof compatibility
- Added resource subtype filtering with tree hierarchy view
- Added model dependencies display in preview panel
- Added close button to resource preview window

### Changed

- Renamed resource type labels to match QGIS Hub Website
- Enhanced UI with improved spacing and layout
- Improved preview panel layout with consistent form spacing
- Made icon size slider visible only in icon view mode
- Optimized resource type tree display for better readability

## 0.3.0 - 2025-02-12

- Update the new resource hub API URL

## 0.2.0 - 2024-11-07

- Limit the name to be maximum 50 character
- Add support for 3D model and QGIS Layer Definition
- Add "add to QGIS" for layer definition
- Fix bug when resource give 404

## 0.1.2 - 2023-11-01

- Fix bug #85: failed to handle null thumbnail

## 0.1.1 - 2023-08-23

- Fix UI issue on HiDPI screen
- Release as non experimental

## 0.1.0 - 2023-04-20

- First release
- Generated with the [QGIS Plugins templater](https://oslandia.gitlab.io/qgis/template-qgis-plugin/)
