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
import os
import shlex
import subprocess as sp
import sys


class DocAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        environ = os.environ.copy()
        page = namespace.doc.man_page
        if os.path.isabs(page) and not os.path.isfile(page):
            print('ERROR - unable to man page "{}"'.format(page))
            exit(1)

        section = getattr(namespace.doc, 'man_section', 1)
        jump_section = getattr(namespace.doc, 'man_jump_into', None)
        command = 'man ' + str(section)
        if jump_section is not None:
            try:
                sp.check_output(
                    shlex.split('grep "{}" "{}"'.format(jump_section, page)),
                    stderr=sp.PIPE,
                    env=environ
                )
            except sp.CalledProcessError:
                print(
                    'ERROR - unable to find {} section at {}'.format(
                        jump_section, page)
                )
                exit(1)
            command += " -P 'less -p \"{}\" -G'".format(jump_section)
        command += ' "{}"'.format(page)
        try:
            sp.call(shlex.split(command), stderr=sp.PIPE, env=environ)
        except sp.CalledProcessError:
            print('ERROR - error while opening man: ' + command)
            exit(1)
        exit(0)


class ServeRestAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        import json
        import io

        from contextlib import contextmanager

        from flask import Flask, request

        @contextmanager
        def catch_stdout_stderr(cmd, out, err):
            old_stdout = cmd._out
            old_stderr = cmd._err
            old_sys_stdout = sys.stdout
            old_sys_stderr = sys.stderr
            cmd._out = out
            cmd._err = err
            # sys's out/err need to be caught in case "parse_args" fails
            # (as it is managed by ArgumentParser)
            sys.stdout = out
            sys.stderr = err
            try:
                yield
            finally:
                cmd.stdout = old_stdout
                cmd.stderr = old_stderr
                sys.stdout = old_sys_stdout
                sys.stderr = old_sys_stderr

        def run_wrapper(cmd):
            def wrapper():
                args = [v for _, v in request.args.items()]
                out = io.StringIO()
                err = io.StringIO()
                with catch_stdout_stderr(cmd, out, err):
                    try:
                        parsed_args = cmd.parser.parse_args(args)
                        retcode = cmd._validate_and_run(parsed_args)
                    except SystemExit:
                        retcode = 1
                response = {
                    'retcode': retcode,
                    'out': out.getvalue(),
                    'err': err.getvalue()
                }
                return json.dumps(response)
            return wrapper

        cmd = namespace.serve_rest
        app = Flask(cmd.name)
        if not cmd.subcommands:
            app.add_url_rule('/', cmd.name, run_wrapper(cmd))
        exit(app.run(host='127.0.0.1'))
