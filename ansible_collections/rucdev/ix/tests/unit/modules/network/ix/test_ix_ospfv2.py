#
# Copyright 2025 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


"""Unit tests of the ix_ospfv2 module."""

from textwrap import dedent
from unittest.mock import patch

from ansible_collections.rucdev.ix.plugins.modules import ix_ospfv2
from ansible_collections.rucdev.ix.tests.unit.modules.utils import set_module_args

from .ix_module import TestIxModule


class TestIxOspfv2Module(TestIxModule):
    """Unit tests of the ix_ospfv2 module."""

    module = ix_ospfv2

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
            "ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.ospfv2.ospfv2."
            "Ospfv2Facts.get_ospfv2_data",
        )
        self.execute_show_command = self.mock_execute_show_command.start()
        self.maxDiff = 10000

    def tearDown(self) -> None:
        """Stop the patches."""
        super().tearDown()
        self.mock_get_resource_connection_facts.stop()
        self.mock_execute_show_command.stop()

    def test_ix_ospfv2_merged(self) -> None:
        """Merged adds the OSPFv2 process settings."""
        self.execute_show_command.return_value = dedent("""\
            ip router ospf 200
             router-id 192.168.1.1
             compatible rfc1583
             distribute-list prefix test_prefix
             network 192.168.0.0/24 area 0
             area 0
             passive-interface GigaEthernet0.0
            """)
        set_module_args(
            {
                "config": {
                    "processes": [
                        {
                            "process_id": 200,
                            "router_id": "192.168.1.1",
                            "compatible": {"rfc1583": True},
                            "network": [
                                {
                                    "address": "192.168.0.0/24",
                                    "area": "0",
                                },
                                {
                                    "address": "10.0.0.0/24",
                                    "area": "10",
                                },
                            ],
                            "areas": [
                                {
                                    "area_id": "0",
                                },
                                {
                                    "area_id": "10",
                                    "default_cost": 10,
                                    "nssa": {
                                        "no_summary": True,
                                        "translate": True,
                                    },
                                },
                            ],
                            "passive_interfaces": [
                                "GigaEthernet0.0",
                                "GigaEthernet0.1",
                            ],
                        },
                    ],
                },
                "state": "merged",
            },
        )
        commands = [
            "ip router ospf 200",
            "network 10.0.0.0/24 area 10",
            "area 10",
            "area 10 default-cost 10",
            "area 10 nssa no-summary translate",
            "passive-interface GigaEthernet0.1",
        ]
        result = self.execute_module(changed=True)
        assert sorted(result["commands"]) == sorted(commands)

    def test_ix_ospfv2_merged_idempotent(self) -> None:
        """Merged with the current settings changes nothing."""
        self.execute_show_command.return_value = dedent("""\
            ip router ospf 200
             router-id 192.168.1.1
             compatible rfc1583
             distribute-list prefix test_prefix
             network 192.168.0.0/24 area 0
             area 0
             area 0 default-cost 10
             passive-interface GigaEthernet0.0
            """)
        set_module_args(
            {
                "config": {
                    "processes": [
                        {
                            "process_id": 200,
                            "router_id": "192.168.1.1",
                            "compatible": {"rfc1583": True},
                            "distribute_list": {
                                "type": "prefix",
                                "name": "test_prefix",
                            },
                            "network": [
                                {
                                    "address": "192.168.0.0/24",
                                    "area": "0",
                                },
                            ],
                            "areas": [
                                {
                                    "area_id": "0",
                                    "default_cost": 10,
                                },
                            ],
                            "passive_interfaces": ["GigaEthernet0.0"],
                        },
                    ],
                },
                "state": "merged",
            },
        )
        self.execute_module(changed=False, commands=[])

    def test_ix_ospfv2_replaced(self) -> None:
        """Replaced sets the process settings and removes the others."""
        self.execute_show_command.return_value = dedent("""\
            ip router ospf 200
             router-id 192.168.1.1
             compatible rfc1583
             distribute-list prefix test_prefix
             network 192.168.0.0/24 area 0
             area 0
             area 0 default-cost 10
             passive-interface GigaEthernet0.0
            """)
        set_module_args(
            {
                "config": {
                    "processes": [
                        {
                            "process_id": 200,
                            "router_id": "192.168.2.1",
                            "default_metric": 10,
                            "network": [
                                {
                                    "address": "192.168.0.0/24",
                                    "area": "0",
                                },
                            ],
                            "areas": [
                                {
                                    "area_id": "0",
                                    "default_cost": 20,
                                },
                            ],
                        },
                    ],
                },
                "state": "replaced",
            },
        )
        commands = [
            "ip router ospf 200",
            "router-id 192.168.2.1",
            "no compatible rfc1583",
            "default-metric 10",
            "no distribute-list prefix test_prefix",
            "area 0 default-cost 20",
            "no passive-interface GigaEthernet0.0",
        ]
        result = self.execute_module(changed=True)
        assert sorted(result["commands"]) == sorted(commands)

    def test_ix_ospfv2_overridden(self) -> None:
        """Overridden removes the processes that are not given."""
        self.execute_show_command.return_value = dedent("""\
            ip router ospf 200
             router-id 192.168.1.1
             compatible rfc1583
             distribute-list prefix test_prefix
             network 192.168.0.0/24 area 0
             area 0
             area 0 default-cost 10
             passive-interface GigaEthernet0.0
            """)
        set_module_args(
            {
                "config": {
                    "processes": [
                        {
                            "process_id": 100,
                            "router_id": "10.10.10.10",
                            "default_metric": 20,
                            "distance": {
                                "external": 110,
                                "inter_area": 90,
                                "intra_area": 80,
                            },
                            "distribute_list": {
                                "type": "route-map",
                                "name": "new_route_map",
                            },
                            "network": [
                                {
                                    "address": "10.0.0.0/24",
                                    "area": "5",
                                },
                            ],
                            "areas": [
                                {
                                    "area_id": "5",
                                    "nssa": {
                                        "no_summary": True,
                                        "translate": True,
                                        "stability_interval": 10,
                                        "default_metric": 20,
                                        "default_metric_type": 1,
                                    },
                                },
                                {
                                    "area_id": "10",
                                    "stub": {
                                        "set": True,
                                        "no_summary": True,
                                    },
                                },
                            ],
                            "originate_default": {
                                "always": True,
                                "metric": 100,
                                "metric_type": 1,
                                "route_map": "default_map",
                            },
                        },
                    ],
                },
                "state": "overridden",
            },
        )
        commands = [
            "no ip router ospf 200",
            "ip router ospf 100",
            "router-id 10.10.10.10",
            "default-metric 20",
            "distance external 110 inter-area 90 intra-area 80 nssa-external 110",
            "distribute-list route-map new_route_map",
            "network 10.0.0.0/24 area 5",
            "area 5",
            "area 5 nssa no-summary stability-interval 10 translate default-metric 20 default-metric-type 1",
            "area 10",
            "area 10 stub no-summary",
            "originate-default always metric 100 metric-type 1 route-map default_map",
        ]
        result = self.execute_module(changed=True)
        assert sorted(result["commands"]) == sorted(commands)

    def test_ix_ospfv2_deleted(self) -> None:
        """Deleted removes the OSPFv2 process."""
        self.execute_show_command.return_value = dedent("""\
            ip router ospf 200
             router-id 192.168.1.1
             compatible rfc1583
             distribute-list prefix test_prefix
             network 192.168.0.0/24 area 0
             area 0 default-cost 10
             passive-interface GigaEthernet0.0
            """)
        set_module_args(
            {
                "config": {"processes": [{"process_id": 200}]},
                "state": "deleted",
            },
        )
        commands = ["no ip router ospf 200"]
        self.execute_module(changed=True, commands=commands)

    def test_ix_ospfv2_parsed(self) -> None:
        """Parsed reads the OSPFv2 settings from running_config."""
        self.execute_show_command.return_value = dedent("""\
            ip router ospf 200
             router-id 192.168.1.1
             compatible rfc1583
             distribute-list prefix test_prefix
             network 192.168.0.0/24 area 0
             area 0 default-cost 10
             passive-interface GigaEthernet0.0
            """)
        set_module_args(
            {
                "running_config": "ip router ospf 1\n area 5 nssa no-summary stability-interval 10 translate default-metric 20 default-metric-type 1\n",
                "state": "parsed",
            },
        )
        result = self.execute_module(changed=False)
        parsed_list = {
            "processes": [
                {
                    "process_id": 1,
                    "areas": [
                        {
                            "area_id": "5",
                            "nssa": {
                                "no_summary": True,
                                "translate": True,
                                "stability_interval": 10,
                                "default_metric": 20,
                                "default_metric_type": 1,
                            },
                        },
                    ],
                },
            ],
        }
        assert parsed_list == result["parsed"]

    def test_ix_ospfv2_rendered(self) -> None:
        """Rendered returns the OSPFv2 commands."""
        set_module_args(
            {
                "config": {
                    "processes": [
                        {
                            "process_id": 100,
                            "router_id": "10.10.10.10",
                            "compatible": {"rfc1583": True},
                            "default_metric": 10,
                            "distance": {
                                "external": 110,
                                "inter_area": 90,
                                "intra_area": 80,
                                "nssa_external": 100,
                            },
                            "distribute_list": {
                                "type": "prefix",
                                "name": "test_prefix",
                            },
                            "network": [
                                {
                                    "address": "192.168.0.0/24",
                                    "area": "5",
                                },
                                {
                                    "address": "10.0.0.0/24",
                                    "area": "10",
                                },
                            ],
                            "nssa_ranges": [
                                {
                                    "range": "192.168.1.0/24",
                                    "not_advertise": True,
                                    "tag": "100",
                                },
                            ],
                            "originate_default": {
                                "always": True,
                                "metric": 100,
                                "metric_type": 1,
                                "route_map": "default_map",
                            },
                            "passive_interfaces": [
                                "GigaEthernet0.0",
                                "GigaEthernet0.1",
                            ],
                            "rib": {"max_entries": 10000},
                            "timers": {
                                "delay": 5,
                                "hold": 10,
                            },
                            "areas": [
                                {
                                    "area_id": "0",
                                    "virtual_links": [
                                        {
                                            "address": "192.168.2.1",
                                            "authentication": {
                                                "auth_type": "message-digest",
                                                "message_digest_key_id": 1,
                                                "message_digest_password": "md5password",
                                            },
                                            "dead_interval": 40,
                                            "hello_interval": 10,
                                            "retransmit_interval": 5,
                                            "transmit_delay": 1,
                                        },
                                    ],
                                },
                                {
                                    "area_id": "5",
                                    "nssa": {
                                        "no_summary": True,
                                        "translate": True,
                                        "stability_interval": 10,
                                        "default_metric": 20,
                                        "default_metric_type": 1,
                                    },
                                    "ranges": [
                                        {
                                            "address": "192.168.10.0/24",
                                            "advertise": True,
                                        },
                                    ],
                                },
                                {
                                    "area_id": "10",
                                    "default_cost": 20,
                                    "stub": {
                                        "set": True,
                                        "no_summary": True,
                                    },
                                },
                            ],
                        },
                    ],
                },
                "state": "rendered",
            },
        )
        commands = [
            "ip router ospf 100",
            "router-id 10.10.10.10",
            "compatible rfc1583",
            "default-metric 10",
            "distance external 110 inter-area 90 intra-area 80 nssa-external 100",
            "distribute-list prefix test_prefix",
            "network 192.168.0.0/24 area 5",
            "network 10.0.0.0/24 area 10",
            "nssa-range 192.168.1.0/24 not-advertise tag 100",
            "originate-default always metric 100 metric-type 1 route-map default_map",
            "passive-interface GigaEthernet0.0",
            "passive-interface GigaEthernet0.1",
            "rib max-entries 10000",
            "timers delay 5 hold 10",
            "area 0",
            (
                "area 0 virtual-link 192.168.2.1 dead-interval 40 hello-interval 10 retransmit-interval"
                " 5 transmit-delay 1 authentication message-digest message-digest-key 1 md5password"
            ),
            "area 5",
            "area 5 nssa no-summary stability-interval 10 translate default-metric 20 default-metric-type 1",
            "area 5 range 192.168.10.0/24 advertise",
            "area 10",
            "area 10 default-cost 20",
            "area 10 stub no-summary",
        ]
        result = self.execute_module(changed=False)
        assert sorted(result["rendered"]) == sorted(commands)

    NSSA_RANGES_CONFIG = dedent("""\
        ip router ospf 1
          area 1
          nssa-range 192.168.1.0/24 tag 100
          nssa-range 192.168.2.0/24 not-advertise
        !
        """)

    def test_ix_ospfv2_nssa_ranges_parsed(self) -> None:
        """Parsed reads the NSSA ranges."""
        set_module_args({"running_config": self.NSSA_RANGES_CONFIG, "state": "parsed"})
        result = self.execute_module(changed=False)
        assert result["parsed"]["processes"][0]["nssa_ranges"] == [
            {"range": "192.168.1.0/24", "tag": "100"},
            {"range": "192.168.2.0/24", "not_advertise": True},
        ]

    def test_ix_ospfv2_nssa_ranges_gathered(self) -> None:
        """Gathered reads the NSSA ranges of the device."""
        self.execute_show_command.return_value = self.NSSA_RANGES_CONFIG
        set_module_args({"state": "gathered"})
        result = self.execute_module(changed=False)
        assert result["gathered"]["processes"][0]["nssa_ranges"] == [
            {"range": "192.168.1.0/24", "tag": "100"},
            {"range": "192.168.2.0/24", "not_advertise": True},
        ]

    def test_ix_ospfv2_nssa_ranges_merged(self) -> None:
        """Merged adds an NSSA range."""
        self.execute_show_command.return_value = self.NSSA_RANGES_CONFIG
        set_module_args(
            {
                "config": {
                    "processes": [
                        {
                            "process_id": 1,
                            "nssa_ranges": [{"range": "10.0.0.0/8", "tag": "200"}],
                        },
                    ],
                },
                "state": "merged",
            },
        )
        self.execute_module(
            changed=True,
            commands=["ip router ospf 1", "nssa-range 10.0.0.0/8 tag 200"],
        )

    def test_ix_ospfv2_nssa_ranges_merged_idempotent(self) -> None:
        """Merged with the current NSSA ranges changes nothing."""
        self.execute_show_command.return_value = self.NSSA_RANGES_CONFIG
        set_module_args(
            {
                "config": {
                    "processes": [
                        {
                            "process_id": 1,
                            "nssa_ranges": [
                                {"range": "192.168.1.0/24", "tag": "100"},
                                {"range": "192.168.2.0/24", "not_advertise": True},
                            ],
                            "areas": [{"area_id": "1"}],
                        },
                    ],
                },
                "state": "merged",
            },
        )
        self.execute_module(changed=False, commands=[])

    def test_ix_ospfv2_nssa_ranges_replaced(self) -> None:
        """Replaced removes the NSSA ranges that are not given."""
        self.execute_show_command.return_value = self.NSSA_RANGES_CONFIG
        set_module_args(
            {
                "config": {
                    "processes": [
                        {
                            "process_id": 1,
                            "nssa_ranges": [{"range": "192.168.1.0/24", "tag": "300"}],
                            "areas": [{"area_id": "1"}],
                        },
                    ],
                },
                "state": "replaced",
            },
        )
        # IX rejects re-registering an existing prefix, so the old entry
        # must be removed before the new one is added (order is checked).
        self.execute_module(
            changed=True,
            sort=False,
            commands=[
                "ip router ospf 1",
                "no nssa-range 192.168.1.0/24 tag 100",
                "nssa-range 192.168.1.0/24 tag 300",
                "no nssa-range 192.168.2.0/24 not-advertise",
            ],
        )

    def test_ix_ospfv2_nssa_ranges_merged_change_tag(self) -> None:
        """Merged changes the tag of an NSSA range."""
        self.execute_show_command.return_value = self.NSSA_RANGES_CONFIG
        set_module_args(
            {
                "config": {
                    "processes": [
                        {
                            "process_id": 1,
                            "nssa_ranges": [{"range": "192.168.1.0/24", "tag": "300"}],
                        },
                    ],
                },
                "state": "merged",
            },
        )
        self.execute_module(
            changed=True,
            sort=False,
            commands=[
                "ip router ospf 1",
                "no nssa-range 192.168.1.0/24 tag 100",
                "nssa-range 192.168.1.0/24 tag 300",
            ],
        )

    def test_ix_ospfv2_nssa_ranges_deleted(self) -> None:
        """Deleted removes the NSSA ranges with the process."""
        self.execute_show_command.return_value = self.NSSA_RANGES_CONFIG
        set_module_args({"state": "deleted"})
        self.execute_module(changed=True, commands=["no ip router ospf 1"])
