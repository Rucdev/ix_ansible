# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests of the ix cliconf plugin."""

from __future__ import annotations

import json

from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_text

from ansible_collections.rucdev.ix.plugins.cliconf import ix

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "ix"


def _connection_side_effect(*args: bytes, **kwargs: bytes) -> bytes | str:
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
        """Create the plugin on a mocked connection that answers from fixture files."""
        self._mock_connection = MagicMock()
        self._mock_connection.send.side_effect = _connection_side_effect
        self._cliconf = ix.Cliconf(self._mock_connection)
        self.maxDiff = None

    def tearDown(self) -> None:
        """Nothing to clean up."""

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
    """Session mode handling (#24).

    Every task starts in exec mode, and the config-only show commands enter
    config mode on their own.
    """

    # show commands that IX rejects in exec mode (IX2215 10.11.18)
    CONFIG_ONLY_SHOW = (
        "show running-config",
        "show startup-config",
        "show ip ospf neighbor",
        "show logging",
    )

    def setUp(self) -> None:
        """Create the plugin on a mocked connection that records the commands sent."""
        self._conn = MagicMock()
        self._conn.connected = True
        self._prompt = b"ix2215# "
        self._conn.get_prompt.side_effect = lambda: self._prompt
        self._sent = []

        def send(command: bytes, *_args: object, **_kwargs: object) -> bytes:
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
            exec_mode = not self._prompt.endswith(b")# ")
            if (cmd in self.CONFIG_ONLY_SHOW and exec_mode) or "bogus" in cmd:
                # what network_cli raises for "% ...  -- Invalid command."
                raise AnsibleConnectionFailure(
                    repr(
                        "{0}\r\n% {1}  -- Invalid command.\r\n{2}".format(
                            cmd, cmd.split()[-1], self._prompt.decode()
                        ).encode()
                    )
                )
            return b""

        self._conn.send.side_effect = send
        self._cliconf = ix.Cliconf(self._conn)

    def test_set_cli_prompt_context_from_config(self) -> None:
        """In config mode, set_cli_prompt_context leaves to exec mode."""
        self._prompt = b"ix2215(config)# "
        self._cliconf.set_cli_prompt_context()
        assert self._sent == ["configure", "exit"]
        assert self._prompt == b"ix2215# "

    def test_set_cli_prompt_context_from_sub_mode(self) -> None:
        """In a sub mode of config, set_cli_prompt_context leaves to exec mode."""
        self._prompt = b"ix2215(config-ospfv2-1)# "
        self._cliconf.set_cli_prompt_context()
        assert self._sent == ["configure", "exit"]
        assert self._prompt == b"ix2215# "

    def test_set_cli_prompt_context_already_exec(self) -> None:
        """In exec mode, set_cli_prompt_context sends nothing."""
        self._cliconf.set_cli_prompt_context()
        assert self._sent == []

    def test_set_cli_prompt_context_not_connected(self) -> None:
        """Without a connection, set_cli_prompt_context sends nothing."""
        self._conn.connected = False
        self._prompt = b"ix2215(config)# "
        self._cliconf.set_cli_prompt_context()
        assert self._sent == []

    def test_run_commands_show_running_config_from_exec(self) -> None:
        """From exec mode, show running-config enters config mode first."""
        self._cliconf.run_commands(["show running-config"])
        assert self._sent == ["configure", "show running-config"]

    def test_run_commands_show_startup_config_from_exec(self) -> None:
        """From exec mode, show startup-config enters config mode first."""
        self._cliconf.run_commands(["show startup-config"])
        assert self._sent == ["configure", "show startup-config"]

    def test_run_commands_show_running_config_in_config(self) -> None:
        """In config mode, show running-config is sent as it is."""
        self._prompt = b"ix2215(config)# "
        self._cliconf.run_commands(["show running-config"])
        assert self._sent == ["show running-config"]

    def test_run_commands_other_commands_stay_in_exec(self) -> None:
        """Other show commands run in exec mode."""
        self._cliconf.run_commands(["show version", "show ip route"])
        assert self._sent == ["show version", "show ip route"]
        assert self._prompt == b"ix2215# "

    def test_run_commands_config_only_show_retried_in_config(self):
        self._cliconf.run_commands(["show ip ospf neighbor", "show logging"])
        self.assertEqual(
            self._sent,
            [
                "show ip ospf neighbor",
                "configure",
                "show ip ospf neighbor",
                "show logging",
            ],
        )

    def test_run_commands_exec_show_not_retried(self):
        self._cliconf.run_commands(["show ip route", "show ip ospf neighbor"])
        self.assertEqual(
            self._sent,
            [
                "show ip route",
                "show ip ospf neighbor",
                "configure",
                "show ip ospf neighbor",
            ],
        )

    def test_run_commands_invalid_show_still_fails(self):
        with self.assertRaises(AnsibleConnectionFailure):
            self._cliconf.run_commands(["show bogus"])
        self.assertEqual(self._sent, ["show bogus", "configure", "show bogus"])

    def test_run_commands_invalid_show_check_rc_false(self):
        out = self._cliconf.run_commands(["show bogus"], check_rc=False)
        self.assertIn("Invalid command", out[0])

    def test_run_commands_non_show_not_retried(self):
        with self.assertRaises(AnsibleConnectionFailure):
            self._cliconf.run_commands(["clear bogus"])
        self.assertEqual(self._sent, ["clear bogus"])

    def test_run_commands_invalid_in_config_not_retried(self):
        self._prompt = b"ix2215(config)# "
        with self.assertRaises(AnsibleConnectionFailure):
            self._cliconf.run_commands(["show bogus"])
        self.assertEqual(self._sent, ["show bogus"])

    def test_get_config_only_show_retried_in_config(self):
        """get() is what ansible.netcommon.cli_command uses."""
        self._cliconf.get(command="show ip ospf neighbor")
        self.assertEqual(
            self._sent,
            ["show ip ospf neighbor", "configure", "show ip ospf neighbor"],
        )

    def test_get_show_running_config_from_exec(self):
        self._cliconf.get(command="show running-config")
        self.assertEqual(self._sent, ["configure", "show running-config"])

    def test_edit_config_then_task_start_is_exec(self) -> None:
        """After edit_config the session is back in exec mode.

        Like 'end' in cisco.ios; show running-config in the next task still
        works.
        """
        self._cliconf.edit_config(candidate=["hostname lab"])
        assert self._prompt == b"ix2215# "
        self._sent.clear()
        self._cliconf.set_cli_prompt_context()
        self._cliconf.run_commands(["show running-config"])
        assert self._sent == ["configure", "show running-config"]

    def test_get_device_info_leaves_exec_mode(self) -> None:
        """get_device_info returns to exec mode after leaving config mode."""
        self._cliconf.get_device_info()
        assert self._sent[-2:] == ["configure", "exit"]
        assert self._prompt == b"ix2215# "
