#
# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from textwrap import dedent
from unittest.mock import patch

from ansible_collections.rucdev.ix.plugins.modules import ix_command
from ansible_collections.rucdev.ix.tests.unit.modules.utils import set_module_args

from .ix_module import TestIxModule

SHOW_VERSION = dedent("""\
    NEC Portable Internetwork Core Operating System Software
    IX Series IX2215 (magellan-sec) Software, Version 10.11.18, RELEASE SOFTWARE
    Compiled Jul 29-Wed-2026 13:36:09 JST #2 by sw-build, coregen-10.11(18)
    """)


class TestIxCommandModule(TestIxModule):
    module = ix_command

    def setUp(self):
        super().setUp()

        self.mock_run_commands = patch(
            "ansible_collections.rucdev.ix.plugins.modules.ix_command.run_commands",
        )
        self.run_commands = self.mock_run_commands.start()

    def tearDown(self):
        super().tearDown()
        self.mock_run_commands.stop()

    def load_fixtures(self, commands=None):
        self.run_commands.return_value = [SHOW_VERSION]

    def test_ix_command_wait_for(self):
        set_module_args(
            dict(commands=["show version"], wait_for=["result[0] contains IX2215"]),
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["stdout"], [SHOW_VERSION])
        self.assertEqual(self.run_commands.call_count, 1)

    def test_ix_command_wait_for_fails(self):
        set_module_args(
            dict(
                commands=["show version"],
                wait_for=["result[0] contains IX3315"],
                retries=1,
            ),
        )
        result = self.execute_module(failed=True)
        self.assertEqual(
            result["msg"],
            "One or more conditional statements have not been satisfied",
        )
        self.assertEqual(result["failed_conditions"], ["result[0] contains IX3315"])
        self.assertEqual(self.run_commands.call_count, 2)

    def test_ix_command_waitfor(self):
        # waitfor is an alias of wait_for, as in other *_command modules
        set_module_args(
            dict(commands=["show version"], waitfor=["result[0] contains IX2215"]),
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["stdout"], [SHOW_VERSION])
        self.assertEqual(self.run_commands.call_count, 1)

    def test_ix_command_waitfor_fails(self):
        set_module_args(
            dict(
                commands=["show version"],
                waitfor=["result[0] contains IX3315"],
                retries=1,
            ),
        )
        result = self.execute_module(failed=True)
        self.assertEqual(
            result["msg"],
            "One or more conditional statements have not been satisfied",
        )
        self.assertEqual(result["failed_conditions"], ["result[0] contains IX3315"])
        self.assertEqual(self.run_commands.call_count, 2)
