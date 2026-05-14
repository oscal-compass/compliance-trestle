# -*- coding:utf-8; mode:python -#-

# Copyright (c) 2020 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import sys

from ilcli.actions import DocAction, ServeRestAction


class Command(object):
    """
    Base class defining default behaviour for commands. Create a child
    class in order to create a cli.
    """

    #: the list classes of subcommands
    subcommands = []

    #: list of arguments identified by their name (-f,--foo for options, foo
    # for positional arguments) a subcommand should ignore
    ignore_arguments = []

    #: the name of the command (if None, class name by default)
    name = None

    #: additional arguments to pass to the ArgumentParser and all sub-parsers
    parser_args = {}

    #: inherit arguments from parent commands
    inherit_arguments = True

    def __init__(
        self, parser=None, parent=None, name=None, out=None, err=None
    ):
        self.name = name or self.name or self.__class__.__name__.lower()
        self.parser = parser or argparse.ArgumentParser(
            prog=self.name,
            **self.parser_args
        )
        self._parent = parent

        self.help = self.__doc__ or ''
        self._subcommands = []
        self._err = err or (self._parent and self._parent._err) or sys.stderr
        self._out = out or (self._parent and self._parent._out) or sys.stdout

        self._known_options = set()

        if not self.subcommands:
            self.parser.set_defaults(func=self._validate_and_run)
        else:
            # Make sub parsers
            subps = self.parser.add_subparsers(dest='cmd')
            subps.required = True
            for c in self.subcommands:
                new_parser = subps.add_parser(
                    c.name or c.__name__.lower(),
                    help=c.__doc__,
                    **self.parser_args
                )
                cmd = c(parser=new_parser, parent=self)
                self._subcommands.append(cmd)

        self.init_arguments()

    def add_argument(self, *args, **kwargs):
        """
        Add an argument to the internal parser. It accepts the same syntax as
         ``argparse.ArgumentParser.add_argument()``.

        :param args: arguments to pass to ``argparse.ArgumentParser``
        :param kwargs: key-value arguments to pass to
          ``argparse.ArgumentParser``
        """
        chars = self.parser.prefix_chars
        if not args or len(args) == 1 and args[0][0] not in chars:
            option_strings = args
        else:
            opt_from_kwargs = self.parser._get_optional_kwargs(
                *args,
                **kwargs
            )['option_strings']
            option_strings = set(opt_from_kwargs) - self._known_options
            self._known_options.update(option_strings)

            if len(option_strings) == 0:
                # Cannot add the requested argument, so do nothing
                return

        if not self._subcommands:
            to_ignore = set(option_strings) & set(self.ignore_arguments)
            if not to_ignore:
                self.parser.add_argument(*option_strings, **kwargs)
            return

        for c in self._subcommands:
            to_ignore = set(option_strings) & set(c.ignore_arguments)
            if c.inherit_arguments and not to_ignore:
                c.add_argument(*option_strings, **kwargs)

    def init_arguments(self):
        """
        Initialise internal parser with the arguments for this command.

        This is the default implementation. Children classes must use
        _init_arguments().
        """
        self._init_arguments()

        if hasattr(self, 'man_page'):
            self.parser.add_argument(
                '--doc', nargs=0, default=self,
                action=DocAction,
                help='open documentation'
            )
        if hasattr(self, 'serve_rest') and self.serve_rest:
            self.parser.add_argument(
                '--serve-rest', nargs=0, default=self,
                action=ServeRestAction,
                help='start a REST server'
            )

    def run(self, args=None):
        """
        Run the command.

        This is the default implementation. Children classes must use
        ``_run()`` method.

        :param args: list of arguments. Default ``sys.argv``.
        """
        parsed_args, extra_args = self.parser.parse_known_args(args)
        return parsed_args.func(parsed_args, extra_args=extra_args)

    def _validate_and_run(self, parsed_args, extra_args=None):
        """
        Perform checks over the parsed arguments and call `_run()`. If
        ``_validate_arguments()`` returns anything but ``None`` then
        ``_run()`` will not be executed.

        :param parsed_args: already parsed and validated arguments at
          ArgumentParser level.
        :param extra_args: if provided, a list of the extra parsed
          arguments.
        """
        # execute this method on all parents
        retval = None
        if self._parent and self.inherit_arguments:
            retval = self._parent._validate_and_run(parsed_args)

        # excecute validate_arguments and take into account the
        # previous result from the parent
        retval = self._validate_arguments(parsed_args) or retval
        retval = self._validate_extra_arguments(extra_args) or retval

        if self.subcommands:
            return retval

        if retval is None:
            return self._run(parsed_args)

        return retval

    def _init_arguments(self):
        """
        Initialize argutments on the internal parser.

        To be implemented by children classes.
        """
        pass

    def _validate_arguments(self, parsed_args):
        pass

    def _validate_extra_arguments(self, extra_args):
        """
        Validate extra arguments. By default, extra arguments are treated
        as an error. This could be overriden by child classes to
        accept extra arguments. In that case, is up to the user to
        parse and store them appropriately since ``_run()`` will not
        be executed with these extra arguments at all.
        """
        if extra_args:
            self.parser.error(
                'unrecognized arguments: %s' % ' '.join(extra_args)
            )

    def _run(self, parsed_args):
        print('Not implemented yet!')
        return 1

    def err(self, *args):
        """
        Print a message into error output (by default, to ``sys.stderr``)::

          > self.err('hello')
          'hello\\n'
          > self.err('hello %s!', 'world')
          'hello world!\\n'
         > self.err()
         '\\n'

        :params args: list of parameters where first element is the
         message and the rest optional arguments will be applied to the
         first argument as string template arguments.
        """
        self.__write_file(self._err, *args)

    def out(self, *args):
        """
        Print a message into the output (by default, ``sys.stdout``)::

         > self.out('hello')
         'hello\\n'
         > self.out('hello %s!', 'world')
         'hello world!\\n'
         > self.out()
         '\\n'

        :params args: list of parameters where first element is the
          message and the rest optional arguments will be applied to the
          first argument as string template arguments.
        """
        self.__write_file(self._out, *args)

    def __write_file(self, f, *args):
        if len(args) == 1:
            f.write(args[0] + '\n')
        elif len(args) > 1:
            f.write(args[0] % args[1:] + '\n')
        else:
            f.write('\n')
        f.flush()
