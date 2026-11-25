#
# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


"""Unit tests of the ix_command module."""

from textwrap import dedent
from unittest.mock import patch

from ansible_collections.rucdev.ix.plugins.modules import ix_command
from ansible_collections.rucdev.ix.tests.unit.modules.utils import set_module_args

from .ix_module import TestIxModule

# The module runs the commands once, then once more for each retry.
RETRIES = 1

SHOW_VERSION = dedent("""\
    NEC Portable Internetwork Core Operating System Software
    IX Series IX2215 (magellan-sec) Software, Version 10.11.18, RELEASE SOFTWARE
    Compiled Jul 29-Wed-2026 13:36:09 JST #2 by sw-build, coregen-10.11(18)
    """)


class TestIxCommandModule(TestIxModule):
    """Unit tests of the ix_command module."""

    module = ix_command

    def setUp(self) -> None:
        """Patch run_commands."""
        super().setUp()

        self.mock_run_commands = patch(
            "ansible_collections.rucdev.ix.plugins.modules.ix_command.run_commands",
        )
        self.run_commands = self.mock_run_commands.start()

    def tearDown(self) -> None:
        """Stop the patches."""
        super().tearDown()
        self.mock_run_commands.stop()

    def load_fixtures(self, _commands=None) -> None:
        """Return show version from run_commands."""
        self.run_commands.return_value = [SHOW_VERSION]

    def test_ix_command_wait_for(self) -> None:
        """wait_for that matches the output succeeds on the first run."""
        set_module_args(
            {"commands": ["show version"], "wait_for": ["result[0] contains IX2215"]},
        )
        result = self.execute_module(changed=False)
        assert result["stdout"] == [SHOW_VERSION]
        assert self.run_commands.call_count == 1

    def test_ix_command_wait_for_fails(self) -> None:
        """wait_for that never matches fails after the retries."""
        set_module_args(
            {
                "commands": ["show version"],
                "wait_for": ["result[0] contains IX3315"],
                "retries": RETRIES,
            },
        )
        result = self.execute_module(failed=True)
        assert (
            result["msg"]
            == "One or more conditional statements have not been satisfied"
        )
        assert result["failed_conditions"] == ["result[0] contains IX3315"]
        assert self.run_commands.call_count == RETRIES + 1

    def test_ix_command_waitfor(self) -> None:
        # waitfor is an alias of wait_for, as in other *_command modules
        """The waitfor alias works like wait_for."""
        set_module_args(
            {"commands": ["show version"], "waitfor": ["result[0] contains IX2215"]},
        )
        result = self.execute_module(changed=False)
        assert result["stdout"] == [SHOW_VERSION]
        assert self.run_commands.call_count == 1

    def test_ix_command_waitfor_fails(self) -> None:
        """The waitfor alias fails like wait_for when it never matches."""
        set_module_args(
            {
                "commands": ["show version"],
                "waitfor": ["result[0] contains IX3315"],
                "retries": RETRIES,
            },
        )
        result = self.execute_module(failed=True)
        assert (
            result["msg"]
            == "One or more conditional statements have not been satisfied"
        )
        assert result["failed_conditions"] == ["result[0] contains IX3315"]
        assert self.run_commands.call_count == RETRIES + 1
