# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock

from ansible.module_utils._text import to_text

from ansible_collections.rucdev.ix.plugins.cliconf import ix

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "ix"


def _connection_side_effect(*args, **kwargs):
    try:
        value = args[0] if args else kwargs.get("command")

        name = to_text(b"_".join(value.split(b" ")), errors="surrogate_or_strict")
        return (FIXTURE_DIR / name).read_bytes()
    except OSError:
        if args:
            return args[0]
        if kwargs.get("command"):
            return kwargs.get("command")

        return "Nope"


class TestPluginCLIConfIOS(TestCase):
    """Test class for IX CLI Conf Methods."""

    def setUp(self) -> None:
        self._mock_connection = MagicMock()
        self._mock_connection.send.side_effect = _connection_side_effect
        self._cliconf = ix.Cliconf(self._mock_connection)
        self.maxDiff = None

    def tearDown(self) -> None:
        pass

    def test_get_device_info(self) -> None:
        """Test get_device_info."""
        device_info = self._cliconf.get_device_info()

        mock_device_info = {
            "network_os": "ix",
            "network_os_model": "IX2105",
            "network_os_version": "10.2.39",
            "network_os_image": "ix2105-ms-10.2.39.ldc",
        }

        assert device_info == mock_device_info

    def test_get_capabilities(self) -> None:
        """Test get_capabilities."""
        capabilities = json.loads(self._cliconf.get_capabilities())
        mock_capabilities = {
            "device_info": {
                "network_os": "ix",
                "network_os_model": "IX2105",
                "network_os_version": "10.2.39",
                "network_os_hostname": "ix-dev",
                "network_os_image": "bootflash:packages.conf",
            },
            "device_operations": {
                "supports_commit": False,
                "supports_commit_comment": False,
                "supports_defaults": True,
                "supports_diff_ignore_lines": True,
                "supports_diff_match": True,
                "supports_diff_replace": True,
                "supports_generate_diff": True,
                "supports_multiline_delimiter": True,
                "supports_onbox_diff": False,
                "supports_replace": False,
                "supports_rollback": False,
            },
            "diff_match": ["line", "strict", "exact", "none"],
            "diff_replace": ["line", "block"],
            "format": ["text"],
            "network_api": "cliconf",
            "output": [],
            "rpc": [
                "edit_config",
                "enable_response_logging",
                "get",
                "get_capabilities",
                "get_config",
                "disable_response_logging",
                "run_commands",
                "edit_banner",
                "get_diff",
                "run_commands",
                "get_defaults_flag",
            ],
        }
        assert sorted(mock_capabilities) == sorted(capabilities)


class TestCliconfModeHandling(TestCase):
    """Session mode handling (#24): every task starts in exec mode, and the
    config-only show commands enter config mode on their own.
    """

    def setUp(self) -> None:
        self._conn = MagicMock()
        self._conn.connected = True
        self._prompt = b"ix2215# "
        self._conn.get_prompt.side_effect = lambda: self._prompt
        self._sent = []

        def send(command, *_args, **_kwargs) -> bytes:
            cmd = command.decode() if isinstance(command, bytes) else command
            self._sent.append(cmd)
            # emulate IX prompt transitions
            if cmd == "configure":
                self._prompt = b"ix2215(config)# "
            elif cmd == "exit":
                if b"(config-" in self._prompt:
                    self._prompt = b"ix2215(config)# "
                else:
                    self._prompt = b"ix2215# "
            elif cmd.startswith("ip router ospf"):
                self._prompt = b"ix2215(config-ospfv2-1)# "
            return b""

        self._conn.send.side_effect = send
        self._cliconf = ix.Cliconf(self._conn)

    def test_set_cli_prompt_context_from_config(self) -> None:
        self._prompt = b"ix2215(config)# "
        self._cliconf.set_cli_prompt_context()
        assert self._sent == ["configure", "exit"]
        assert self._prompt == b"ix2215# "

    def test_set_cli_prompt_context_from_sub_mode(self) -> None:
        self._prompt = b"ix2215(config-ospfv2-1)# "
        self._cliconf.set_cli_prompt_context()
        assert self._sent == ["configure", "exit"]
        assert self._prompt == b"ix2215# "

    def test_set_cli_prompt_context_already_exec(self) -> None:
        self._cliconf.set_cli_prompt_context()
        assert self._sent == []

    def test_set_cli_prompt_context_not_connected(self) -> None:
        self._conn.connected = False
        self._prompt = b"ix2215(config)# "
        self._cliconf.set_cli_prompt_context()
        assert self._sent == []

    def test_run_commands_show_running_config_from_exec(self) -> None:
        self._cliconf.run_commands(["show running-config"])
        assert self._sent == ["configure", "show running-config"]

    def test_run_commands_show_startup_config_from_exec(self) -> None:
        self._cliconf.run_commands(["show startup-config"])
        assert self._sent == ["configure", "show startup-config"]

    def test_run_commands_show_running_config_in_config(self) -> None:
        self._prompt = b"ix2215(config)# "
        self._cliconf.run_commands(["show running-config"])
        assert self._sent == ["show running-config"]

    def test_run_commands_other_commands_stay_in_exec(self) -> None:
        self._cliconf.run_commands(["show version", "show ip route"])
        assert self._sent == ["show version", "show ip route"]
        assert self._prompt == b"ix2215# "

    def test_edit_config_then_task_start_is_exec(self) -> None:
        """edit_config leaves exec mode (like cisco.ios 'end'); the next
        task's show running-config still works.
        """
        self._cliconf.edit_config(candidate=["hostname lab"])
        assert self._prompt == b"ix2215# "
        self._sent.clear()
        self._cliconf.set_cli_prompt_context()
        self._cliconf.run_commands(["show running-config"])
        assert self._sent == ["configure", "show running-config"]

    def test_get_device_info_leaves_exec_mode(self) -> None:
        self._cliconf.get_device_info()
        assert self._sent[-2:] == ["configure", "exit"]
        assert self._prompt == b"ix2215# "
