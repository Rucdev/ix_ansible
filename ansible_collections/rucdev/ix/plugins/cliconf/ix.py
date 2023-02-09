import re
import json
from functools import wraps
from ansible.module_utils._text import to_text
from ansible_collections.ansible.netcommon.plugins.plugin_utils.cliconf_base import (
    CliconfBase,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_list,
)
from ansible.module_utils.common._collections_compat import Mapping
from ansible.errors import AnsibleConnectionFailure
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import (
    NetworkConfig,
    dumps,
)
from ansible.utils.display import Display

DOCUMENTATION = """
author: 
- rucdev
name: ix
short_description: Use ix cliconf to run command on NEC IX platform
description:
- ""
version_added: 1.0.0
"""

display = Display()


def configure_mode(func):
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        prompt = self._connection.get_prompt()
        if not to_text(prompt, errors="surrogate_or_strict").strip().endswith("#"):
            self.send_command("configure")
        return func(self, *args, **kwargs)

    return wrapped


class Cliconf(CliconfBase):
    def __init__(self, *args, **kwargs):
        self._device_info = {}
        display.vvvvv("cliconf init")
        super(Cliconf, self).__init__(*args, **kwargs)

    @configure_mode
    def get_config(self, source="running", flags=None, format=None):
        if source not in ("running", "startup"):
            raise ValueError(
                # running, starting以外はエラーとする
                f"fetching configuration for {source} is not supported"
            )

        if format:
            raise ValueError(f"'format' value {format} is not supported for get_config")

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
        diff = {}
        device_operations = self.get_device_operations()
        option_values = self.get_option_values()
        if candidate is None and device_operations["supports_generate_diff"]:
            raise ValueError("candidate configuration is required to generate diff")

        if diff_match not in option_values["diff_match"]:
            raise ValueError(
                f"'match' value {diff_match} in invalid, valid values are {', '.join(option_values['diff_match'])}"
            )

        if diff_replace not in option_values["diff_replace"]:
            raise ValueError(
                f"'replace' value {diff_replace} in invalid, valid values are {', '.join(option_values['diff_replace'])}"
            )

        candidate_obj = NetworkConfig(indent=1)
        # TODO: バナーに対応させる
        # want_src, want_banners = self._extract_banners(candi)
        candidate_obj.load(candidate)

        if running and diff_match != "none":
            # have_src, have_banners = self._extract_banners(running)
            running_obj = NetworkConfig(
                indent=1, contents=running, ignore_lines=diff_ignore_lines
            )
            configdiffobjs = candidate_obj.difference(
                running_obj, path=path, match=diff_match, replace=diff_replace
            )
        else:
            configdiffobjs = candidate_obj.items
            have_banners = {}

        diff["config_diff"] = (
            dumps(configdiffobjs, "commands") if configdiffobjs else ""
        )
        # banners = self.__diff_banners(want_banners, have_banners)
        # diff["banner_diff"] = banners if banners else {}

        return diff

    def get_device_info(self) -> dict:
        if not self._device_info:
            device_info = {}
            device_info["network_os"] = "ix"

            reply = self.get(command="show version")
            data = to_text(reply, errors="surrogate_or_strict")
            version_pattern = r"IX Series (.+) Software, Version (\S+),"

            match = re.search(version_pattern, data, re.M)
            if match:
                device_info["network_os_version"] = match.group(2)

            # TODO: hostnameとnetwork_os_modelの取得方法を追加する
            self.send_command("configure")
            self.send_command("terminal length 0")
            reply = self.get(command="show running-config")
            data = to_text(reply, errors="surrogate_or_strict")
            match = re.search(r"hostname (.+)", data, re.M)
            if match:
                device_info["network_os_hostname"] = match.group(1)

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
        if not command:
            raise ValueError("must provide value of command to execute")
        if output:
            raise ValueError(f"'output' value {output} is not supported for get")

        return self.send_command(
            command=command,
            prompt=prompt,
            answer=answer,
            sendonly=sendonly,
            newline=newline,
            check_all=check_all,
        )

    def get_capabilities(self) -> str:
        result = super(Cliconf, self).get_capabilities()
        result["rpc"] += ["get_diff", "run_commands"]
        result["device_operations"] = self.get_device_operations()
        return json.dumps(result)

    def get_device_operations(self) -> dict:
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
        return {
            "format": ["text"],
            "diff_match": ["line", "strict", "exact", "none"],
            "diff_replace": ["line", "block"],
            "output": [],
        }

    def run_commands(self, commands=None, check_rc=True) -> list:
        if commands is None:
            raise ValueError("'commands' value is required")

        responses = list()
        for cmd in to_list(commands):
            if not isinstance(cmd, Mapping):
                cmd = {"command": cmd}
            output = cmd.pop("output", None)
            if output:
                raise ValueError(
                    f"'output' value {output} is not supported for run_commands"
                )

            try:
                out = self.send_command(**cmd)
            except AnsibleConnectionFailure as e:
                if check_rc:
                    raise
                out = getattr(e, "err", to_text(e))

            responses.append(out)

        return responses

    @configure_mode
    def run_configs(self, commands=None, check_rc=True) -> list:
        return self.run_commands(commands=commands, check_rc=check_rc)

    @configure_mode
    def edit_config(
        self, candidate=None, commit=True, replace=None, diff=False, comment=None
    ):
        resp = {}
        operations = self.get_device_operations()
        self.check_edit_config_capability(
            operations, candidate, commit, replace, comment
        )

        results = []
        requests = []
        if commit:
            self.send_command("configure")
            for line in to_list(candidate):
                if not isinstance(line, Mapping):
                    line = {"command": line}

                cmd = line["command"]
                if cmd != "exit":
                    results.append(self.send_command(**line))
                    requests.append(cmd)

            self.send_command("configure")
            self.send_command("exit")

        else:
            raise ValueError("check mode is not supported")

        resp["request"] = requests
        resp["response"] = results
        return resp

    def get_default_flag(self):
        self.send_command("configure")
        out = self.get("show running-config ?")
        out = to_text(out, errors="surrogate_then_replace")

        commands = set()
        for line in out.splitlines():
            if line.strip():
                commands.add(line.strip().split()[0])
        if "all" in commands:
            return "all"
        else:
            return "full"
