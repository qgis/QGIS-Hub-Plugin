# Packaging and deployment

## Packaging

This plugin is using the [qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci/) tool to perform packaging operations.  
Under the hood, the package command is performing a `git archive` run based on `CHANGELOG.md`.

Install additional dependencies:

```bash
python -m pip install -U -r requirements/packaging.txt
```

Then use it:

```bash
# package a specific version
qgis-plugin-ci package 1.3.1
# package latest version
qgis-plugin-ci package latest
# print the changelog of a version, as used in the release notes
qgis-plugin-ci changelog 1.3.1
```

## Release a version

Pushing a tag triggers the `releaser.yml` workflow, which creates the GitHub release with the plugin zip and
`plugins.xml`, and uploads the zip to [plugins.qgis.org](https://plugins.qgis.org/plugins/qgis_hub_plugin/) with the
`QGIS_PLUGIN_TOKEN` repository secret.

1. Open a PR adding the new version to `CHANGELOG.md`, and merge it into `main`.
   Use plain `Added:` / `Changed:` / `Fixed:` labels, not `###` headings: qgis-plugin-ci ends a version's notes at the
   next `##`, which would leave the release notes and the plugin manager changelog empty.
   No need to edit the version in `metadata.txt`, it is set from the tag.
1. Make sure CI passes on `main`, then tag and push:

   ```bash
   git checkout main && git pull
   git tag -a X.Y.Z -m "Version X.Y.Z"
   git push origin X.Y.Z
   ```

1. Check the Releaser run, the GitHub release, and the security scan of the new version on plugins.qgis.org.

Do not create the GitHub release by hand before pushing the tag: the workflow then fails because the release already
exists. A version number can only be uploaded once to plugins.qgis.org, so a blocked or broken upload needs a new patch
version.
