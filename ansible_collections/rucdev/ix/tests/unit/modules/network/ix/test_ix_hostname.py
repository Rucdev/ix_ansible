#
# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


"""Unit tests of the ix_hostname module."""

from textwrap import dedent
from unittest.mock import patch

from ansible_collections.rucdev.ix.plugins.modules import ix_hostname
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


class TestIxHostnameModule(TestIxModule):
    """Unit tests of the ix_hostname module."""

    module = ix_hostname

    def setUp(self) -> None:
        """Patch the connection and the function that returns the device config."""
        super().setUp()

        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base."
            "get_resource_connection",
        )
        self.get_resource_connection_facts = (
            self.mock_get_resource_connection_facts.start()
        )

        self.mock_execute_show_command = patch(
            "ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.hostname.hostname."
            "HostnameFacts.get_hostname_data",
        )
        self.execute_show_command = self.mock_execute_show_command.start()

    def tearDown(self) -> None:
        """Stop the patches."""
        super().tearDown()
        self.mock_get_resource_connection_facts.stop()
        self.mock_execute_show_command.stop()

    def test_ix_hostname_merged(self) -> None:
        """Merged sets a new hostname."""
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args({"config": {"hostname": "Router2"}, "state": "merged"})
        self.execute_module(changed=True, commands=["hostname Router2"])

    def test_ix_hostname_merged_from_empty(self) -> None:
        """Merged sets the hostname when none is configured."""
        self.execute_show_command.return_value = "timezone +09 00\n"
        set_module_args({"config": {"hostname": "Router2"}, "state": "merged"})
        self.execute_module(changed=True, commands=["hostname Router2"])

    def test_ix_hostname_merged_idempotent(self) -> None:
        """Merged with the current hostname changes nothing."""
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args({"config": {"hostname": "Router1"}, "state": "merged"})
        self.execute_module(changed=False, commands=[])

    def test_ix_hostname_replaced(self) -> None:
        """Replaced sets a new hostname."""
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args({"config": {"hostname": "Router2"}, "state": "replaced"})
        self.execute_module(changed=True, commands=["hostname Router2"])

    def test_ix_hostname_replaced_idempotent(self) -> None:
        """Replaced with the current hostname changes nothing."""
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args({"config": {"hostname": "Router1"}, "state": "replaced"})
        self.execute_module(changed=False, commands=[])

    def test_ix_hostname_overridden(self) -> None:
        """Overridden sets a new hostname."""
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args({"config": {"hostname": "Router2"}, "state": "overridden"})
        self.execute_module(changed=True, commands=["hostname Router2"])

    def test_ix_hostname_overridden_idempotent(self) -> None:
        """Overridden with the current hostname changes nothing."""
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args({"config": {"hostname": "Router1"}, "state": "overridden"})
        self.execute_module(changed=False, commands=[])

    def test_ix_hostname_deleted(self) -> None:
        """Deleted removes the hostname."""
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args({"state": "deleted"})
        self.execute_module(changed=True, commands=["no hostname"])

    def test_ix_hostname_deleted_idempotent(self) -> None:
        """Deleted without a hostname changes nothing."""
        self.execute_show_command.return_value = "timezone +09 00\n"
        set_module_args({"state": "deleted"})
        self.execute_module(changed=False, commands=[])

    def test_ix_hostname_rendered(self) -> None:
        """Rendered returns the hostname command."""
        set_module_args({"config": {"hostname": "Router1"}, "state": "rendered"})
        result = self.execute_module(changed=False)
        assert result["rendered"] == ["hostname Router1"]

    def test_ix_hostname_parsed(self) -> None:
        """Parsed reads the hostname from running_config."""
        set_module_args({"running_config": RUNNING_CONFIG, "state": "parsed"})
        result = self.execute_module(changed=False)
        assert result["parsed"] == {"hostname": "Router1"}

    def test_ix_hostname_parsed_ignores_indented_lines(self) -> None:
        """Parsed ignores an indented hostname line, which belongs to another block."""
        set_module_args({"running_config": " hostname NotThis\n", "state": "parsed"})
        result = self.execute_module(changed=False)
        assert result["parsed"] == {}

    def test_ix_hostname_gathered(self) -> None:
        """Gathered reads the hostname of the device."""
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args({"state": "gathered"})
        result = self.execute_module(changed=False)
        assert result["gathered"] == {"hostname": "Router1"}

    def test_ix_hostname_rejects_whitespace(self) -> None:
        # IX silently truncates "hostname lab ix" to "lab" (verified on IX2215)
        """A hostname with whitespace is rejected."""
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args({"config": {"hostname": "lab ix"}, "state": "merged"})
        result = self.execute_module(failed=True)
        assert "without whitespace" in result["msg"]

    def test_ix_hostname_rendered_rejects_whitespace(self) -> None:
        """Rendered also rejects a hostname with whitespace."""
        set_module_args({"config": {"hostname": "lab ix"}, "state": "rendered"})
        self.execute_module(failed=True)
