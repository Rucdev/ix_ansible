#
# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from textwrap import dedent
from unittest.mock import patch

from ansible_collections.rucdev.ix.plugins.modules import ix_facts, ix_static_routes
from ansible_collections.rucdev.ix.tests.unit.modules.utils import set_module_args

from .ix_module import TestIxModule

# Lines exactly as IX2215 10.10.29 shows them in running-config.
RUNNING_CONFIG = dedent("""\
    hostname ix2215
    !
    ip route default 192.168.37.26
    ip route 198.51.100.0/24 192.168.37.26 distance 10 tag 7
    ip route 198.51.100.0/24 Null0.0 distance 250
    ip route 198.51.100.128/25 192.168.37.26 GigaEthernet0.0 distance 5
    ip route 203.0.113.0/24 GigaEthernet2.0 dhcp metric 3
    ip route 192.0.2.0/24 192.168.37.26 connected distance 10 metric 5 tag 7
    ip route vrf blue 198.51.100.0/24 Null0.0
    ipv6 route 2001:db8::/32 GigaEthernet2.0 dhcp tag 4
    ipv6 route 2001:db8:1::/48 GigaEthernet2.0 ra distance 9
    ipv6 route 2001:db8:2::/48 fe80::1%GigaEthernet0.0 metric 2
    !
    interface GigaEthernet0.0
      ip address 192.168.37.127/24
    !
    """)

# A device without any ip/ipv6 route line.
NO_ROUTES_CONFIG = dedent("""\
    hostname ix2215
    !
    interface GigaEthernet0.0
      ip address 192.168.37.127/24
    !
    interface Null0.0
      no ip address
    !
    """)

PARSED = [
    {
        "address_families": [
            {
                "afi": "ipv4",
                "routes": [
                    {
                        "dest": "default",
                        "next_hops": [{"forward_router_address": "192.168.37.26"}],
                    },
                    {
                        "dest": "198.51.100.0/24",
                        "next_hops": [
                            {
                                "forward_router_address": "192.168.37.26",
                                "distance": 10,
                                "tag": 7,
                            },
                            {"interface": "Null0.0", "distance": 250},
                        ],
                    },
                    {
                        "dest": "198.51.100.128/25",
                        "next_hops": [
                            {
                                "forward_router_address": "192.168.37.26",
                                "interface": "GigaEthernet0.0",
                                "distance": 5,
                            },
                        ],
                    },
                    {
                        "dest": "203.0.113.0/24",
                        "next_hops": [
                            {"interface": "GigaEthernet2.0", "dhcp": True, "metric": 3},
                        ],
                    },
                    {
                        "dest": "192.0.2.0/24",
                        "next_hops": [
                            {
                                "forward_router_address": "192.168.37.26",
                                "connected": True,
                                "distance": 10,
                                "metric": 5,
                                "tag": 7,
                            },
                        ],
                    },
                ],
            },
            {
                "afi": "ipv6",
                "routes": [
                    {
                        "dest": "2001:db8::/32",
                        "next_hops": [
                            {"interface": "GigaEthernet2.0", "dhcp": True, "tag": 4},
                        ],
                    },
                    {
                        "dest": "2001:db8:1::/48",
                        "next_hops": [
                            {"interface": "GigaEthernet2.0", "ra": True, "distance": 9},
                        ],
                    },
                    {
                        "dest": "2001:db8:2::/48",
                        "next_hops": [
                            {
                                "forward_router_address": "fe80::1%GigaEthernet0.0",
                                "metric": 2,
                            },
                        ],
                    },
                ],
            },
        ],
    },
    {
        "vrf": "blue",
        "address_families": [
            {
                "afi": "ipv4",
                "routes": [
                    {
                        "dest": "198.51.100.0/24",
                        "next_hops": [{"interface": "Null0.0"}],
                    },
                ],
            },
        ],
    },
]


def v4(*routes, **kw):
    """Config helper: v4(("dest", [next_hops...]), ..., vrf=None)."""
    entry = {
        "address_families": [
            {
                "afi": "ipv4",
                "routes": [{"dest": d, "next_hops": nh} for d, nh in routes],
            },
        ],
    }
    if kw.get("vrf"):
        entry["vrf"] = kw["vrf"]
    return entry


class TestIxStaticRoutesModule(TestIxModule):
    module = ix_static_routes

    def setUp(self) -> None:
        super().setUp()
        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base."
            "get_resource_connection",
        )
        self.mock_get_resource_connection.start()
        self.mock_get_data = patch(
            "ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.static_routes.static_routes."
            "Static_routesFacts.get_static_route_data",
        )
        self.get_data = self.mock_get_data.start()
        self.get_data.return_value = RUNNING_CONFIG
        self.maxDiff = None

    def tearDown(self) -> None:
        super().tearDown()
        self.mock_get_resource_connection.stop()
        self.mock_get_data.stop()

    # ---- read ----
    def test_parsed(self) -> None:
        set_module_args({"running_config": RUNNING_CONFIG, "state": "parsed"})
        result = self.execute_module(changed=False)
        assert result["parsed"] == PARSED

    def test_gathered(self) -> None:
        set_module_args({"state": "gathered"})
        result = self.execute_module(changed=False)
        assert result["gathered"] == PARSED

    def test_parsed_no_routes(self) -> None:
        set_module_args({"running_config": NO_ROUTES_CONFIG, "state": "parsed"})
        result = self.execute_module(changed=False)
        assert result["parsed"] == []

    def test_gathered_no_routes(self) -> None:
        self.get_data.return_value = NO_ROUTES_CONFIG
        set_module_args({"state": "gathered"})
        result = self.execute_module(changed=False)
        assert result["gathered"] == []

    def test_rendered(self) -> None:
        set_module_args(
            {
                "config": [
                    v4(
                        (
                            "192.0.2.0/24",
                            [
                                {
                                    "forward_router_address": "192.0.2.1",
                                    "interface": "GigaEthernet0.0",
                                    "connected": True,
                                    "distance": 10,
                                    "metric": 5,
                                    "tag": 7,
                                },
                                # defaults are treated as not specified
                                {"interface": "Null0.0", "distance": 1, "metric": 1},
                            ],
                        ),
                        vrf="blue",
                    ),
                    {
                        "address_families": [
                            {
                                "afi": "ipv6",
                                "routes": [
                                    {
                                        "dest": "2001:db8::/32",
                                        "next_hops": [
                                            {
                                                "interface": "GigaEthernet0.0",
                                                "ra": True,
                                                "tag": 3,
                                            },
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ],
                "state": "rendered",
            },
        )
        result = self.execute_module(changed=False)
        assert result["rendered"] == [
            "ip route vrf blue 192.0.2.0/24 192.0.2.1 GigaEthernet0.0 connected distance 10 metric 5 tag 7",
            "ip route vrf blue 192.0.2.0/24 Null0.0",
            "ipv6 route 2001:db8::/32 GigaEthernet0.0 ra tag 3",
        ]

    # ---- merged ----
    def test_merged_new_route(self) -> None:
        set_module_args(
            {
                "config": [
                    v4(
                        (
                            "192.0.2.128/25",
                            [
                                {
                                    "forward_router_address": "192.168.37.26",
                                    "distance": 20,
                                },
                            ],
                        ),
                    ),
                ],
                "state": "merged",
            },
        )
        self.execute_module(
            changed=True,
            commands=["ip route 192.0.2.128/25 192.168.37.26 distance 20"],
        )

    def test_merged_first_route(self) -> None:
        self.get_data.return_value = NO_ROUTES_CONFIG
        set_module_args(
            {
                "config": [
                    v4(("default", [{"forward_router_address": "192.168.37.26"}])),
                ],
                "state": "merged",
            },
        )
        self.execute_module(changed=True, commands=["ip route default 192.168.37.26"])

    def test_merged_idempotent(self) -> None:
        set_module_args(
            {
                "config": [
                    v4(
                        ("default", [{"forward_router_address": "192.168.37.26"}]),
                        (
                            "198.51.100.0/24",
                            [
                                {
                                    "forward_router_address": "192.168.37.26",
                                    "distance": 10,
                                    "tag": 7,
                                },
                            ],
                        ),
                    ),
                ],
                "state": "merged",
            },
        )
        self.execute_module(changed=False, commands=[])

    def test_merged_default_values_idempotent(self) -> None:
        # distance 1 / metric 1 never appear in running-config
        set_module_args(
            {
                "config": [
                    v4(
                        (
                            "default",
                            [
                                {
                                    "forward_router_address": "192.168.37.26",
                                    "distance": 1,
                                    "metric": 1,
                                },
                            ],
                        ),
                    ),
                ],
                "state": "merged",
            },
        )
        self.execute_module(changed=False, commands=[])

    def test_merged_change_one_option_keeps_others(self) -> None:
        # IX replaces all options when a route is re-entered, so the command
        # must carry the existing distance and tag
        set_module_args(
            {
                "config": [
                    v4(
                        (
                            "198.51.100.0/24",
                            [{"forward_router_address": "192.168.37.26", "metric": 5}],
                        ),
                    ),
                ],
                "state": "merged",
            },
        )
        self.execute_module(
            changed=True,
            commands=[
                "ip route 198.51.100.0/24 192.168.37.26 distance 10 metric 5 tag 7",
            ],
        )

    def test_merged_omitted_option_keeps_device_value(self) -> None:
        set_module_args(
            {
                "config": [
                    v4(
                        (
                            "198.51.100.0/24",
                            [{"forward_router_address": "192.168.37.26"}],
                        ),
                    ),
                ],
                "state": "merged",
            },
        )
        self.execute_module(changed=False, commands=[])

    def test_merged_gateway_case_insensitive(self) -> None:
        set_module_args(
            {
                "config": [
                    {
                        "address_families": [
                            {
                                "afi": "ipv6",
                                "routes": [
                                    {
                                        "dest": "2001:db8:2::/48",
                                        "next_hops": [
                                            {
                                                "forward_router_address": "FE80::1%GigaEthernet0.0",
                                                "metric": 2,
                                            },
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ],
                "state": "merged",
            },
        )
        self.execute_module(changed=False, commands=[])

    # ---- replaced ----
    def test_replaced(self) -> None:
        set_module_args(
            {
                "config": [
                    v4(
                        (
                            "198.51.100.0/24",
                            [{"forward_router_address": "192.168.37.26", "metric": 5}],
                        ),
                    ),
                ],
                "state": "replaced",
            },
        )
        # option set is replaced as a whole (distance/tag reset to default),
        # the Null0.0 route to the same dest is removed (identity only),
        # other destinations are untouched
        self.execute_module(
            changed=True,
            sort=False,
            commands=[
                "ip route 198.51.100.0/24 192.168.37.26 metric 5",
                "no ip route 198.51.100.0/24 Null0.0",
            ],
        )

    def test_replaced_idempotent(self) -> None:
        set_module_args(
            {
                "config": [
                    v4(
                        (
                            "198.51.100.0/24",
                            [
                                {
                                    "forward_router_address": "192.168.37.26",
                                    "distance": 10,
                                    "tag": 7,
                                },
                                {"interface": "Null0.0", "distance": 250},
                            ],
                        ),
                    ),
                ],
                "state": "replaced",
            },
        )
        self.execute_module(changed=False, commands=[])

    def test_replaced_no_routes(self) -> None:
        self.get_data.return_value = NO_ROUTES_CONFIG
        set_module_args(
            {
                "config": [v4(("192.0.2.0/24", [{"interface": "Null0.0"}]))],
                "state": "replaced",
            },
        )
        self.execute_module(changed=True, commands=["ip route 192.0.2.0/24 Null0.0"])

    # ---- overridden ----
    def test_overridden(self) -> None:
        set_module_args(
            {
                "config": [
                    v4(
                        ("default", [{"forward_router_address": "192.168.37.26"}]),
                        ("192.0.2.0/24", [{"interface": "Null0.0"}]),
                    ),
                ],
                "state": "overridden",
            },
        )
        self.execute_module(
            changed=True,
            sort=False,
            commands=[
                "ip route 192.0.2.0/24 Null0.0",
                "no ip route 198.51.100.0/24 192.168.37.26",
                "no ip route 198.51.100.0/24 Null0.0",
                "no ip route 198.51.100.128/25 192.168.37.26 GigaEthernet0.0",
                "no ip route 203.0.113.0/24 GigaEthernet2.0 dhcp",
                "no ip route 192.0.2.0/24 192.168.37.26 connected",
                "no ipv6 route 2001:db8::/32 GigaEthernet2.0 dhcp",
                "no ipv6 route 2001:db8:1::/48 GigaEthernet2.0 ra",
                "no ipv6 route 2001:db8:2::/48 fe80::1%GigaEthernet0.0",
                "no ip route vrf blue 198.51.100.0/24 Null0.0",
            ],
        )

    def test_overridden_idempotent(self) -> None:
        set_module_args({"config": PARSED, "state": "overridden"})
        self.execute_module(changed=False, commands=[])

    def test_overridden_no_routes(self) -> None:
        self.get_data.return_value = NO_ROUTES_CONFIG
        set_module_args(
            {
                "config": [v4(("192.0.2.0/24", [{"interface": "Null0.0"}]))],
                "state": "overridden",
            },
        )
        self.execute_module(changed=True, commands=["ip route 192.0.2.0/24 Null0.0"])

    # ---- deleted ----
    def test_deleted_all(self) -> None:
        self.get_data.return_value = "ip route default 192.168.37.26\nip route vrf blue 198.51.100.0/24 Null0.0\n"
        set_module_args({"state": "deleted"})
        self.execute_module(
            changed=True,
            commands=[
                "no ip route default 192.168.37.26",
                "no ip route vrf blue 198.51.100.0/24 Null0.0",
            ],
        )

    def test_deleted_all_no_routes(self) -> None:
        self.get_data.return_value = NO_ROUTES_CONFIG
        set_module_args({"state": "deleted"})
        self.execute_module(changed=False, commands=[])

    def test_deleted_last_route(self) -> None:
        # facts are read again for "after"; by then the device has no routes
        self.get_data.side_effect = [
            "ip route default 192.168.37.26\n",
            NO_ROUTES_CONFIG,
        ]
        set_module_args({"state": "deleted"})
        result = self.execute_module(
            changed=True,
            commands=["no ip route default 192.168.37.26"],
        )
        assert result["after"] == []

    def test_deleted_by_dest(self) -> None:
        set_module_args(
            {
                "config": [
                    {
                        "address_families": [
                            {"afi": "ipv4", "routes": [{"dest": "198.51.100.0/24"}]},
                        ],
                    },
                ],
                "state": "deleted",
            },
        )
        self.execute_module(
            changed=True,
            commands=[
                "no ip route 198.51.100.0/24 192.168.37.26",
                "no ip route 198.51.100.0/24 Null0.0",
            ],
        )

    def test_deleted_by_next_hop_ignores_options(self) -> None:
        set_module_args(
            {
                "config": [v4(("198.51.100.0/24", [{"interface": "Null0.0"}]))],
                "state": "deleted",
            },
        )
        self.execute_module(
            changed=True,
            commands=["no ip route 198.51.100.0/24 Null0.0"],
        )

    def test_deleted_by_vrf(self) -> None:
        set_module_args({"config": [{"vrf": "blue"}], "state": "deleted"})
        self.execute_module(
            changed=True,
            commands=["no ip route vrf blue 198.51.100.0/24 Null0.0"],
        )

    def test_deleted_idempotent(self) -> None:
        set_module_args(
            {
                "config": [v4(("192.0.2.128/25", [{"interface": "Null0.0"}]))],
                "state": "deleted",
            },
        )
        self.execute_module(changed=False, commands=[])

    # ---- validation ----
    def _fails(self, config, msg) -> None:
        set_module_args({"config": config, "state": "merged"})
        result = self.execute_module(failed=True)
        assert msg in result["msg"]

    def test_fail_no_next_hop_target(self) -> None:
        self._fails(
            [v4(("192.0.2.0/24", [{"distance": 5}]))],
            "forward_router_address and/or interface",
        )

    def test_fail_ra_on_ipv4(self) -> None:
        self._fails(
            [v4(("192.0.2.0/24", [{"interface": "GigaEthernet0.0", "ra": True}]))],
            "ra is only valid for ipv6",
        )

    def test_fail_dhcp_without_interface(self) -> None:
        self._fails(
            [
                v4(
                    (
                        "192.0.2.0/24",
                        [{"forward_router_address": "192.0.2.1", "dhcp": True}],
                    ),
                ),
            ],
            "dhcp requires interface",
        )


class TestIxFactsStaticRoutes(TestIxModule):
    module = ix_facts

    def setUp(self) -> None:
        super().setUp()
        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts."
            "get_resource_connection",
        )
        self.mock_get_resource_connection.start()
        self.mock_get_data = patch(
            "ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.static_routes.static_routes."
            "Static_routesFacts.get_static_route_data",
        )
        self.get_data = self.mock_get_data.start()
        self.get_data.return_value = NO_ROUTES_CONFIG

    def tearDown(self) -> None:
        super().tearDown()
        self.mock_get_resource_connection.stop()
        self.mock_get_data.stop()

    def test_ix_facts_static_routes_no_routes(self) -> None:
        set_module_args({"gather_network_resources": ["static_routes"]})
        result = self.execute_module(changed=False)
        assert (
            result["ansible_facts"]["ansible_network_resources"]["static_routes"] == []
        )
