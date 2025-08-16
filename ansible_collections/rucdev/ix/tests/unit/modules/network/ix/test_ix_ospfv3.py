#
# -*- coding: utf-8 -*-
# Copyright 2025 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from textwrap import dedent
from unittest.mock import patch

from ansible_collections.rucdev.ix.plugins.modules import ix_ospfv3
from ansible_collections.rucdev.ix.tests.unit.modules.utils import set_module_args

from .ix_module import TestIxModule


class TestIxOspfv3Module(TestIxModule):
    module = ix_ospfv3

    def setUp(self):
        super(TestIxOspfv3Module, self).setUp()

        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base."
            "get_resource_connection"
        )
        self.get_resource_connection_facts = (
            self.mock_get_resource_connection_facts.start()
        )

        self.mock_execute_show_command = patch(
            "ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.ospfv3.ospfv3."
            "Ospfv3Facts.get_ospfv3_data"
        )
        self.execute_show_command = self.mock_execute_show_command.start()
        self.maxDiff = 10000

    def tearDown(self):
        super(TestIxOspfv3Module, self).tearDown()
        self.mock_get_resource_connection_facts.stop()
        self.mock_execute_show_command.stop()

    def test_ix_ospfv3_merged(self):
        self.execute_show_command.return_value = dedent(
            """\
            ipv6 router ospf 200
             router-id 192.168.1.1
             network GigaEthernet0.0 area 0
             area 0
             passive-interface GigaEthernet0.0
            """
        )
        set_module_args(
            dict(
                config=dict(
                    processes=[
                        dict(
                            process_id=200,
                            router_id="192.168.1.1",
                            network=[
                                dict(
                                    interface="GigaEthernet0.0",
                                    area="0",
                                ),
                                dict(
                                    interface="GigaEthernet0.1",
                                    area="10",
                                ),
                            ],
                            areas=[
                                dict(
                                    area_id="0",
                                ),
                                dict(
                                    area_id="10",
                                    default_cost=10,
                                    stub=dict(
                                        set=True,
                                        no_summary=True,
                                    ),
                                ),
                            ],
                            passive_interfaces=["GigaEthernet0.0", "GigaEthernet0.2"],
                        )
                    ]
                ),
                state="merged",
            )
        )
        commands = [
            "ipv6 router ospf 200",
            "network GigaEthernet0.1 area 10",
            "area 10",
            "area 10 default-cost 10",
            "area 10 stub no-summary",
            "passive-interface GigaEthernet0.2",
        ]
        result = self.execute_module(changed=True)
        self.assertEqual(sorted(result["commands"]), sorted(commands))

    def test_ix_ospfv3_merged_idempotent(self):
        self.execute_show_command.return_value = dedent(
            """\
            ipv6 router ospf 200
             router-id 192.168.1.1
             network GigaEthernet0.0 area 0
             area 0
             passive-interface GigaEthernet0.0
            """
        )
        set_module_args(
            dict(
                config=dict(
                    processes=[
                        dict(
                            process_id=200,
                            router_id="192.168.1.1",
                            network=[
                                dict(
                                    interface="GigaEthernet0.0",
                                    area="0",
                                ),
                            ],
                            areas=[
                                dict(
                                    area_id="0",
                                ),
                            ],
                            passive_interfaces=["GigaEthernet0.0"],
                        )
                    ]
                ),
                state="merged",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_ix_ospfv3_replaced(self):
        self.execute_show_command.return_value = dedent(
            """\
            ipv6 router ospf 200
             router-id 192.168.1.1
             network GigaEthernet0.0 area 0
             area 0
             passive-interface GigaEthernet0.0
            """
        )
        set_module_args(
            dict(
                config=dict(
                    processes=[
                        dict(
                            process_id=200,
                            router_id="192.168.2.1",
                            network=[
                                dict(
                                    interface="GigaEthernet0.0",
                                    area="0",
                                ),
                            ],
                            areas=[
                                dict(
                                    area_id="0",
                                ),
                            ],
                        )
                    ]
                ),
                state="replaced",
            )
        )
        commands = [
            "ipv6 router ospf 200",
            "router-id 192.168.2.1",
            "no passive-interface GigaEthernet0.0",
        ]
        result = self.execute_module(changed=True)
        self.assertEqual(sorted(result["commands"]), sorted(commands))

    def test_ix_ospfv3_overridden(self):
        self.execute_show_command.return_value = dedent(
            """\
            ipv6 router ospf 200
             router-id 192.168.1.1
             network GigaEthernet0.0 area 0
             area 0
             passive-interface GigaEthernet0.0
            """
        )
        set_module_args(
            dict(
                config=dict(
                    processes=[
                        dict(
                            process_id=100,
                            router_id="10.10.10.10",
                            distance=dict(
                                external=110,
                                inter_area=90,
                                intra_area=80,
                            ),
                            network=[
                                dict(
                                    interface="GigaEthernet0.0",
                                    area="5",
                                ),
                            ],
                            areas=[
                                dict(
                                    area_id="10",
                                    stub=dict(
                                        set=True,
                                        no_summary=True,
                                    ),
                                ),
                            ],
                            originate_default=dict(
                                metric=100,
                                metric_type=1,
                                route_map="default_map",
                                tag="20",
                            ),
                        )
                    ]
                ),
                state="overridden",
            )
        )
        commands = [
            "no ipv6 router ospf 200",
            "ipv6 router ospf 100",
            "router-id 10.10.10.10",
            "distance external 110 inter-area 90 intra-area 80",
            "network GigaEthernet0.0 area 5",
            "area 10",
            "area 10 stub no-summary",
            "originate-default metric 100 metric-type 1 route-map default_map tag 20",
        ]
        result = self.execute_module(changed=True)
        self.assertEqual(sorted(result["commands"]), sorted(commands))

    def test_ix_ospfv3_deleted(self):
        self.execute_show_command.return_value = dedent(
            """\
            ipv6 router ospf 200
             router-id 192.168.1.1
             network GigaEthernet0.0 area 0
             area 0
             passive-interface GigaEthernet0.0
            """
        )
        set_module_args(
            dict(
                config=dict(processes=[dict(process_id=200)]),
                state="deleted",
            )
        )
        commands = ["no ipv6 router ospf 200"]
        self.execute_module(changed=True, commands=commands)

    def test_ix_ospfv3_parsed(self):
        self.execute_show_command.return_value = dedent(
            """\
            ipv6 router ospf 200
             router-id 192.168.1.1
             network GigaEthernet0.0 area 0
             area 0
             passive-interface GigaEthernet0.0
            """
        )
        set_module_args(
            dict(
                running_config="ipv6 router ospf 1\n area 5\n network GigaEhternet0.0 area 5",
                state="parsed",
            )
        )
        result = self.execute_module(changed=False)
        parsed_list = {
            "processes": [
                {
                    "process_id": 1,
                    "areas": [
                        {
                            "area_id": "5",
                        }
                    ],
                    "network": [
                        {
                            "interface": "GigaEhternet0.0",
                            "area": "5",
                        }
                    ],
                }
            ]
        }
        self.assertEqual(parsed_list, result["parsed"])

    def test_ix_ospfv3_rendered(self):
        set_module_args(
            dict(
                config=dict(
                    processes=[
                        dict(
                            process_id=100,
                            router_id="10.10.10.10",
                            distance=dict(
                                external=110,
                                inter_area=90,
                                intra_area=80,
                            ),
                            network=[
                                dict(
                                    interface="GigaEthernet0.0",
                                    area="5",
                                ),
                                dict(
                                    interface="GigaEthernet0.1",
                                    area="10",
                                ),
                            ],
                            originate_default=dict(
                                metric=100,
                                route_map="default_map",
                            ),
                            passive_interfaces=["GigaEthernet0.0", "GigaEthernet0.1"],
                            timers=dict(
                                delay=5,
                                hold=10,
                            ),
                            areas=[
                                dict(
                                    area_id="0",
                                ),
                                dict(
                                    area_id="5",
                                    ranges=[
                                        dict(
                                            address="2001:db8:1::/64",
                                            advertise=True,
                                        ),
                                    ],
                                ),
                                dict(
                                    area_id="10",
                                    default_cost=20,
                                    stub=dict(
                                        no_summary=True,
                                    ),
                                ),
                            ],
                        )
                    ]
                ),
                state="rendered",
            )
        )
        commands = [
            "ipv6 router ospf 100",
            "router-id 10.10.10.10",
            "distance external 110 inter-area 90 intra-area 80",
            "network GigaEthernet0.0 area 5",
            "network GigaEthernet0.1 area 10",
            "originate-default metric 100 metric-type 2 route-map default_map tag 0",
            "passive-interface GigaEthernet0.0",
            "passive-interface GigaEthernet0.1",
            "timers delay 5 hold 10",
            "area 0",
            "area 5",
            "area 5 range 2001:db8:1::/64 advertise",
            "area 10",
            "area 10 default-cost 20",
            "area 10 stub no-summary",
        ]
        result = self.execute_module(changed=False)
        self.assertEqual(sorted(result["rendered"]), sorted(commands))
