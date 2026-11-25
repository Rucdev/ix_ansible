#
# (c) 2017 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.


"""Cliconf plugin for NEC IX routers."""

DOCUMENTATION = """
author: Yushi Takeda (@ruc_dev)
name: ix
short_description: Use ix cliconf to run command on NEC IX platform
description:
- ""
version_added: 0.1.0
"""

import json
import re

from functools import wraps

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_text
from ansible.module_utils.common._collections_compat import Mapping
from ansible.utils.display import Display
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import (
    NetworkConfig,
    dumps,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_list,
)
from ansible_collections.ansible.netcommon.plugins.plugin_utils.cliconf_base import (
    CliconfBase,
)

display = Display()


SVINTR_CONFIG = "svintr-config"

# Global config mode "(config)#" and sub-modes such as "(config-ospfv2-1)#".
CONFIG_PROMPT_RE = re.compile(r"\(config[^)]*\)#$")

# On IX these commands exist only in config mode (verified on IX2215 10.10.29);
# in exec mode they fail with "% running-config  -- Invalid command."
CONFIG_ONLY_COMMANDS_RE = re.compile(r"^\s*show\s+(running-config|startup-config)\b")


def configure_mode(func):
    """Decorate a Cliconf method so that it runs in config mode."""

    @wraps(func)
    def wrapped(self, *args, **kwargs):
        self._enter_config_mode()
        return func(self, *args, **kwargs)

    return wrapped


class Cliconf(CliconfBase):
    """Cliconf plugin for NEC IX routers."""

    def __init__(self, *args, **kwargs) -> None:
        """Set up the cache of the device information."""
        self._device_info = {}
        display.vvvvv("cliconf init")
        super().__init__(*args, **kwargs)

    def _current_prompt(self):
        prompt = self._connection.get_prompt()
        return to_text(prompt, errors="surrogate_or_strict").strip() if prompt else ""

    def _enter_config_mode(self) -> None:
        """Enter global config mode unless already there.

        From a sub-mode (e.g. "(config-ospfv2-1)#") "configure" also returns
        to the global "(config)#" prompt.
        """
        if not self._current_prompt().endswith("(config)#"):
            self.send_command("configure")

    def set_cli_prompt_context(self) -> None:
        """Make sure every task starts in exec mode, like cisco.ios.

        Called by network_cli at the start of each task. IX has no "end"
        command, so return with "configure" (to global config, also from a
        sub-mode) followed by "exit" (to exec) -- the same sequence
        edit_config uses.
        """
        if not self._connection.connected:
            return
        if CONFIG_PROMPT_RE.search(self._current_prompt()):
            self._connection.queue_message(
                "vvvv",
                "config mode at task start, returning to exec mode",
            )
            self.send_command("configure")
            self.send_command("exit")

    @configure_mode
    def get_config(self, source="running", flags=None, format=None):
        """Return the output of show running-config.

        flags are appended to the command without a space in between.
        source="startup" is accepted, but only "running" sets the show command,
        so the command is then built from the flags alone.
        """
        # running, startup以外はエラーとする
        if source not in ("running", "startup"):
            msg = f"fetching configuration for {source} is not supported"
            raise ValueError(msg)

        if format:
            msg = f"'format' value {format} is not supported for get_config"
            raise ValueError(msg)

        if not flags:
            flags = []

        cmd = ""
        if source == "running":
            cmd = "show running-config"
        cmd += " ".join(to_list(flags))
        cmd = cmd.strip()
        return self.send_command(cmd)

    def get_diff(
        self,
        candidate=None,
        running=None,
        diff_match=None,
        diff_ignore_lines=None,
        path=None,
        diff_replace=None,
    ):
        """Return the lines of the candidate config that the running config lacks."""
        diff = {}
        device_operations = self.get_device_operations()
        option_values = self.get_option_values()
        if candidate is None and device_operations["supports_generate_diff"]:
            msg = "candidate configuration is required to generate diff"
            raise ValueError(msg)

        if diff_match not in option_values["diff_match"]:
            msg = f"'match' value {diff_match} in invalid, valid values are {', '.join(option_values['diff_match'])}"
            raise ValueError(
                msg,
            )

        if diff_replace not in option_values["diff_replace"]:
            msg = f"'replace' value {diff_replace} in invalid, valid values are {', '.join(option_values['diff_replace'])}"
            raise ValueError(
                msg,
            )

        # Banners are not compared; only the configuration lines are.
        candidate_obj = NetworkConfig(indent=1)
        candidate_obj.load(candidate)

        if running and diff_match != "none":
            running_obj = NetworkConfig(
                indent=1,
                contents=running,
                ignore_lines=diff_ignore_lines,
            )
            configdiffobjs = candidate_obj.difference(
                running_obj,
                path=path,
                match=diff_match,
                replace=diff_replace,
            )
        else:
            configdiffobjs = candidate_obj.items

        diff["config_diff"] = (
            dumps(configdiffobjs, "commands") if configdiffobjs else ""
        )

        return diff

    def get_device_info(self) -> dict:
        """Return the OS, version, model and hostname of the device."""
        if not self._device_info:
            device_info = {}
            device_info["network_os"] = "ix"

            reply = self.get(command="show version")
            data = to_text(reply, errors="surrogate_or_strict")
            version_pattern = r"IX Series (\S+).*Software, Version (\S+),"

            match = re.search(version_pattern, data, re.MULTILINE)
            if match:
                device_info["network_os_model"] = match.group(1)
                device_info["network_os_version"] = match.group(2)

            match = re.search(r"System image file is \"(\S*)\"", data, re.MULTILINE)
            if match:
                device_info["network_os_image"] = match.group(1)

            self.send_command(SVINTR_CONFIG)
            self.send_command("configure")
            self.send_command("terminal length 0")
            reply = self.get(command="show running-config")
            data = to_text(reply, errors="surrogate_or_strict")
            match = re.search(r"hostname (.+)", data, re.MULTILINE)
            if match:
                device_info["network_os_hostname"] = match.group(1)

            # Leave the session in exec mode like every other task boundary
            # (see set_cli_prompt_context); this runs inside the first task,
            # after its prompt-context check.
            self.send_command("configure")
            self.send_command("exit")

            self._device_info = device_info
        return self._device_info

    def get(
        self,
        command=None,
        prompt=None,
        answer=None,
        sendonly=False,
        newline=True,
        output=None,
        check_all=False,
    ):
        """Send one command and return its output."""
        if not command:
            msg = "must provide value of command to execute"
            raise ValueError(msg)
        if output:
            msg = f"'output' value {output} is not supported for get"
            raise ValueError(msg)

        return self.send_command(
            command=command,
            prompt=prompt,
            answer=answer,
            sendonly=sendonly,
            newline=newline,
            check_all=check_all,
        )

    @configure_mode
    def configure_get(
        self,
        command=None,
        prompt=None,
        answer=None,
        sendonly=False,
        newline=True,
        output=None,
        check_all=False,
    ):
        """Send one command in config mode and return its output."""
        return self.get(
            command,
            prompt,
            answer,
            sendonly,
            newline,
            output,
            check_all,
        )

    def get_capabilities(self) -> str:
        """Return the capabilities of the plugin and the device as JSON."""
        result = super().get_capabilities()
        result["rpc"] += ["get_diff", "run_commands"]
        result["device_operations"] = self.get_device_operations()
        result.update(self.get_option_values())
        return json.dumps(result)

    def get_device_operations(self) -> dict:
        """Return the configuration operations that the device supports."""
        return {
            "supports_diff_replace": True,
            "supports_commit": False,
            "supports_rollback": False,
            "supports_onbox_diff": False,
            "supports_commit_comment": False,
            "supports_multiline_delimiter": False,
            "supports_diff_match": True,
            "supports_diff_ignore_lines": True,
            "supports_generate_diff": True,
            "supports_replace": False,
        }

    def get_option_values(self):
        """Return the accepted values of the format, diff and output options."""
        return {
            "format": ["text"],
            "diff_match": ["line", "strict", "exact", "none"],
            "diff_replace": ["line", "block"],
            "output": [],
        }

    def run_commands(self, commands=None, check_rc=True) -> list:
        """Run commands and return their outputs."""
        if commands is None:
            msg = "'commands' value is required"
            raise ValueError(msg)

        responses = []
        for item in to_list(commands):
            cmd = item if isinstance(item, Mapping) else {"command": item}
            output = cmd.pop("output", None)
            if output:
                msg = f"'output' value {output} is not supported for run_commands"
                raise ValueError(
                    msg,
                )

            if CONFIG_ONLY_COMMANDS_RE.match(to_text(cmd["command"])):
                self._enter_config_mode()

            try:
                out = self.send_command(**cmd)
            except AnsibleConnectionFailure as e:
                if check_rc:
                    raise
                out = getattr(e, "err", to_text(e))

            responses.append(out)

        return responses

    @configure_mode
    def run_configs(self, commands=None, *, check_rc=True) -> list:
        """Run commands in config mode and return their outputs."""
        return self.run_commands(commands=commands, check_rc=check_rc)

    @configure_mode
    def edit_config(
        self,
        candidate=None,
        commit=True,
        replace=None,
        diff=False,
        comment=None,
    ):
        """Send the candidate lines in config mode."""
        resp = {}
        operations = self.get_device_operations()
        self.check_edit_config_capability(
            operations,
            candidate,
            commit,
            replace,
            comment,
        )

        results = []
        requests = []
        if commit:
            self.send_command("configure")
            for item in to_list(candidate):
                line = item if isinstance(item, Mapping) else {"command": item}
                cmd = line["command"]
                if cmd != "exit":
                    results.append(self.send_command(**line))
                    requests.append(cmd)

            self.send_command("configure")
            self.send_command("exit")

        else:
            msg = "check mode is not supported"
            raise ValueError(msg)

        resp["request"] = requests
        resp["response"] = results
        return resp

    def get_default_flag(self) -> str:
        """Return the show running-config flag that includes the default values."""
        self.send_command(SVINTR_CONFIG)
        out = self.get("show running-config ?")
        out = to_text(out, errors="surrogate_then_replace")

        commands = set()
        for line in out.splitlines():
            if line.strip():
                commands.add(line.strip().split()[0])
        if "all" in commands:
            return "all"
        return "full"
