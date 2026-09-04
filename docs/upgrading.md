---
title: Upgrading
description: How to upgrade compliance-trestle from one major version to the next
---

# Upgrading

## v4 → v5

v5.0.0 is a breaking release. The changes below affect anyone who imports from
`trestle` directly in Python code. Users who interact with trestle only through
the CLI do not need to change any calling code, but must satisfy the Python and
dependency requirements listed first.

### Python version

v5 raises the minimum Python version from **3.10** to **3.11**. Before upgrading,
confirm your environment meets this requirement:

```bash
$ python -V
Python 3.11.x   # 3.11, 3.12, 3.13, or 3.14 are all supported
```

If you are on Python 3.10, upgrade your Python installation before proceeding.

### Install v5

```bash
pip install --upgrade "compliance-trestle>=5,<6"
```

### Breaking changes for Python API users

#### Pydantic v2 mode

The core model layer (`OscalBaseModel` and all generated OSCAL classes) now runs
in **full Pydantic v2 mode**. The v1 compatibility shim that was active in v4 has
been removed. The table below lists every pattern that changed.

| v4 (Pydantic v1 compat) | v5 (Pydantic v2) |
|---|---|
| `model.dict(by_alias=True, exclude_none=True)` | `model.model_dump(by_alias=True, exclude_none=True)` |
| `model.dict(by_alias=True, exclude_none=True, mode='json')` | `model.model_dump(by_alias=True, exclude_none=True, mode='json')` |
| `MyModel.parse_obj(data)` | `MyModel.model_validate(data)` (`parse_obj` still works but is deprecated and will be removed in a future release) |
| `MyModel.parse_raw(json_str)` | `MyModel.model_validate_json(json_str)` |
| `model.json()` | `model.model_dump_json()` |
| `model.schema()` | `MyModel.model_json_schema()` |
| `class MyModel(OscalBaseModel):\n    class Config:\n        ...` | `class MyModel(OscalBaseModel):\n    model_config = ConfigDict(...)` |
| `__root__` field on a model | Inherit from `RootModel` instead; access the value via `.root` |
| `ModelField` (from `pydantic.fields`) | `FieldInfo` (from `pydantic.fields`); field names are accessible via `model_fields` dict |

#### `AnyUrl` is no longer a `str` subclass

In Pydantic v2, `AnyUrl` instances are not strings. Code that compared or
concatenated a URL field directly with a string must call `str()` first:

```python
# v4
href = catalog.metadata.links[0].href  # was already a str

# v5
href = str(catalog.metadata.links[0].href)
```

Trestle's own serialization (`oscal_serialize_json_bytes`, `oscal_write`) handles
this automatically; only hand-written code that accesses URL fields is affected.

#### Datetime serialization precision

`robust_datetime_serialization` no longer always emits millisecond precision.
When the microsecond component is zero the output is now
`2024-01-01T00:00:00+00:00` instead of `2024-01-01T00:00:00.000+00:00`. Both
are valid ISO-8601 and accepted by all OSCAL validators. Code that does exact
string comparison of serialized datetimes should be updated to use
datetime-aware comparison instead.

#### `RiskStatus` and other root-model types

Models that previously used `__root__` now use `RootModel`. Access the
underlying value via the `.root` attribute:

```python
# v4
status_value = risk_status.__root__

# v5
status_value = risk_status.root
```

#### `model_fields` replaces `__fields__`

If your code introspected `MyModel.__fields__` (a Pydantic v1 dict of
`ModelField`), switch to `MyModel.model_fields` (a dict of `FieldInfo`):

```python
# v4
for name, field in MyModel.__fields__.items():
    alias = field.alias

# v5
for name, field_info in MyModel.model_fields.items():
    alias = field_info.alias if field_info.alias else name
```

### Verifying the upgrade

After upgrading, run a quick sanity check:

```bash
trestle version
```

If you have a trestle workspace, validate it:

```bash
trestle validate --all
```

### Still on v4?

v4 is in **maintenance mode** with security and bug-fix releases available until
**December 31, 2026**. Install the latest v4 patch with:

```bash
pip install --upgrade "compliance-trestle>=4,<5"
```

See [README § Development status](https://github.com/oscal-compass/compliance-trestle#development-status)
for the full support matrix.
