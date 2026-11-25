#
# -*- coding: utf-8 -*-
# Copyright 2025 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from textwrap import dedent
from unittest.mock import patch

from ansible_collections.rucdev.ix.plugins.modules import ix_ospf_interfaces
from ansible_collections.rucdev.ix.tests.unit.modules.utils import set_module_args

from .ix_module import TestIxModule


class TestIxOspfInterfacesModule(TestIxModule):
    module = ix_ospf_interfaces

    def setUp(self):
        super(TestIxOspfInterfacesModule, self).setUp()

        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base."
            "get_resource_connection"
        )
        self.get_resource_connection_facts = (
            self.mock_get_resource_connection_facts.start()
        )

        self.mock_execute_show_command = patch(
            "ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.ospf_interfaces.ospf_interfaces."
            "Ospf_interfacesFacts.get_ospf_interfaces_data"
        )
        self.execute_show_command = self.mock_execute_show_command.start()
        self.maxDiff = None

    def tearDown(self):
        super(TestIxOspfInterfacesModule, self).tearDown()
        self.mock_get_resource_connection_facts.stop()
        self.mock_execute_show_command.stop()

    def test_ix_ospf_interfaces_merged(self):
        self.execute_show_command.return_value = dedent(
            """\
            interface GigaEthernet0.0
             ip ospf priority 20
             ip ospf cost 100
             ip ospf network point-to-point
            interface GigaEthernet1.0
             ipv6 ospf priority 60
            """
        )
        set_module_args(
            dict(
                config=[
                    dict(
                        name="GigaEthernet0.0",
                        address_family=[
                            dict(
                                afi="ipv4",
                                mtu_ignore=True,
                                priority=40,
                            ),
                        ],
                    ),
                    dict(
                        name="GigaEthernet1.0",
                        address_family=[
                            dict(
                                afi="ipv6",
                                priority=80,
                            )
                        ],
                    ),
                ],
                state="merged",
            )
        )
        commands = [
            "interface GigaEthernet0.0",
            "ip ospf mtu-ignore",
            "ip ospf priority 40",
            "interface GigaEthernet1.0",
            "ipv6 ospf priority 80",
        ]
        result = self.execute_module(changed=True)
        self.assertEqual(sorted(result["commands"]), sorted(commands))

    def test_ix_ospf_interfaces_merged_idempotent(self):
        self.execute_show_command.return_value = dedent(
            """\
            interface GigaEthernet0.0
             ip ospf priority 20
             ip ospf mtu-ignore
            interface GigaEthernet1.0
             ipv6 ospf priority 60
            """
        )
        set_module_args(
            dict(
                config=[
                    dict(
                        name="GigaEthernet0.0",
                        address_family=[
                            dict(
                                afi="ipv4",
                                priority=20,
                                mtu_ignore=True,
                            ),
                        ],
                    ),
                    dict(
                        name="GigaEthernet1.0",
                        address_family=[
                            dict(
                                afi="ipv6",
                                priority=60,
                            )
                        ],
                    ),
                ],
                state="merged",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_ix_ospf_interfaces_replaced(self):
        self.execute_show_command.return_value = dedent(
            """\
            interface GigaEthernet0.0
             ip ospf priority 20
             ip ospf network point-to-point
             ip ospf cost 100
            interface GigaEthernet1.0
             ipv6 ospf priority 60
            """
        )
        set_module_args(
            dict(
                config=[
                    dict(
                        name="GigaEthernet0.0",
                        address_family=[
                            dict(
                                afi="ipv4",
                                priority=30,
                                cost=200,
                            ),
                        ],
                    )
                ],
                state="replaced",
            )
        )
        commands = [
            "interface GigaEthernet0.0",
            "no ip ospf network point-to-point",
            "ip ospf priority 30",
            "ip ospf cost 200",
        ]
        result = self.execute_module(changed=True)
        self.assertEqual(sorted(result["commands"]), sorted(commands))

    def test_ix_ospf_interfaces_overridden(self):
        self.execute_show_command.return_value = dedent(
            """\
            interface GigaEthernet0.0
             ip ospf priority 20
             ip ospf network point-to-point
            interface GigaEthernet1.0
             ipv6 ospf priority 60
             ipv6 ospf cost 150
            """
        )
        set_module_args(
            dict(
                config=[
                    dict(
                        name="GigaEthernet0.0",
                        address_family=[
                            dict(
                                afi="ipv4",
                                priority=50,
                                hello_interval=15,
                            ),
                        ],
                    )
                ],
                state="overridden",
            )
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
        self.assertEqual(sorted(result["commands"]), sorted(commands))

    def test_ix_ospf_interfaces_deleted(self):
        self.execute_show_command.return_value = dedent(
            """\
            interface GigaEthernet0.0
             ip ospf priority 20
             ip ospf network point-to-point
             ip ospf cost 100
            interface GigaEthernet1.0
             ipv6 ospf priority 60
            """
        )
        set_module_args(
            dict(
                config=[
                    dict(
                        name="GigaEthernet0.0",
                    )
                ],
                state="deleted",
            )
        )
        commands = [
            "interface GigaEthernet0.0",
            "no ip ospf priority 20",
            "no ip ospf network point-to-point",
            "no ip ospf cost 100",
        ]
        self.execute_module(changed=True, commands=commands)

    def test_ix_ospf_interfaces_parsed(self):
        self.execute_show_command.return_value = dedent(
            """\
            interface GigaEthernet0.0
             ip ospf priority 20
             ip ospf network point-to-point
            """
        )
        set_module_args(
            dict(
                running_config="interface GigaEthernet1.0\n ip ospf priority 30\n ip ospf cost 200\n ipv6 ospf priority 40\n",
                state="parsed",
            )
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
            }
        ]
        self.assertEqual(parsed_list, result["parsed"])

    # IX hides the neighbor defaults (poll-interval 120, priority 1).
    NEIGHBORS = dedent("""\
        interface GigaEthernet1.0
          ip address 10.0.91.2/24
          ipv6 enable
          ipv6 ospf neighbor 1 10.0.91.3 2001:db8:91::3 poll-interval 180 priority 10
          ip ospf network non-broadcast
          ip ospf neighbor 10.0.91.3 poll-interval 180 priority 10
          ip ospf neighbor 10.0.91.4
          no shutdown
        !
        """)

    @staticmethod
    def _neighbors(v2=None, v3=None):
        afs = [dict(afi="ipv4", interface_type="non-broadcast", neighbor_v2=v2 or [])]
        if v3:
            afs.append(dict(afi="ipv6", neighbor_v3=v3))
        return [dict(name="GigaEthernet1.0", address_family=afs)]

    V2_3 = dict(router_id="10.0.91.3", interval=180, priority=10)
    V2_4 = dict(router_id="10.0.91.4")
    V3_3 = dict(
        process_id=1,
        router_id="10.0.91.3",
        address="2001:db8:91::3",
        interval=180,
        priority=10,
    )

    def test_ix_ospf_interfaces_parsed_neighbors(self):
        set_module_args(dict(running_config=self.NEIGHBORS, state="parsed"))
        result = self.execute_module(changed=False)
        self.assertEqual(
            result["parsed"],
            [
                dict(
                    name="GigaEthernet1.0",
                    address_family=[
                        dict(
                            afi="ipv4",
                            interface_type="non-broadcast",
                            neighbor_v2=[
                                self.V2_3,
                                dict(router_id="10.0.91.4", interval=120, priority=1),
                            ],
                        ),
                        dict(afi="ipv6", neighbor_v3=[self.V3_3]),
                    ],
                )
            ],
        )

    def test_ix_ospf_interfaces_rendered_neighbors(self):
        set_module_args(
            dict(
                config=self._neighbors(
                    v2=[self.V2_3, self.V2_4, dict(router_id="10.0.91.5", priority=20)],
                    v3=[self.V3_3],
                ),
                state="rendered",
            )
        )
        result = self.execute_module(changed=False)
        self.assertEqual(
            sorted(result["rendered"]),
            sorted(
                [
                    "interface GigaEthernet1.0",
                    "ip ospf network non-broadcast",
                    "ip ospf neighbor 10.0.91.3 poll-interval 180 priority 10",
                    "ip ospf neighbor 10.0.91.4",
                    "ip ospf neighbor 10.0.91.5 priority 20",
                    "ipv6 ospf neighbor 1 10.0.91.3 2001:db8:91::3 poll-interval 180 priority 10",
                ]
            ),
        )

    def test_ix_ospf_interfaces_merged_neighbor_add(self):
        self.execute_show_command.return_value = self.NEIGHBORS
        set_module_args(
            dict(
                config=self._neighbors(v2=[dict(router_id="10.0.91.1", priority=20)]),
                state="merged",
            )
        )
        self.execute_module(
            changed=True,
            commands=[
                "interface GigaEthernet1.0",
                "ip ospf neighbor 10.0.91.1 priority 20",
            ],
        )

    def test_ix_ospf_interfaces_merged_neighbor_idempotent(self):
        # includes a neighbor with default options and an upper-case v3 address
        self.execute_show_command.return_value = self.NEIGHBORS
        v3 = dict(self.V3_3, address="2001:DB8:91::3")
        set_module_args(
            dict(
                config=self._neighbors(v2=[self.V2_3, self.V2_4], v3=[v3]),
                state="merged",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_ix_ospf_interfaces_merged_neighbor_change_options(self):
        # re-entering a neighbor replaces all of its options on IX
        self.execute_show_command.return_value = self.NEIGHBORS
        set_module_args(
            dict(
                config=self._neighbors(
                    v2=[dict(router_id="10.0.91.3", priority=20)],
                    v3=[dict(self.V3_3, interval=120)],
                ),
                state="merged",
            )
        )
        self.execute_module(
            changed=True,
            commands=[
                "interface GigaEthernet1.0",
                "ip ospf neighbor 10.0.91.3 priority 20",
                "ipv6 ospf neighbor 1 10.0.91.3 2001:db8:91::3 priority 10",
            ],
        )

    def test_ix_ospf_interfaces_replaced_neighbors(self):
        self.execute_show_command.return_value = self.NEIGHBORS
        set_module_args(
            dict(
                config=self._neighbors(v2=[self.V2_3, dict(router_id="10.0.91.5")]),
                state="replaced",
            )
        )
        self.execute_module(
            changed=True,
            sort=False,
            commands=[
                "interface GigaEthernet1.0",
                "ip ospf neighbor 10.0.91.5",
                "no ip ospf neighbor 10.0.91.4",
                "no ipv6 ospf neighbor 1 10.0.91.3 2001:db8:91::3",
            ],
        )

    def test_ix_ospf_interfaces_overridden_neighbors(self):
        self.execute_show_command.return_value = self.NEIGHBORS
        set_module_args(
            dict(
                config=[
                    dict(
                        name="GigaEthernet1.0",
                        address_family=[dict(afi="ipv4", neighbor_v2=[self.V2_4])],
                    )
                ],
                state="overridden",
            )
        )
        self.execute_module(
            changed=True,
            sort=False,
            commands=[
                "interface GigaEthernet1.0",
                "no ip ospf network non-broadcast",
                "no ip ospf neighbor 10.0.91.3",
                "no ipv6 ospf neighbor 1 10.0.91.3 2001:db8:91::3",
            ],
        )

    def test_ix_ospf_interfaces_deleted_neighbors(self):
        self.execute_show_command.return_value = self.NEIGHBORS
        set_module_args(dict(config=[dict(name="GigaEthernet1.0")], state="deleted"))
        self.execute_module(
            changed=True,
            sort=False,
            commands=[
                "interface GigaEthernet1.0",
                "no ip ospf network non-broadcast",
                "no ip ospf neighbor 10.0.91.3",
                "no ip ospf neighbor 10.0.91.4",
                "no ipv6 ospf neighbor 1 10.0.91.3 2001:db8:91::3",
            ],
        )

    def test_ix_ospf_interfaces_neighbor_requires_router_id(self):
        set_module_args(
            dict(
                config=self._neighbors(v2=[dict(priority=20)]),
                state="rendered",
            )
        )
        result = self.execute_module(failed=True)
        self.assertIn("router_id", result["msg"])

    def test_ix_ospf_interfaces_rendered(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="GigaEthernet0.0",
                        address_family=[
                            dict(
                                afi="ipv4",
                                priority=10,
                                cost=100,
                                hello_interval=15,
                                dead_interval=60,
                                mtu_ignore=True,
                                interface_type="point-to-point",
                                authentication_type="text",
                                authentication_key="mypassword",
                            ),
                        ],
                    ),
                    dict(
                        name="GigaEthernet1.0",
                        address_family=[
                            dict(
                                afi="ipv6",
                                priority=20,
                                cost=200,
                                hello_interval=10,
                                dead_interval=40,
                            )
                        ],
                    ),
                ],
                state="rendered",
            )
        )
        commands = [
            "interface GigaEthernet0.0",
            "ip ospf priority 10",
            "ip ospf cost 100",
            "ip ospf hello-interval 15",
            "ip ospf dead-interval 60",
            "ip ospf mtu-ignore",
            "ip ospf network point-to-point",
            "ip ospf authentication-key mypassword",
            "interface GigaEthernet1.0",
            "ipv6 ospf priority 20",
            "ipv6 ospf cost 200",
            "ipv6 ospf hello-interval 10",
            "ipv6 ospf dead-interval 40",
        ]
        result = self.execute_module(changed=False)
        self.assertEqual(sorted(result["rendered"]), sorted(commands))
