# Trestle Task Specifications (v0.0.1)

## Table of Contents

- [Purpose](#purpose)
- [Users](#users)
- [Scope](#scope)
- [Trestle commands](#trestle-commands)
  - [Draft commands](#draft-commands)
- [Future work](#future-work)
  - [Deploy commands](#deploy-commands)
  - [Monitor commands](#monitor-commands)
  - [Reporting commands](#reporting-commands)

## Purpose

This document contains detail on "trestle tasks":

1. A definition of what the task it is and the usecases.
1. The Abstractions provided by a task.
1. The expectation for a task in terms of behaviour.
1. Key identified workflows.

## Overview of trestle tasks

The initial trestle apis were for performing a discrete set of operations on the files in the trestle directory. However, an arbitrary set of potential different tasks can be performed on top of OSCAL object. Many of these are "workflow" style items.

For trestle tasks a simple interface has been designed:

1. Tasks are considered independent. Interdependent use of tasks may be performed by is presumed to be performed outside of trestle e.g. a tool such as `tekton` is used to ensure fail-safety
1. Trestle tasks are primarily configured via config files rather than the CLI. This allows us to maintain a relatively simple CLI interface.

## Principles for trestle tasks

1. Trestle tasks must not take an object in the 'editing space' and move it to the 'published "dist" space'.
1. Trestle tasks MAY NOT take content from both spaces at the same time.
1. Trestle tasks MUST be able to be report on status as a task outcome
1. Trestle tasks SHOULD be able to be rolled back if technicallly fesiable.
1. If trestle tasks cannot be rolled back trestle actions *should* have a dry run mode / probing mode.
1. Trestle tasks SHOULD use the internal actions framework to queue / rollback operations.

## Users

- Trestle developers
- Trestle stakeholders looking for improvements.

# Interaction styles to use tasks.

## Assumptions

1. Users need to be able to select tasks
1. tasks will need configuration information.
1. Configuration information may be inconsistent acros various APIs
1. Configuration information may include credentials
1. tasks may be invoked as a python API call
1. API call does may pass configuration manually.
1. By default will use config

```shell
trestle tasks tasks_name #uses default config file in .trestle directory
trestle tasks tasks_name -c config.file # tasks will execute using user provided config file.
```

```
trestle tasks -l

returns all tasks with descriptions
```

```
class MyTask(TasksBase):

    def __init__(self, config_object):

    def execute(self) 
        returns succes criteria
```

# Reference tasks

## tasks 6: Target to component generation based on applicable controls.

### Inputs

- One target definition
- One profile

### Outputs

- One component definition

### Operation

## tasks 1: Creation of an sP from profile and component definition.

### Inputs

- 1:N Component definitions with a total of M components ()
- 1 or more profiles (profiles are recursive) (e.g. we need to collapse profiles)
  *- List of components applicable which is a subset of the M components.*

### Outputs

### Notes:

- Profile resolution is not required for first version (can be tested by ensuring profile only refers to a catalog object.)
- Component definitions in this use case are generic and will require a filtering both by applicable component and applicable controls.

## task 2: Partial SSP asembly from non-OSCAL artifacts or fragmentary artifacts

## task 3: AP Generation from SSP and inventory.

## task 4: Generation of pretty print OSCAL documents from json/yaml source

## task 5: Generation of asesment results with multiple sets of obserations

## task 7: SSP inventory injection (SSP + inventory => SSP with inventory.)

## task 8: SSP merging (service -> Platform):

## tasks 9: Approval integrated change detection.

# Open questions:

- Templating mechanisms.
- Inheritence of partial filled documents.
  - Behaviour on overwrite control.
