from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import re

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_bytes, to_text
from ansible_collections.ansible.netcommon.plugins.plugin_utils.terminal_base import (
    TerminalBase,
)


class TerminalModule(TerminalBase):
    def __init__(self, connection):
        super().__init__(connection)

    terminal_stdout_re = [
        re.compile(
            rb"[\r\n]?[\w\+\-\.:\/\[\]]+(?:\([^\)]+\)){0,3}(?:[%$#]) ?$",
        )
    ]

    # TODO: エラーメッセージのパターンをある程度収集する
    terminal_stderr_re = [
        re.compile(rb"% .* Invalid command\."),
        re.compile(rb"% .* -- Ambiguous command."),
        re.compile(rb"% Expects a subcommand or item selection."),
    ]

    terminal_config_prompt = re.compile(r"^.+\(config\)#$")

    def on_open_shell(self):
        pass

    def on_become(self, passwd=None):
        if self._get_prompt().endswith(b"(config)#"):
            return
        cmd = {"command": "configure"}
        if passwd:
            cmd["prompt"] = to_text(
                r"[\r\n]?Password: ?$", errors="surrogate_or_strict"
            )
            cmd["answer"] = passwd
        try:
            self._exec_cli_command(
                to_bytes(json.dumps(cmd), errors="surrogate_or_strict")
            )
        except AnsibleConnectionFailure:
            raise AnsibleConnectionFailure("unable to switch configure mode")

    def on_unbecome(self):
        prompt = self._get_prompt()
        if prompt is None:
            return
        elif b"(config" in prompt:
            self._exec_cli_command(b"configure")
            self._exec_cli_command(b"exit")
