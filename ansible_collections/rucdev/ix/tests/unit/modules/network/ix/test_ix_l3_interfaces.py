# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests of the ix_l3_interfaces module."""

from __future__ import annotations

from textwrap import dedent
from unittest.mock import patch

from ansible_collections.rucdev.ix.plugins.modules import ix_l3_interfaces
from ansible_collections.rucdev.ix.tests.unit.modules.utils import set_module_args

from .ix_module import TestIxModule

RUNNING_CONFIG = dedent("""\
    interface GigaEthernet1.0
      ip address 192.0.2.1/24
      ipv6 address 2001:db8::1/64
    !
    """)


class TestIxL3InterfacesModule(TestIxModule):
    """Unit tests of the ix_l3_interfaces module."""

    module = ix_l3_interfaces

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
            "ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.l3_interfaces.l3_interfaces."
            "L3InterfacesFacts.get_l3_interfaces_data",
        )
        self.execute_show_command = self.mock_execute_show_command.start()

    def tearDown(self) -> None:
        """Stop the patches."""
        super().tearDown()
        self.mock_get_resource_connection_facts.stop()
        self.mock_execute_show_command.stop()

    def test_ix_l3_interfaces_rendered_valid_addresses(self) -> None:
        """Rendered gives the commands for valid IPv4 and IPv6 addresses."""
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet1.0",
                        "ipv4": [{"address": "198.51.100.1/24"}],
                        "ipv6": [{"address": "2001:db8:1::1/64"}],
                    },
                ],
                "state": "rendered",
            },
        )
        result = self.execute_module(changed=False)
        assert sorted(result["rendered"]) == [
            "interface GigaEthernet1.0",
            "ip address 198.51.100.1/24",
            "ipv6 address 2001:db8:1::1/64",
        ]

    def test_ix_l3_interfaces_invalid_addresses(self) -> None:
        """Each invalid address fails with a message that names the problem."""
        for afi, address, message in (
            ("ipv4", "192.0.2.1", "address format is <ipv4 address>/<mask>"),
            ("ipv4", "192.0.2.1/33", "mask should be in range 0-32"),
            ("ipv4", "192.0.2.1/abc", "invalid value for mask: abc"),
            ("ipv4", "not-an-ip/24", "address should be an IPv4 address"),
            ("ipv4", "2001:db8::1/24", "address should be an IPv4 address"),
            ("ipv6", "2001:db8::1", "address format is <ipv6 address>/<mask>"),
            ("ipv6", "2001:db8::1/129", "mask should be in range 0-128"),
            ("ipv6", "2001:db8::1/abc", "invalid value for mask: abc"),
            ("ipv6", "zzzz/64", "address should be an IPv6 address"),
            ("ipv6", "192.0.2.1/64", "address should be an IPv6 address"),
        ):
            with self.subTest(afi=afi, address=address):
                set_module_args(
                    {
                        "config": [
                            {"name": "GigaEthernet1.0", afi: [{"address": address}]},
                        ],
                        "state": "rendered",
                    },
                )
                result = self.execute_module(failed=True)
                assert message in result["msg"]

    def test_ix_l3_interfaces_merged_invalid_address(self) -> None:
        """Merged rejects an invalid address before it sends any command."""
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args(
            {
                "config": [
                    {"name": "GigaEthernet1.0", "ipv6": [{"address": "zzzz/64"}]},
                ],
                "state": "merged",
            },
        )
        result = self.execute_module(failed=True)
        assert "address should be an IPv6 address" in result["msg"]

    def test_ix_l3_interfaces_merged_idempotent(self) -> None:
        """Merged with the addresses that the device has changes nothing."""
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet1.0",
                        "ipv4": [{"address": "192.0.2.1/24"}],
                        "ipv6": [{"address": "2001:db8::1/64"}],
                    },
                ],
                "state": "merged",
            },
        )
        self.execute_module(changed=False, commands=[])
