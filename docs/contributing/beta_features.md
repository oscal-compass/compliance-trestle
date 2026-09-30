---
title: Developing beta features
description: Guidance for adding experimental beta features to trestle
---

# Developing beta features

Use beta features for commands or behavior that should be available for early testing without becoming part of the
stable trestle interface yet. Beta features must be explicit opt-ins and should have tests and documentation before they
are registered.

## Register a feature

Register the feature in `trestle/core/beta_features.py`.

```python
BETA_FEATURES = {
    'example-feature': BetaFeature(
        name='example-feature',
        description='Short user-facing description',
        commands=['trestle example'],
        since_version='4.0.0',
        stability='beta',
        documentation_url='https://oscal-compass.github.io/compliance-trestle/beta/example-feature',
        enabled_by_default=False,
        deprecation_version=None,
    ),
}
```

Feature names should be stable, lower-case, and hyphenated.

## Guard beta behavior

Decorate the command run method with `@beta_feature('<feature-name>')`.

```python
from trestle.core.beta_features import beta_feature


class ExampleCmd(CommandBase):
    """Example beta command."""

    name = 'example'

    @beta_feature('example-feature')
    def _run(self, args: argparse.Namespace) -> int:
        """Run the beta command."""
        return CmdReturnCodes.SUCCESS.value
```

When the feature is disabled, the decorator returns a command error and tells the user how to enable the feature.
The decorator also allows `--beta` to run the beta command one time without writing config. Commands without the
decorator will warn that `--beta` is only effective for beta level commands, but will otherwise proceed normally.

## Configuration

`trestle beta enable <feature>` writes enabled features to `.trestle/config.ini` when the current directory is inside a
trestle workspace. Outside a workspace, trestle uses the user-level beta config file.

For CI and other ephemeral environments, `TRESTLE_BETA_FEATURES` can enable features without writing config:

```bash
TRESTLE_BETA_FEATURES=example-feature trestle example
```

Features enabled through `TRESTLE_BETA_FEATURES` cannot be disabled with `trestle beta disable`; remove the feature from
the environment variable instead.

## Documentation checklist

Each beta feature should document:

- What the feature does.
- Which commands or options it enables.
- The expected stability level.
- Known limitations.
- How to enable, use, and disable it.
