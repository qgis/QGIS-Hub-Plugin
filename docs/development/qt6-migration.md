# Qt6 / QGIS 4 migration notes

Reference notes for the QGIS 3 / Qt5 → QGIS 4 / Qt6 migration done in
`v0.6.0`. Future maintainers hitting odd Qt6 behaviour: start here.

The plugin supports **both** Qt5 (QGIS 3.28+) and Qt6 (QGIS 4.x) from a
single codebase. CI runs the integration suite on both `qgis/qgis:release-3_34`
and `qgis/qgis:4.0` to catch regressions on either side.

## 1. Webp thumbnails (Qt6 has no webp plugin)

Qt5 in QGIS 3 ships the webp image-format plugin. Qt6 in QGIS 4 does
**not**. `QPixmap("foo.webp")` silently returns a null pixmap with no
visible error, just a broken thumbnail.

**Workaround** (`qgis_hub_plugin/utilities/common.py`):

- Probe `QImageReader.supportedImageFormats()` once at import time
  (`_QT_SUPPORTED_IMAGE_FORMATS`).
- When Qt cannot decode the downloaded format, fall back to a one-shot
  Pillow → PNG conversion stored beside the original
  (`_convert_thumbnail_to_png`). The PNG sibling is reused on subsequent
  calls.
- Pillow is an **optional** dependency (`HAS_PILLOW`); without it,
  un-decodable thumbnails fall back to the default hub icon.

If a webp variant ever ships with Qt6 in a future QGIS release, the
probe will detect it and skip the conversion path automatically.

## 2. Scoped Qt enums

PyQt5 accepts both `Qt.UserRole` (unscoped) and `Qt.ItemDataRole.UserRole`
(scoped). PyQt6 only accepts the scoped form. Raw ints are no longer
coerced to enum values either.

Use the scoped form everywhere:

| Unscoped (Qt5-only)               | Scoped (works on both)                          |
| --------------------------------- | ----------------------------------------------- |
| `Qt.UserRole`                     | `Qt.ItemDataRole.UserRole`                      |
| `Qt.KeepAspectRatio`              | `Qt.AspectRatioMode.KeepAspectRatio`            |
| `Qt.WaitCursor`                   | `Qt.CursorShape.WaitCursor`                     |
| `Qt.CaseInsensitive`              | `QRegularExpression.PatternOption.CaseInsensitiveOption` |
| `QSizePolicy.Minimum`             | `QSizePolicy.Policy.Minimum`                    |
| `QNetworkReply.NoError`           | `QNetworkReply.NetworkError.NoError`            |
| `QDialogButtonBox.Help`           | `QDialogButtonBox.StandardButton.Help`          |
| `QIODevice.WriteOnly`             | `QIODevice.OpenModeFlag.WriteOnly`              |
| `QItemSelectionModel.ClearAndSelect` | `QItemSelectionModel.SelectionFlag.ClearAndSelect` |
| `QFormLayout.LabelRole`           | `QFormLayout.ItemRole.LabelRole`                |
| `QMessageBox.Yes` / `.No`         | `QMessageBox.StandardButton.Yes` / `.No`        |

**Watch out in tests.** `mock.error.return_value = 0` worked on Qt5
because PyQt compared int-to-enum loosely; on Qt6 it must be
`QNetworkReply.NetworkError.NoError`. Same for
`proxy.sort(0, 1)` — under Qt6 the second argument must be
`Qt.SortOrder.DescendingOrder`. These failures only surface on the Qt6
CI job (or against a local QGIS 4 install) — they pass on Qt5 LTS CI.

## 3. `QRegExp` is gone in Qt6

Replace everywhere:

```python
# Qt5-only
from qgis.PyQt.QtCore import QRegExp
proxy.setFilterRegExp(QRegExp(text, Qt.CaseInsensitive))
if regex.indexIn(s) != -1: ...

# Works on both
from qgis.PyQt.QtCore import QRegularExpression
proxy.setFilterRegularExpression(
    QRegularExpression(text, QRegularExpression.PatternOption.CaseInsensitiveOption)
)
if regex.match(s).hasMatch(): ...
```

## 4. Translations + f-strings

`pylupdate` cannot extract f-string contents from inside `self.tr(...)`,
so any runtime-interpolated values defeat translation:

```python
# Wrong — the literal string seen by pylupdate is "Script "{resource.name}" added"
self.show_error_message(self.tr(f"Script “{resource.name}” added"))

# Right — pylupdate extracts "Script "{name}" added", placeholders fill at runtime
self.show_error_message(
    self.tr("Script “{name}” added").format(name=resource.name)
)
```

This is not Qt6-specific, but came up during the migration when new
error branches were added. Several pre-existing `tr(f"…")` sites
remain in the codebase — clean up opportunistically.

## 5. CI: PEP 668 on Trixie-based QGIS 4 image

The `qgis/qgis:4.0` image is built on Debian Trixie with Python 3.13,
which marks the system Python as **externally managed** (PEP 668). pip
refuses to install into system site-packages without
`--break-system-packages`.

In `.github/workflows/tester.yml`:

- The flag is set **per matrix entry** (`pip-extra-args`), because older
  pip in the Qt5 image errors on unknown flags.
- The `pip install --upgrade pip setuptools wheel` step was **dropped**:
  the Debian-managed `wheel` on Trixie has no RECORD file, so pip
  refuses to uninstall it for the upgrade. The container pip on both
  images is recent enough to install `requirements/testing.txt`
  directly.

## 6. Local dev venv

PyQGIS is not on PyPI. The venv must link to system packages:

```bash
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
python -m pip install -U -r requirements/development.txt
```

A clean venv (without `--system-site-packages`) will not import `qgis`
and the QGIS-dependent tests (`tests/qgis/`) will all fail with
`ModuleNotFoundError: No module named 'qgis'`.

## 7. Friendlier error for PyQt5-only processing scripts

QGIS Hub still hosts processing scripts written against PyQt5
(`from PyQt5.QtCore import ...`). Under Qt6 these fail to import with a
`ModuleNotFoundError: No module named 'PyQt5'`.

`add_processing_script_to_qgis` in `gui/resource_browser.py` catches the
specific case and surfaces a clear message pointing at `qgis.PyQt`
(the version-agnostic shim) instead of a raw traceback. The script is
still saved to disk so the user can edit and re-add it.

## 8. Things still not working on Qt6

Tracked but not fixed in `v0.6.0`:

- PyQt5-only processing scripts cannot be loaded until the upstream
  script is updated to import from `qgis.PyQt`. The error is surfaced
  cleanly (see section 7); a real fix would need upstream cooperation
  from script authors on QGIS Hub.

The relevant entry point is `add_processing_script_to_qgis` in
`gui/resource_browser.py`.
