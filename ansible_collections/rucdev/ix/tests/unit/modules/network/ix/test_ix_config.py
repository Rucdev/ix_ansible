#
# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


"""Unit tests of the ix_config module."""

from __future__ import annotations

from textwrap import dedent
from unittest.mock import ANY, MagicMock, patch

from ansible_collections.rucdev.ix.plugins.cliconf.ix import Cliconf
from ansible_collections.rucdev.ix.plugins.modules import ix_config
from ansible_collections.rucdev.ix.tests.unit.modules.utils import set_module_args

from .ix_module import TestIxModule

RUNNING_CONFIG = dedent("""\
    ! NEC Portable Internetwork Core Operating System Software
    !
    hostname Router1
    timezone +09 00
    !
    interface GigaEthernet0.0
      no ip address
      shutdown
    !
    """)


class TestIxConfigModule(TestIxModule):
    """Unit tests of the ix_config module."""

    module = ix_config

    def setUp(self) -> None:
        """Patch the connection, get_config and run_commands."""
        super().setUp()

        self.mock_get_config = patch(
            "ansible_collections.rucdev.ix.plugins.modules.ix_config.get_config",
        )
        self.get_config = self.mock_get_config.start()

        self.mock_get_connection = patch(
            "ansible_collections.rucdev.ix.plugins.modules.ix_config.get_connection",
        )
        self.get_connection = self.mock_get_connection.start()
        self.conn = self.get_connection()
        # Use the real cliconf diff so commands are computed as on a device.
        self.cliconf_obj = Cliconf(MagicMock())
        self.conn.get_diff.side_effect = self.cliconf_obj.get_diff

        self.mock_run_commands = patch(
            "ansible_collections.rucdev.ix.plugins.modules.ix_config.run_commands",
        )
        self.run_commands = self.mock_run_commands.start()

    def tearDown(self) -> None:
        """Stop the patches."""
        super().tearDown()
        self.mock_get_config.stop()
        self.mock_get_connection.stop()
        self.mock_run_commands.stop()

    def load_fixtures(self, _commands: list | None = None) -> None:
        """Return the running config from get_config and run_commands."""
        self.get_config.return_value = RUNNING_CONFIG
        self.run_commands.return_value = [RUNNING_CONFIG]

    def assert_str_warnings(self, result: dict) -> None:
        # ansible-core rejects any warning that is not a str.
        """Check that every warning is a str, as ansible-core requires."""
        for warning in result.get("warnings", []):
            assert isinstance(warning, str), result["warnings"]

    def test_ix_config_lines_diff(self) -> None:
        """With lines in diff mode, the missing line is sent."""
        set_module_args({"lines": ["hostname Router2"], "_ansible_diff": True})
        result = self.execute_module(changed=True, commands=["hostname Router2"])
        self.conn.edit_config.assert_called_once_with(candidate=["hostname Router2"])
        self.assert_str_warnings(result)

    def test_ix_config_lines_diff_check_mode(self) -> None:
        """With lines in diff and check mode, the line is reported but not sent."""
        set_module_args(
            {
                "lines": ["hostname Router2"],
                "_ansible_diff": True,
                "_ansible_check_mode": True,
            },
        )
        result = self.execute_module(changed=True, commands=["hostname Router2"])
        self.conn.edit_config.assert_not_called()
        self.assert_str_warnings(result)

    def test_ix_config_src_diff(self) -> None:
        """With src in diff mode, the missing line is sent."""
        set_module_args({"src": "hostname Router2\n", "_ansible_diff": True})
        result = self.execute_module(changed=True, commands=["hostname Router2"])
        self.conn.edit_config.assert_called_once_with(candidate=["hostname Router2"])
        self.assert_str_warnings(result)

    def test_ix_config_save_when_always_diff(self) -> None:
        """With save_when always, the config is saved in diff mode too."""
        set_module_args({"save_when": "always", "_ansible_diff": True})
        result = self.execute_module(changed=True)
        self.run_commands.assert_any_call(
            ANY,
            "copy running-config startup-config\r",
            configure=True,
        )
        self.assert_str_warnings(result)

    def test_ix_config_diff_against_intended(self) -> None:
        """With diff_against intended, the difference from intended_config is reported."""
        intended = RUNNING_CONFIG.replace("hostname Router1", "hostname Router9")
        set_module_args(
            {
                "diff_against": "intended",
                "intended_config": intended,
                "_ansible_diff": True,
            },
        )
        result = self.execute_module(changed=True)
        self.conn.edit_config.assert_not_called()
        assert "hostname Router1" in result["diff"]["before"]
        assert "hostname Router9" not in result["diff"]["before"]
        assert "hostname Router9" in result["diff"]["after"]
        self.assert_str_warnings(result)
