# CHANGELOG

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

<!--

Unreleased

## version_tag - YYYY-DD-mm

### Added

### Changed

### Removed

-->

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
