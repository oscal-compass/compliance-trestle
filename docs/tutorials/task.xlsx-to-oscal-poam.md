# xlsx-to-oscal-poam Task Tutorial

## Overview

The `xlsx-to-oscal-poam` task transforms FedRAMP Plan of Action and Milestones (POA&M) Excel spreadsheets into OSCAL POAM JSON format. This task is designed specifically for the FedRAMP POAM template structure and creates valid OSCAL v1.1+ POAM documents.

## Prerequisites

- Trestle installed (see [Installation Guide](../installation.md))
- FedRAMP POAM Excel template or compatible spreadsheet
- Basic understanding of OSCAL POAM format
- Initialized trestle workspace (run `trestle init` in your working directory)

## Quick Start

### 1. Create Configuration File

Create a configuration file (e.g., `.trestle/config.ini`):

```ini
[task.xlsx-to-oscal-poam]
xlsx-file = path/to/FedRAMP-POAM-Template.xlsx
output-dir = output/poams
title = MySystem Plan of Action and Milestones
version = 1.0
```

### 2. Run the Task

```bash
trestle task xlsx-to-oscal-poam -c .trestle/config.ini
```

### 3. Verify Output

The task creates `output/poams/plan-of-action-and-milestones.json` with your OSCAL POAM:

```bash
cat output/poams/plan-of-action-and-milestones.json | jq '.plan-of-action-and-milestones.poam-items | length'
```

## Configuration Parameters

### Required Parameters

| Parameter    | Description                     | Example                      |
| ------------ | ------------------------------- | ---------------------------- |
| `xlsx-file`  | Path to FedRAMP POAM Excel file | `FedRAMP-POAM-Template.xlsx` |
| `output-dir` | Output directory for POAM JSON  | `output/poams`               |
| `title`      | Title for the POAM document     | `Production System POA&M`    |
| `version`    | Version of the POAM             | `1.0`                        |

### Optional Parameters

| Parameter                  | Description                             | Default            |
| -------------------------- | --------------------------------------- | ------------------ |
| `work-sheet-name`          | Name of Excel worksheet to process      | `Open POA&M Items` |
| `system-id`                | System identifier for the POAM          | None               |
| `output-overwrite`         | Overwrite existing output file          | `true`             |
| `validate-required-fields` | Validation mode: `on`, `warn`, or `off` | `warn`             |
| `quiet`                    | Suppress informational messages         | `false`            |

### Validation Modes

- **`on`**: Fail task if any validation errors occur (strict mode)
- **`warn`**: Log warnings but continue processing (default)
- **`off`**: Skip validation (not recommended)

## Excel Template Requirements

### Template Structure

The FedRAMP POAM Excel template must have:

- **Rows 1-4**: Template metadata and instructions
- **Row 5**: Column headers
- **Row 6+**: Data rows (one POAM item per row)

### Required Columns

The following columns are required (task will fail if missing):

1. **POAM ID**: Unique identifier for each POAM item (e.g., `P001`)
1. **Controls**: NIST control IDs (e.g., `AC-1, AC-2, SC-7(5)`)
1. **Weakness Name**: Title of the weakness/issue
1. **Weakness Description**: Detailed description

### Optional Columns

All other columns are optional but recommended:

- Weakness Detector Source
- Weakness Source Identifier (e.g., CVE ID)
- Asset Identifier
- Point of Contact
- Resources Required
- Overall Remediation Plan
- Original Detection Date
- Scheduled Completion Date
- Planned Milestones
- Risk ratings (Original/Adjusted)
- Status fields (Risk Adjustment, False Positive, Operational Requirement)
- And more... (see Column Mapping below)

## Column-to-OSCAL Mapping

### PoamItem Mapping

| Excel Column         | OSCAL Field                         | Notes                         |
| -------------------- | ----------------------------------- | ----------------------------- |
| POAM ID              | `PoamItem.props[name='poam-id']`    | Also used for UUID generation |
| Weakness Name        | `PoamItem.title`                    | Required                      |
| Weakness Description | `PoamItem.description`              | Required                      |
| Controls             | `PoamItem.props[name='control-id']` | One property per control ID   |
| Comments             | `PoamItem.remarks`                  | Optional                      |
| Supporting Documents | `PoamItem.links`                    | If URLs provided              |

### Observation Mapping

| Excel Column               | OSCAL Field                           | Notes                                  |
| -------------------------- | ------------------------------------- | -------------------------------------- |
| Weakness Detector Source   | `Observation.origins[0].actors[0]`    | Actor type: tool/assessment-platform   |
| Asset Identifier           | `Observation.subjects[0]`             | Subject type: component/inventory-item |
| Original Detection Date    | `Observation.collected`               | Required field                         |
| Weakness Source Identifier | Included in `Observation.description` | E.g., CVE ID                           |

### Risk Mapping

| Excel Column              | OSCAL Field                                  | Notes                                      |
| ------------------------- | -------------------------------------------- | ------------------------------------------ |
| Weakness Name             | `Risk.title`                                 | Required                                   |
| Weakness Description      | `Risk.description`                           | Required                                   |
| Overall Remediation Plan  | `Risk.statement`                             | Required                                   |
| Status                    | `Risk.status`                                | Always `"open"` for Open POA&M Items sheet |
| Original Risk Rating      | `Risk.props[name='original-risk-rating']`    | Low/Moderate/High/N/A                      |
| Adjusted Risk Rating      | `Risk.props[name='adjusted-risk-rating']`    | Low/Moderate/High/N/A                      |
| Scheduled Completion Date | `Risk.deadline`                              | ISO 8601 datetime                          |
| Planned Milestones        | `Risk.remediations[0].tasks[]`               | Parsed into Task objects                   |
| Risk Adjustment           | `Risk.props[name='risk-adjustment']`         | Yes/No/Pending                             |
| False Positive            | `Risk.props[name='false-positive']`          | Yes/No/Pending                             |
| Operational Requirement   | `Risk.props[name='operational-requirement']` | Yes/No/Pending                             |
| Deviation Rationale       | `Risk.props[name='deviation-rationale']`     | Free text                                  |

## Data Format Specifications

### Control IDs

Control IDs must follow the pattern: `XX-N` or `XX-N(N)`

**Valid examples**:

- `AC-1` (Access Control family, control 1)
- `SC-7(5)` (System and Communications Protection family, control 7, enhancement 5)
- `AU-2, AU-3, AU-12` (Multiple controls, comma-separated)

**Invalid examples**:

- `ac1` (missing hyphen)
- `AC-` (missing number)
- `A-1` (family must be 2 letters)

### Risk Ratings

Risk rating values must be:

- `Low`
- `Moderate`
- `High`
- `N/A` (not applicable)

Case-insensitive, but stored as shown above.

### Yes/No/Pending Fields

Fields like Risk Adjustment, False Positive, and Operational Requirement accept:

- `Yes`
- `No`
- `Pending`

Case-insensitive.

### Dates

Dates can be in:

1. **Excel date format** (automatically detected)
1. **ISO 8601 string**: `YYYY-MM-DDTHH:MM:SS±HH:MM` or `YYYY-MM-DD`

All dates are stored with UTC timezone in the output.

### Milestones

Milestones can be formatted as:

```
Milestone 1: Complete analysis by 2024-03-01
Milestone 2: Deploy fix by 2024-06-30
```

The parser handles:

- Multi-line milestone text (separated by newlines)
- Optional dates (using `by YYYY-MM-DD` pattern)
- Numbered milestones (`Milestone N:` or `M1:`)

## Usage Examples

### Example 1: Basic Usage

```ini
[task.xlsx-to-oscal-poam]
xlsx-file = FedRAMP-POAM-Template.xlsx
output-dir = output
title = Production System POA&M
version = 1.0
```

```bash
trestle task xlsx-to-oscal-poam -c config.ini
```

### Example 2: With System ID

```ini
[task.xlsx-to-oscal-poam]
xlsx-file = poam-2024-q1.xlsx
output-dir = output/2024-q1
title = Q1 2024 POA&M
version = 1.0
system-id = prod-system-001
```

### Example 3: Strict Validation

```ini
[task.xlsx-to-oscal-poam]
xlsx-file = FedRAMP-POAM-Template.xlsx
output-dir = output
title = Validated POA&M
version = 1.0
validate-required-fields = on
```

This will fail if any required fields are missing.

### Example 4: Custom Worksheet

```ini
[task.xlsx-to-oscal-poam]
xlsx-file = custom-poam.xlsx
output-dir = output
title = Custom POA&M
version = 1.0
work-sheet-name = Closed POA&M Items
```

## Troubleshooting

### Issue: "Excel file not found"

**Cause**: The `xlsx-file` path is incorrect or file doesn't exist.

**Solution**:

- Use absolute paths or paths relative to where you run the command
- Check file name spelling and extension (.xlsx)

### Issue: "Worksheet not found"

**Cause**: The specified worksheet name doesn't exist in the Excel file.

**Solution**:

- Verify worksheet name matches exactly (case-sensitive)
- Default is `"Open POA&M Items"` - check if your template uses a different name
- Error message lists available worksheets

### Issue: "Missing required field"

**Cause**: One or more required columns are missing or have empty values.

**Solution**:

- Required columns: POAM ID, Controls, Weakness Name, Weakness Description
- Check that column headers match exactly (case-sensitive)
- Ensure data rows have values in required columns

### Issue: "Invalid control format"

**Cause**: Control IDs don't match expected pattern.

**Solution**:

- Use format: `XX-N` or `XX-N(N)` (e.g., `AC-1`, `SC-7(5)`)
- Multiple controls: separate with commas: `AC-1, AC-2`
- In `warn` mode, invalid controls are skipped with warnings

### Issue: "Invalid risk rating"

**Cause**: Risk rating value is not one of the valid options.

**Solution**:

- Valid values: Low, Moderate, High, N/A
- Check for typos or extra spaces
- Case-insensitive but must match one of the four values

### Issue: Output file already exists

**Cause**: Output file exists and `output-overwrite` is `false`.

**Solution**:

- Set `output-overwrite = true` to allow overwriting
- Or delete/move the existing output file
- Or change the `output-dir` to a different location

## Advanced Topics

### UUID Generation Strategy

The task uses **deterministic UUIDs** (UUID5) for stability across runs:

```python
NAMESPACE = 'e8d8efc6-c23e-4e3e-a2e8-bc8fc08ff6c3'

poam_item_uuid = uuid5(NAMESPACE, f'poam-item-{POAM_ID}')
observation_uuid = uuid5(NAMESPACE, f'observation-{POAM_ID}')
risk_uuid = uuid5(NAMESPACE, f'risk-{POAM_ID}')
```

**Benefits**:

- Same POAM ID always generates same UUID
- Enables stable updates when re-processing
- Facilitates merging with existing POAM files

### Object Linking

Each Excel row creates **three linked OSCAL objects**:

1. **PoamItem**: Main weakness description

   - Links to → Observation (via `related_observations`)
   - Links to → Risk (via `related_risks`)

1. **Observation**: Detection details

   - Linked from → PoamItem

1. **Risk**: Risk assessment and remediation

   - Links to → Observation (via `related_observations`)
   - Linked from → PoamItem

This creates a comprehensive representation of each weakness.

### Custom Property Namespaces

Properties are created without explicit namespaces by default. To add namespaces:

1. Modify the task source code in `PoamBuilder.create_poam_item()`
1. Add `ns` parameter to Property creation:

```python
Property(name='poam-id', value=poam_id, ns='https://example.com/ns/poam')
```

## Future Enhancements

### Planned Features (Not Yet Implemented)

1. **Update/Merge Support**:

   - Read existing POAM JSON
   - Merge Excel changes with existing data
   - Preserve UUIDs for unchanged items
   - Track modifications

1. **Closed POA&M Items Support**:

   - Process "Closed POA&M Items" worksheet
   - Set Risk.status to `"closed"`

1. **Validation Against Profile**:

   - Validate control IDs against resolved profile catalog
   - Similar to `csv-to-oscal-cd` control validation

## Reference

- [OSCAL POAM Specification](https://pages.nist.gov/OSCAL/concepts/layer/assessment/poam/)
- [FedRAMP POAM Requirements](https://www.fedramp.gov/assets/resources/templates/FedRAMP-POAM-Template.xlsx)
- [NIST SP 800-53 Controls](https://nvd.nist.gov/800-53)
- [Trestle Documentation](https://oscal-compass.github.io/compliance-trestle/)

## Getting Help

- **GitHub Issues**: [compliance-trestle/issues](https://github.com/oscal-compass/compliance-trestle/issues)
- **Command help**: `trestle task xlsx-to-oscal-poam -h`
- **Task info**: `trestle task xlsx-to-oscal-poam -i`
