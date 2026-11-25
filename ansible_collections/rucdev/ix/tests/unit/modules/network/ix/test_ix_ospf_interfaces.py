#
# Copyright 2025 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


"""Unit tests of the ix_ospf_interfaces module."""

from textwrap import dedent
from typing import NoReturn
from unittest.mock import patch

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.parameters import remove_values

from ansible_collections.rucdev.ix.plugins.modules import ix_ospf_interfaces
from ansible_collections.rucdev.ix.tests.unit.modules.utils import (
    AnsibleExitJsonError,
    set_module_args,
)

from .ix_module import TestIxModule


def exit_json_no_log(module, **kwargs) -> NoReturn:
    # Hide the no_log values like the real AnsibleModule.exit_json does.
    """Raise AnsibleExitJsonError with the no_log values hidden, as exit_json does."""
    kwargs.setdefault("changed", False)
    raise AnsibleExitJsonError(remove_values(kwargs, module.no_log_values))


class TestIxOspfInterfacesModule(TestIxModule):
    """Unit tests of the ix_ospf_interfaces module."""

    module = ix_ospf_interfaces

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
            "ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.ospf_interfaces.ospf_interfaces."
            "OspfInterfacesFacts.get_ospf_interfaces_data",
        )
        self.execute_show_command = self.mock_execute_show_command.start()
        self.maxDiff = None

    def tearDown(self) -> None:
        """Stop the patches."""
        super().tearDown()
        self.mock_get_resource_connection_facts.stop()
        self.mock_execute_show_command.stop()

    def test_ix_ospf_interfaces_merged(self) -> None:
        """Merged adds the OSPF interface settings."""
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet0.0
             ip ospf priority 20
             ip ospf cost 100
             ip ospf network point-to-point
            interface GigaEthernet1.0
             ipv6 ospf priority 60
            """)
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet0.0",
                        "address_family": [
                            {
                                "afi": "ipv4",
                                "mtu_ignore": True,
                                "priority": 40,
                            },
                        ],
                    },
                    {
                        "name": "GigaEthernet1.0",
                        "address_family": [
                            {
                                "afi": "ipv6",
                                "priority": 80,
                            },
                        ],
                    },
                ],
                "state": "merged",
            },
        )
        commands = [
            "interface GigaEthernet0.0",
            "ip ospf mtu-ignore",
            "ip ospf priority 40",
            "interface GigaEthernet1.0",
            "ipv6 ospf priority 80",
        ]
        result = self.execute_module(changed=True)
        assert sorted(result["commands"]) == sorted(commands)

    def test_ix_ospf_interfaces_merged_idempotent(self) -> None:
        """Merged with the current settings changes nothing."""
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet0.0
             ip ospf priority 20
             ip ospf mtu-ignore
            interface GigaEthernet1.0
             ipv6 ospf priority 60
            """)
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet0.0",
                        "address_family": [
                            {
                                "afi": "ipv4",
                                "priority": 20,
                                "mtu_ignore": True,
                            },
                        ],
                    },
                    {
                        "name": "GigaEthernet1.0",
                        "address_family": [
                            {
                                "afi": "ipv6",
                                "priority": 60,
                            },
                        ],
                    },
                ],
                "state": "merged",
            },
        )
        self.execute_module(changed=False, commands=[])

    def test_ix_ospf_interfaces_replaced(self) -> None:
        """Replaced sets the interface settings and removes the others."""
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet0.0
             ip ospf priority 20
             ip ospf network point-to-point
             ip ospf cost 100
            interface GigaEthernet1.0
             ipv6 ospf priority 60
            """)
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet0.0",
                        "address_family": [
                            {
                                "afi": "ipv4",
                                "priority": 30,
                                "cost": 200,
                            },
                        ],
                    },
                ],
                "state": "replaced",
            },
        )
        commands = [
            "interface GigaEthernet0.0",
            "no ip ospf network point-to-point",
            "ip ospf priority 30",
            "ip ospf cost 200",
        ]
        result = self.execute_module(changed=True)
        assert sorted(result["commands"]) == sorted(commands)

    def test_ix_ospf_interfaces_ipv4_only_options_under_ipv6(self) -> None:
        # IX has no "ipv6 ospf" form of these; they used to render "ip ospf ..."
        """Each IPv4-only option under afi ipv6 is rejected."""
        for option, value in (
            ("authentication_type", "message-digest"),
            ("authentication_key", "secret01"),
            ("message_digest_key", {"key_id": 1, "password": "secret01"}),
            ("mtu_ignore", True),
            ("mtu_ignore", False),
            ("interface_type", "point-to-point"),
        ):
            with self.subTest(option=option, value=value):
                af = {"afi": "ipv6", "cost": 10}
                af[option] = value
                set_module_args(
                    {
                        "config": [{"name": "GigaEthernet1.0", "address_family": [af]}],
                        "state": "rendered",
                    },
                )
                result = self.execute_module(failed=True)
                assert option in result["msg"]
                assert "GigaEthernet1.0" in result["msg"]

    def test_ix_ospf_interfaces_ipv4_only_options_without_afi(self) -> None:
        # without afi these used to be silently ignored
        """Each IPv4-only option without afi is rejected."""
        for option, value in (
            ("authentication_type", "message-digest"),
            ("authentication_key", "secret01"),
            ("message_digest_key", {"key_id": 1, "password": "secret01"}),
            ("mtu_ignore", True),
            ("interface_type", "point-to-point"),
        ):
            with self.subTest(option=option, value=value):
                af = {"cost": 10}
                af[option] = value
                set_module_args(
                    {
                        "config": [{"name": "GigaEthernet1.0", "address_family": [af]}],
                        "state": "rendered",
                    },
                )
                result = self.execute_module(failed=True)
                assert option in result["msg"]
                assert "afi: not set" in result["msg"]

    def test_ix_ospf_interfaces_ipv4_only_options_under_ipv6_merged(self) -> None:
        """Several IPv4-only options under afi ipv6 are rejected together."""
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet1.0
              ipv6 ospf cost 20
            !
            """)
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet1.0",
                        "address_family": [
                            {
                                "afi": "ipv6",
                                "mtu_ignore": True,
                                "interface_type": "point-to-point",
                                "authentication_key": "secret01",
                            },
                        ],
                    },
                ],
                "state": "merged",
            },
        )
        result = self.execute_module(failed=True)
        assert "authentication_key, mtu_ignore, interface_type" in result["msg"]

    def test_ix_ospf_interfaces_ipv6_common_options(self) -> None:
        # options with an "ipv6 ospf" form are still accepted under ipv6
        """Options that have an ipv6 ospf form are accepted under afi ipv6."""
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet1.0",
                        "address_family": [
                            {
                                "afi": "ipv6",
                                "cost": 10,
                                "hello_interval": 5,
                                "priority": 0,
                            },
                        ],
                    },
                ],
                "state": "rendered",
            },
        )
        result = self.execute_module(changed=False)
        assert sorted(result["rendered"]) == sorted(
            [
                "interface GigaEthernet1.0",
                "ipv6 ospf cost 10",
                "ipv6 ospf hello-interval 5",
                "ipv6 ospf priority 0",
            ],
        )

    def test_ix_ospf_interfaces_overridden(self) -> None:
        """Overridden removes the settings of the interfaces that are not given."""
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet0.0
             ip ospf priority 20
             ip ospf network point-to-point
            interface GigaEthernet1.0
             ipv6 ospf priority 60
             ipv6 ospf cost 150
            """)
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet0.0",
                        "address_family": [
                            {
                                "afi": "ipv4",
                                "priority": 50,
                                "hello_interval": 15,
                            },
                        ],
                    },
                ],
                "state": "overridden",
            },
        )
        commands = [
            "interface GigaEthernet0.0",
            "no ip ospf network point-to-point",
            "ip ospf priority 50",
            "ip ospf hello-interval 15",
            "interface GigaEthernet1.0",
            "no ipv6 ospf priority 60",
            "no ipv6 ospf cost 150",
        ]
        result = self.execute_module(changed=True)
        assert sorted(result["commands"]) == sorted(commands)

    def test_ix_ospf_interfaces_deleted(self) -> None:
        """Deleted removes the OSPF settings of the interface."""
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet0.0
             ip ospf priority 20
             ip ospf network point-to-point
             ip ospf cost 100
            interface GigaEthernet1.0
             ipv6 ospf priority 60
            """)
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet0.0",
                    },
                ],
                "state": "deleted",
            },
        )
        commands = [
            "interface GigaEthernet0.0",
            "no ip ospf priority 20",
            "no ip ospf network point-to-point",
            "no ip ospf cost 100",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_ix_ospf_interfaces_parsed(self) -> None:
        """Parsed reads the OSPF interface settings from running_config."""
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet0.0
             ip ospf priority 20
             ip ospf network point-to-point
            """)
        set_module_args(
            {
                "running_config": "interface GigaEthernet1.0\n ip ospf priority 30\n ip ospf cost 200\n ipv6 ospf priority 40\n",
                "state": "parsed",
            },
        )
        result = self.execute_module(changed=False)
        parsed_list = [
            {
                "name": "GigaEthernet1.0",
                "address_family": [
                    {
                        "afi": "ipv4",
                        "priority": 30,
                        "cost": 200,
                    },
                    {
                        "afi": "ipv6",
                        "priority": 40,
                    },
                ],
            },
        ]
        assert parsed_list == result["parsed"]

    def test_ix_ospf_interfaces_rendered(self) -> None:
        """Rendered returns the OSPF interface commands."""
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet0.0",
                        "address_family": [
                            {
                                "afi": "ipv4",
                                "priority": 10,
                                "cost": 100,
                                "hello_interval": 15,
                                "dead_interval": 60,
                                "mtu_ignore": True,
                                "interface_type": "point-to-point",
                                "authentication_type": "text",
                                "authentication_key": "mypassword",
                            },
                        ],
                    },
                    {
                        "name": "GigaEthernet1.0",
                        "address_family": [
                            {
                                "afi": "ipv6",
                                "priority": 20,
                                "cost": 200,
                                "hello_interval": 10,
                                "dead_interval": 40,
                            },
                        ],
                    },
                ],
                "state": "rendered",
            },
        )
        commands = [
            "interface GigaEthernet0.0",
            "ip ospf priority 10",
            "ip ospf cost 100",
            "ip ospf hello-interval 15",
            "ip ospf dead-interval 60",
            "ip ospf mtu-ignore",
            "ip ospf network point-to-point",
            "ip ospf authentication",
            "ip ospf authentication-key mypassword",
            "interface GigaEthernet1.0",
            "ipv6 ospf priority 20",
            "ipv6 ospf cost 200",
            "ipv6 ospf hello-interval 10",
            "ipv6 ospf dead-interval 40",
        ]
        result = self.execute_module(changed=False)
        assert sorted(result["rendered"]) == sorted(commands)

    # The running-config snippets below are as printed by an IX2215 (10.11.18).
    # IX stores the passwords in plain text, so they can be compared.

    def test_ix_ospf_interfaces_parsed_authentication(self) -> None:
        """Parsed reads the authentication type and the MD5 key."""
        set_module_args(
            {
                "running_config": dedent("""\
                    interface GigaEthernet1.0
                      no ip address
                      ip ospf authentication message-digest
                      ip ospf message-digest-key 1 md5pw001
                      shutdown
                    !
                    interface GigaEthernet2.0
                      no ip address
                      ip ospf authentication
                      ip ospf authentication-key txtpw001
                      shutdown
                    !
                    """),
                "state": "parsed",
            },
        )
        result = self.execute_module(changed=False)
        parsed_list = [
            {
                "name": "GigaEthernet1.0",
                "address_family": [
                    {
                        "afi": "ipv4",
                        "authentication_type": "message-digest",
                        "message_digest_key": {
                            "key_id": 1,
                            "password": "md5pw001",
                        },
                    },
                ],
            },
            {
                "name": "GigaEthernet2.0",
                "address_family": [
                    {
                        "afi": "ipv4",
                        "authentication_type": "text",
                        "authentication_key": "txtpw001",
                    },
                ],
            },
        ]
        assert parsed_list == result["parsed"]

    def test_ix_ospf_interfaces_gathered_authentication(self) -> None:
        """Gathered reads the authentication settings of the device."""
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet1.0
              no ip address
              ip ospf authentication message-digest
              ip ospf message-digest-key 1 md5pw001
              shutdown
            !
            """)
        set_module_args({"state": "gathered"})
        result = self.execute_module(changed=False)
        gathered = [
            {
                "name": "GigaEthernet1.0",
                "address_family": [
                    {
                        "afi": "ipv4",
                        "authentication_type": "message-digest",
                        "message_digest_key": {
                            "key_id": 1,
                            "password": "md5pw001",
                        },
                    },
                ],
            },
        ]
        assert gathered == result["gathered"]

    def test_ix_ospf_interfaces_rendered_authentication(self) -> None:
        """Rendered returns the authentication commands."""
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet1.0",
                        "address_family": [
                            {
                                "afi": "ipv4",
                                "authentication_type": "message-digest",
                                "message_digest_key": {
                                    "key_id": 1,
                                    "password": "md5pw001",
                                },
                            },
                        ],
                    },
                ],
                "state": "rendered",
            },
        )
        commands = [
            "interface GigaEthernet1.0",
            "ip ospf authentication message-digest",
            "ip ospf message-digest-key 1 md5pw001",
        ]
        result = self.execute_module(changed=False)
        assert sorted(result["rendered"]) == sorted(commands)

    def test_ix_ospf_interfaces_merged_authentication(self) -> None:
        """Merged adds the authentication type and the MD5 key."""
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet1.0
              no ip address
              shutdown
            !
            """)
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet1.0",
                        "address_family": [
                            {
                                "afi": "ipv4",
                                "authentication_type": "message-digest",
                                "message_digest_key": {
                                    "key_id": 1,
                                    "password": "md5pw001",
                                },
                            },
                        ],
                    },
                ],
                "state": "merged",
            },
        )
        commands = [
            "interface GigaEthernet1.0",
            "ip ospf authentication message-digest",
            "ip ospf message-digest-key 1 md5pw001",
        ]
        self.execute_module(changed=True, commands=commands, sort=False)

    def test_ix_ospf_interfaces_merged_authentication_idempotent(self) -> None:
        """Merged with the current authentication changes nothing."""
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet1.0
              no ip address
              ip ospf authentication message-digest
              ip ospf message-digest-key 1 md5pw001
              shutdown
            !
            """)
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet1.0",
                        "address_family": [
                            {
                                "afi": "ipv4",
                                "authentication_type": "message-digest",
                                "message_digest_key": {
                                    "key_id": 1,
                                    "password": "md5pw001",
                                },
                            },
                        ],
                    },
                ],
                "state": "merged",
            },
        )
        self.execute_module(changed=False, commands=[])

    def test_ix_ospf_interfaces_merged_authentication_key_change(self) -> None:
        # IX keeps one key per interface: a new KEY_ID replaces the old key.
        """Merged replaces the MD5 key with a new one."""
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet1.0
              no ip address
              ip ospf authentication message-digest
              ip ospf message-digest-key 2 md5pw002
              shutdown
            !
            """)
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet1.0",
                        "address_family": [
                            {
                                "afi": "ipv4",
                                "message_digest_key": {
                                    "key_id": 1,
                                    "password": "md5pw001",
                                },
                            },
                        ],
                    },
                ],
                "state": "merged",
            },
        )
        commands = [
            "interface GigaEthernet1.0",
            "ip ospf message-digest-key 1 md5pw001",
        ]
        self.execute_module(changed=True, commands=commands, sort=False)

    def test_ix_ospf_interfaces_replaced_authentication(self) -> None:
        """Replaced removes the authentication that is not given."""
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet1.0
              no ip address
              ip ospf authentication message-digest
              ip ospf message-digest-key 1 md5pw001
              ip ospf cost 10
              shutdown
            !
            """)
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet1.0",
                        "address_family": [
                            {
                                "afi": "ipv4",
                                "cost": 10,
                            },
                        ],
                    },
                ],
                "state": "replaced",
            },
        )
        commands = [
            "interface GigaEthernet1.0",
            "no ip ospf authentication message-digest",
            "no ip ospf message-digest-key 1 md5pw001",
        ]
        self.execute_module(changed=True, commands=commands, sort=False)

    def test_ix_ospf_interfaces_replaced_text_authentication(self) -> None:
        # IX keeps an MD5 key next to text authentication; both must go.
        """Replaced sets text authentication."""
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet1.0
              no ip address
              ip ospf authentication
              ip ospf authentication-key txtpw001
              ip ospf message-digest-key 1 md5pw001
              shutdown
            !
            """)
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet1.0",
                        "address_family": [
                            {
                                "afi": "ipv4",
                                "cost": 10,
                            },
                        ],
                    },
                ],
                "state": "replaced",
            },
        )
        commands = [
            "interface GigaEthernet1.0",
            "no ip ospf authentication",
            "no ip ospf authentication-key txtpw001",
            "ip ospf cost 10",
            "no ip ospf message-digest-key 1 md5pw001",
        ]
        self.execute_module(changed=True, commands=commands, sort=False)

    def test_ix_ospf_interfaces_replaced_md5_to_text_authentication(self) -> None:
        # "ip ospf authentication" replaces "ip ospf authentication message-digest".
        """Replaced changes MD5 authentication to text authentication."""
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet1.0
              no ip address
              ip ospf authentication message-digest
              ip ospf message-digest-key 1 md5pw001
              shutdown
            !
            """)
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet1.0",
                        "address_family": [
                            {
                                "afi": "ipv4",
                                "authentication_type": "text",
                                "authentication_key": "txtpw001",
                            },
                        ],
                    },
                ],
                "state": "replaced",
            },
        )
        commands = [
            "interface GigaEthernet1.0",
            "ip ospf authentication",
            "ip ospf authentication-key txtpw001",
            "no ip ospf message-digest-key 1 md5pw001",
        ]
        self.execute_module(changed=True, commands=commands, sort=False)

    def test_ix_ospf_interfaces_overridden_authentication(self) -> None:
        """Overridden removes the authentication of the other interfaces."""
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet1.0
              no ip address
              ip ospf authentication message-digest
              ip ospf message-digest-key 1 md5pw001
              shutdown
            !
            interface GigaEthernet2.0
              no ip address
              ip ospf authentication
              ip ospf authentication-key txtpw001
              shutdown
            !
            """)
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet2.0",
                        "address_family": [
                            {
                                "afi": "ipv4",
                                "cost": 20,
                            },
                        ],
                    },
                ],
                "state": "overridden",
            },
        )
        commands = [
            "interface GigaEthernet1.0",
            "no ip ospf authentication message-digest",
            "no ip ospf message-digest-key 1 md5pw001",
            "interface GigaEthernet2.0",
            "no ip ospf authentication",
            "no ip ospf authentication-key txtpw001",
            "ip ospf cost 20",
        ]
        self.execute_module(changed=True, commands=commands, sort=False)

    def test_ix_ospf_interfaces_deleted_authentication(self) -> None:
        """Deleted removes the authentication settings."""
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet1.0
              no ip address
              ip ospf authentication message-digest
              ip ospf message-digest-key 1 md5pw001
              shutdown
            !
            interface GigaEthernet2.0
              no ip address
              ip ospf authentication
              ip ospf authentication-key txtpw001
              shutdown
            !
            """)
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet1.0",
                    },
                ],
                "state": "deleted",
            },
        )
        commands = [
            "interface GigaEthernet1.0",
            "no ip ospf authentication message-digest",
            "no ip ospf message-digest-key 1 md5pw001",
        ]
        self.execute_module(changed=True, commands=commands, sort=False)

    def test_ix_ospf_interfaces_gathered_authentication_no_log(self) -> None:
        # Only the password read from the device may be hidden in the result.
        """Gathered hides only the password, not the key ID or other values."""
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet1.0
              no ip address
              ip ospf authentication message-digest
              ip ospf message-digest-key 1 md5pw001
              ip ospf cost 10
              shutdown
            !
            """)
        set_module_args({"state": "gathered"})
        with patch.object(AnsibleModule, "exit_json", exit_json_no_log):
            result = self.execute_module(changed=False)
        gathered = [
            {
                "name": "GigaEthernet1.0",
                "address_family": [
                    {
                        "afi": "ipv4",
                        "authentication_type": "message-digest",
                        "cost": 10,
                        "message_digest_key": {
                            "key_id": 1,
                            "password": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
                        },
                    },
                ],
            },
        ]
        assert gathered == result["gathered"]

    def test_ix_ospf_interfaces_deleted_authentication_no_log(self) -> None:
        """Deleted hides only the password in the result."""
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet1.0
              no ip address
              ip ospf authentication message-digest
              ip ospf message-digest-key 1 md5pw001
              ip ospf cost 10
              shutdown
            !
            """)
        set_module_args(
            {
                "config": [
                    {
                        "name": "GigaEthernet1.0",
                    },
                ],
                "state": "deleted",
            },
        )
        commands = [
            "interface GigaEthernet1.0",
            "no ip ospf authentication message-digest",
            "no ip ospf cost 10",
            "no ip ospf message-digest-key 1 ********",
        ]
        with patch.object(AnsibleModule, "exit_json", exit_json_no_log):
            self.execute_module(changed=True, commands=commands, sort=False)
