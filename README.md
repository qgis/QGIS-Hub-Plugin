# QGIS Hub Plugin - QGIS Plugin

A QGIS plugins to fetch resources from the QGIS Hub

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

[![flake8](https://img.shields.io/badge/linter-flake8-green)](https://flake8.pycqa.org/)

## Generated options

### Plugin

| Cookiecutter option              |                     Picked value                      |
| :------------------------------- | :---------------------------------------------------: |
| Plugin name                      |                    QGIS Hub Plugin                    |
| Plugin name slugified            |                    qgis_hub_plugin                    |
| Plugin name class (used in code) |                     QgisHubPlugin                     |
| Plugin category                  |                          Web                          |
| Plugin description short         |  A QGIS plugins to fetch resources from the QGIS Hub  |
| Plugin description long          |  A QGIS plugins to fetch resources from the QGIS Hub  |
| Plugin tags                      | style, model, layer, resource, 3d model, project, hub |
| Plugin icon                      |                   default_icon.png                    |
| Plugin with processing provider  |                          no                           |
| Author name                      |                     Ismail Sunni                      |
| Author organization              |                      Camptocamp                       |
| Author email                     |                 imajimatika@gmail.com                 |
| Minimum QGIS version             |                         3.28                          |
| Maximum QGIS version             |                         3.99                          |
| Git repository URL               |        https://github.com/qgis/QGIS-Hub-Plugin        |
| Git default branch               |                         main                          |
| License                          |                         GPLv3                         |
| Python linter                    |                        Flake8                         |
| CI/CD platform                   |                        GitHub                         |
| IDE                              |                        VSCode                         |

### Tooling

This project is configured with the following tools:

- [Black](https://black.readthedocs.io/en/stable/) to format the code without any existential question
- [iSort](https://pycqa.github.io/isort/) to sort the Python imports

Code rules are enforced with [pre-commit](https://pre-commit.com/) hooks.
Static code analisis is based on: Flake8

See also: [contribution guidelines](CONTRIBUTING.md).

## CI/CD

Plugin is linted, tested, packaged and published with GitHub.

If you mean to deploy it to the [official QGIS plugins repository](https://plugins.qgis.org/), remember to set your OSGeo credentials (`OSGEO_USER_NAME` and `OSGEO_USER_PASSWORD`) as environment variables in your CI/CD tool.

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
