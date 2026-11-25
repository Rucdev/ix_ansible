# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import re

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_bytes, to_text
from ansible_collections.ansible.netcommon.plugins.plugin_utils.terminal_base import (
    TerminalBase,
)


class TerminalModule(TerminalBase):
    def __init__(self, connection) -> None:
        super().__init__(connection)

    terminal_stdout_re = [
        re.compile(
            rb"[\r\n]?[\w\+\-\.:\/\[\]]+(?:\([^\)]+\)){0,3}(?:[%$#]) ?$",
        ),
    ]

    # IX error messages that mean a command failed. Add new ones as they are found.
    terminal_stderr_re = [
        re.compile(rb"% .* Invalid command\."),
        re.compile(rb"% .* -- Ambiguous command."),
        re.compile(rb"% Expects a subcommand or item selection."),
        re.compile(rb"% Another OSPF process is already running."),
        re.compile(rb"% This network is already registered."),
        re.compile(rb"% This range is already registered."),
        re.compile(rb"% Area not found."),
        re.compile(rb"% Area is a stub area or nssa, so virtual links are not allowed"),
        re.compile(rb"% Area contains some interfaces or virtual-links."),
        re.compile(rb"% Same instance ID is already used."),
    ]

    terminal_config_prompt = re.compile(r"^.+\(config\)#$")

    def on_open_shell(self) -> None:
        pass

    def on_become(self, passwd=None) -> None:
        if self._get_prompt().endswith(b"(config)#"):
            return
        cmd = {"command": "configure"}
        if passwd:
            cmd["prompt"] = to_text(
                r"[\r\n]?Password: ?$",
                errors="surrogate_or_strict",
            )
            cmd["answer"] = passwd
        try:
            self._exec_cli_command(
                to_bytes(json.dumps(cmd), errors="surrogate_or_strict"),
            )
        except AnsibleConnectionFailure as exc:
            msg = "unable to switch configure mode"
            raise AnsibleConnectionFailure(msg) from exc

    def on_unbecome(self) -> None:
        prompt = self._get_prompt()
        if prompt is None:
            return
        if b"(config" in prompt:
            self._exec_cli_command(b"configure")
            self._exec_cli_command(b"exit")
