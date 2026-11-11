# QGIS Hub Plugin - QGIS Plugin

A QGIS plugins to fetch resources from the QGIS Hub

[Resource Browser](./docs/images/resource_browser.png)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

[![flake8](https://img.shields.io/badge/linter-flake8-green)](https://flake8.pycqa.org/)

### Tooling

This project is configured with the following tools:

- [Black](https://black.readthedocs.io/en/stable/) to format the code without any existential question
- [iSort](https://pycqa.github.io/isort/) to sort the Python imports

Code rules are enforced with [pre-commit](https://pre-commit.com/) hooks.
Static code analisis is based on: Flake8

See also: [contribution guidelines](CONTRIBUTING.md).

## CI/CD

Plugin is linted, tested, packaged and published with GitHub Actions.

The Linter workflow runs [Bandit](https://bandit.readthedocs.io/) and the Qt6 test job runs QGIS's
`pyqt5_to_pyqt6.py` check: the same scans the [QGIS plugins repository](https://plugins.qgis.org/)
runs on upload, where any finding blocks the version.

### Releasing

Pushing a tag triggers the Releaser workflow, which uses [qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci/) to
create the GitHub release with the plugin zip and `plugins.xml`, and to upload the zip to the QGIS plugins repository
(with the `QGIS_PLUGIN_TOKEN` repository secret, a token from the plugin's page on plugins.qgis.org).

1. Open a PR adding the new version to `CHANGELOG.md`, and merge it into `main`:

   ```markdown
   ## X.Y.Z - YYYY-MM-DD

   Added:

   - ...

   Fixed:

   - ...
   ```

   Use plain `Added:` / `Changed:` / `Fixed:` labels, not `###` headings: qgis-plugin-ci ends a version's notes at the
   next `##`, which would leave the release notes and the plugin manager changelog empty.
   No need to edit the version in `metadata.txt`, it is set from the tag.

1. Make sure CI passes on `main`, then tag and push:

   ```sh
   git checkout main && git pull
   git tag -a X.Y.Z -m "Version X.Y.Z"
   git push origin X.Y.Z
   ```

1. Check the Releaser run, the [GitHub release](https://github.com/qgis/QGIS-Hub-Plugin/releases), and the security
   scan of the new version on [plugins.qgis.org](https://plugins.qgis.org/plugins/qgis_hub_plugin/).

Do not create the GitHub release by hand before pushing the tag: the workflow then fails because the release already exists.
A version number can only be uploaded once to plugins.qgis.org, so a blocked or broken upload needs a new patch version.

To check the changelog or build the zip locally:

```sh
python -m pip install -U -r requirements/packaging.txt
qgis-plugin-ci changelog X.Y.Z
qgis-plugin-ci package X.Y.Z --allow-uncommitted-changes
```

### Documentation

The documentation is generated using Sphinx and is automatically generated through the CI and published on Pages.

- homepage: <https://github.com/qgis/QGIS-Hub-Plugin>
- repository: <https://github.com/qgis/QGIS-Hub-Plugin>
- tracker: <https://github.com/qgis/QGIS-Hub-Plugin/issues>

---

## Next steps

### Set up development environment

> Typical commands on Linux (Ubuntu).

1. If you don't pick the `git init` option, initialize your local repository:

   ```sh
   git init
   ```

1. Follow the [embedded documentation to set up your development environment](./docs/development/environment.md)
1. Add all files to git index to prepare initial commit:

   ```sh
   git add -A
   ```

1. Run the git hooks to ensure that everything runs OK and to start developing on quality standards:

   ```sh
   pre-commit run
   ```

### Try to build documentation locally

1. Have a look to the [plugin's metadata.txt file](qgis_hub_plugin/metadata.txt): review it, complete it or fix it if needed (URLs, etc.).
1. Follow the [embedded documentation to build plugin documentation locally](./docs/development/environment.md)

---

## License

Distributed under the terms of the [`GPLv3` license](LICENSE).
