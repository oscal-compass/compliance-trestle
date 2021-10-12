# Using trestle as an object model for OSCAL

Trestle provides an object model for OSCAL to ease the development and validation of OSCAL objects that reside in the `trestle.oscal` module.
This functionality, which is built on [pydantic](https://pydantic-docs.helpmanual.io/) and [python data classes](https://docs.python.org/3/library/dataclasses.html), allows validation of the OSCAL schema and is leveraged to provide a variety of utility functions including:

- IO Support for yaml / json / python dict serialisation [see `OscalBaseModel` for trestle enhancements](https://github.com/IBM/compliance-trestle/blob/develop/trestle/core/base_model.py)
- The ability to generate pro-forma objects using [`trestle.core.generate::generate_sample_model`](https://github.com/IBM/compliance-trestle/blob/develop/trestle/core/generators.py)
- Integration into the flask api framework [(demo)](https://github.com/IBM/compliance-trestle-demos/tree/develop/trestle_flask_api)

## Mapping and variance with OSCAL names.

The underlying object model that trestle relies on is the json schema published by NIST [here](https://github.com/usnistgov/OSCAL/tree/main/json/schema). In understanding these models the [model reference page](https://pages.nist.gov/OSCAL/reference/1.0.0/) is an indispensable source.

When generating the python data class based models we have tried to be as faithful as we can to the naming convention provided by OSCAL. This is the hierarchy of rules that we have used:

1. Do not include prepends from the json schema (e.g. `assembly_oscal-catalog_catalog` becomes the short name `catalog`), modules are used for scoping statements
1. OSCAL modules use hyphen case (e.g. `system-security-plan`) and this is converted to CamelCase (e.g. `SystemSecurityPlan`)
1. Name collisions with [reserved words](https://docs.python.org/3/reference/lexical_analysis.html#keywords) in python are post-pended with an underscore (e.g. `class` becomes `class_`)
1. If a model is used across multiple OSCAL schemas (e.g. `metadata`) it is put into the common module(`trestle.oscal.common`), otherwise it will be scoped to a model specifically for that schema.
1. Any unresolved duplicates are resolved by adding an index e.g. `class State1`

### OSCAL Schema mapping

This maps between OSCAL values and the corresponding pydantic/python data class in trestle. For example, to get a catalog you would call:

```python
from pathlib import Path
from trestle.oscal.catalog import Catalog

my_catalog = Catalog.oscal_read(Path('path/to/file.json'))
```

| Oscal schema                  | json schema name                | Trestle module                     | Trestle class name          |
| ----------------------------- | ------------------------------- | ---------------------------------- | --------------------------- |
| Catalog                       | `catalog`                       | `catalog`                          | `trestle.oscal.catalog`     |
| Profile                       | `profile`                       | `profile`                          | `trestle.oscal.profile`     |
| Component Definition          | `component-definition`          | `trestle.oscal.component`          | `ComponentDefinition`       |
| System Security Plan          | `system-security-plan`          | `trestle.oscal.ssp`                | `SystemSecurityPlan`        |
| Assessment Plan               | `assessment-plan`               | `trestle.oscal.assessment_plan`    | `AssessmentPlan`            |
| Assessment Results            | `assessment-results`            | `trestle.oscal.assessment_results` | `AssessmentResults`         |
| Plan of action and milestones | `plan-of-action-and-milestones` | `trestle.oscal.poam`               | `PlanOfActionAndMilestones` |
