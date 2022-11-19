from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import re

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_bytes, to_text
from ansible.utils.display import Display
from ansible_collections.ansible.netcommon.plugins.plugin_utils.terminal_base import (
    TerminalBase,
)

display = Display()


class TerminalModule(TerminalBase):
    def __init__(self, connection):
        display.vvvvv("Terminal init")
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
    ]

    terminal_config_prompt = re.compile(r"^.+\(config\)#$")

    def on_open_shell(self):
        pass
        # try:
        #     prompt = self._get_prompt()
        #     if prompt.strip().endswith(b"#"):
        #         display.vvv("starting cli", self._connection._play_context.remote_addr)
        #     else:
        #         raise AnsibleConnectionFailure
        # except AnsibleConnectionFailure:
        #     raise AnsibleConnectionFailure("")
        # try:
        #     self._exec_cli_command(b"terminal length 0")
        # except AnsibleConnectionFailure:
        #     raise AnsibleConnectionFailure("unable to set parameters")
        # return super().on_open_shell()

    def on_become(self, passwd=None):
        display.vvv("ix role is become ")
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
