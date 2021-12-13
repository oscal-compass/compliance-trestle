# Adding plugins to trestle

Trestle provides a mechanism for 3rd party providers to extend its command interface via a plugin architecture. All trestle plugins that conforms to this specification will be automatically discovered by trestle if installed, and their command(s) will be added to trestle sub-commands list. Below we describe this plugin mechanism with the help of an example plugin [`compliance-trestle-fedramp`](https://github.com/IBM/compliance-trestle-fedramp) that we created as a separate python project that can be installed via `pip`.

## Create the trestle plugin proejct

A separate plugin project needs to be created that will conatin the code for plugin and its commands. This plugin can be given any name and should be available for installation via `pip`. For example, we created a plugin project called  `compliance-trestle-fedramp` which can be installed as `pip install compliance-trestle-fedramp`. The project name doesn't need to start with `compliance-trestle`.

## Project Organization

The plugin project should be organized as shown below.

```text
compliance-trestle-fedramp
├── trestle_fedramp
│   ├── __init.py__
│   ├── commands
|   |   ├── __init.py__
|   |   ├── validate.py
│   ├── <other source files or folder>
├── <other files or folder>
```

Trestle uses a naming convention to discover the top-level module of the plugin projects. It expects the top-level module to be named `trestle_{plugin_name}`. This covention must be followed by plugins to be discoverable by trestle. In the above example, the top-level module is named as `trestle_fedramp` so that it can be autmatically discovered by trestle. All the python source files should be created inside this module (folder).

The top-evel module should contain a `commands` directory where all the plugin command files should be stored. Each command should have its own python file. In the above exaample, `validate.py` file conatins one command for this plugin. Other python files or folders should be created in the top-level module folder, outside the `commands` folder. This helps in keeping the commands separate and in their discovery by trestle.

## Command Creation

The plugin command should be created as shown in the below code snippet.

```python
from trestle.core.commands.command_docs import CommandBase
from trestle.core.commands.command_docs import CommandPlusDocs

class ValidateCmd(CommandBase):
    """Validate contents of an OSCAL model based on FedRAMP specifications."""

    name = 'fedramp-validate'

    def _init_arguments(self) -> None:
        logger.debug('Init arguments')
        self.add_argument('-f', '--file', help='OSCAL file to validate.', type=str, required=True)

        self.add_argument(
            '-o', '--output-dir', help='Output directory for validation results.', type=str, required=True
        )

    def _run(self, args: argparse.Namespace) -> int:
        model_file = pathlib.Path(args.file).resolve()

        output_dir = pathlib.Path(args.output_dir).resolve()
        ...
        ...
        return 0 if valid else 1

```

There should be a command class for example, `ValidateCmd` which should either extend from `CommandBase` or `CommandPlusDocs`. Trestle uses `ilcli` package to create commands. `CommandBase` extends from `ilcli.Command` that initializes the command including help messages and input parameters. `CommandPlusDocs` in turn extends from `CommandBase`. The difference between `CommandBase` and `CommandPLusDocs` is that `CommandBase` does not require command line parameter `trestle-root` to be set or the current directory to be a valid trestle root, whereas `CommandPlusDocs` requires a valid `trestle-root` and checks for it. Hence, depending upon the requirement of the plugin command it can extend from either of these classes.

The docstring of the command class is used as the help message for the command. Input arguments to the command should be specified in `_init_arguments` method as shown above. The acutal code of the command is contained in`_run` method. This method is called by ilcli when the command is excuted on the commandline. The command arguments can be accessed from the `args` input parameter as shown above. The command should return `0` in case of successful execution, or any number greater than 0 in case of failure. Please see `trestle.core.commands.common.return_codes.CmdReturnCodes` class for specific return codes in case of failure.

The command class should conatin the `name` field which should be set to the desired command name. In the above example, the command is called `fedramp-validate`. This name is automatically added to the list of sub-command names of trestle during the plugin discovery process. This command can then be invoked as `trestle {name}` from the commandline e.g., `trestle fedramp-validate`. Any input parameters to the command can also be passed on the commandline after the command name.
