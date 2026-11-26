#
# -*- coding: utf-8 -*-
# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from textwrap import dedent
from unittest.mock import patch

from ansible_collections.rucdev.ix.plugins.modules import ix_l2_interfaces
from ansible_collections.rucdev.ix.tests.unit.modules.utils import set_module_args

from .ix_module import TestIxModule

# Format as shown by "show running-config interface" on IX2215 10.10.29
RUNNING_CONFIG = dedent("""\
    interface GigaEthernet0.0
      ip address 192.168.37.127/24
      no shutdown
    !
    interface GigaEthernet2.0
      no ip address
      bridge-group 1
      shutdown
    !
    interface GigaEthernet2.1
      encapsulation dot1q 10 tpid 8100
      auto-connect
      no ip address
      bridge-group 1
      shutdown
    !
    interface GigaEthernet2.2
      encapsulation dot1q 20 tpid 88a8
      auto-connect
      no ip address
      bridge-group 2 port-protected
      bridge-group 2 port-table-size 5
      shutdown
    !
    interface BRI0.0
      encapsulation ppp
      no auto-connect
      no ip address
      shutdown
    !
    interface Loopback0.0
      ip address 192.168.2.1/32
    """)

GATHERED = [
    {"name": "GigaEthernet2.0", "bridge_group": {"group": 1}},
    {
        "name": "GigaEthernet2.1",
        "dot1q": {"vlan_id": 10, "tpid": "8100"},
        "bridge_group": {"group": 1},
    },
    {"name": "GigaEthernet2.2", "dot1q": {"vlan_id": 20, "tpid": "88a8"}},
]


class TestIxL2InterfacesModule(TestIxModule):
    module = ix_l2_interfaces

    def setUp(self):
        super(TestIxL2InterfacesModule, self).setUp()

        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base."
            "get_resource_connection"
        )
        self.get_resource_connection_facts = (
            self.mock_get_resource_connection_facts.start()
        )

        self.mock_execute_show_command = patch(
            "ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.l2_interfaces.l2_interfaces."
            "L2_interfacesFacts.get_l2_interfaces_data"
        )
        self.execute_show_command = self.mock_execute_show_command.start()
        self.execute_show_command.return_value = RUNNING_CONFIG

    def tearDown(self):
        super(TestIxL2InterfacesModule, self).tearDown()
        self.mock_get_resource_connection_facts.stop()
        self.mock_execute_show_command.stop()

    # merged

    def test_merged_new_subinterface(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="GigaEthernet2.3",
                        dot1q=dict(vlan_id=30),
                        bridge_group=dict(group=1),
                    )
                ],
                state="merged",
            )
        )
        result = self.execute_module(
            changed=True,
            commands=[
                "interface GigaEthernet2.3",
                "encapsulation dot1q 30 tpid 8100",
                "bridge-group 1",
            ],
            sort=False,
        )
        self.assertEqual(len(result["warnings"]), 1)
        self.assertIn("restart", result["warnings"][0])

    def test_merged_changes_vlan_and_moves_bridge_group(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="GigaEthernet2.1",
                        dot1q=dict(vlan_id=11),
                        bridge_group=dict(group=2),
                    )
                ],
                state="merged",
            )
        )
        # the old group must go first: IX rejects a second bridge-group
        self.execute_module(
            changed=True,
            commands=[
                "interface GigaEthernet2.1",
                "encapsulation dot1q 11 tpid 8100",
                "no bridge-group 1",
                "bridge-group 2",
            ],
            sort=False,
        )

    def test_merged_keeps_unspecified_settings(self):
        set_module_args(
            dict(
                config=[dict(name="GigaEthernet2.2", bridge_group=dict(group=3))],
                state="merged",
            )
        )
        result = self.execute_module(
            changed=True,
            commands=["interface GigaEthernet2.2", "bridge-group 3"],
            sort=False,
        )
        self.assertEqual(result["warnings"], [])

    def test_merged_idempotent(self):
        set_module_args(
            dict(
                config=[
                    dict(name="GigaEthernet2.0", bridge_group=dict(group=1)),
                    # tpid omitted == 8100
                    dict(name="GigaEthernet2.1", dot1q=dict(vlan_id=10)),
                    dict(
                        name="GigaEthernet2.2",
                        dot1q=dict(vlan_id=20, tpid="0x88A8"),
                    ),
                ],
                state="merged",
            )
        )
        self.execute_module(changed=False, commands=[])

    def test_merged_tpid_change(self):
        set_module_args(
            dict(
                config=[
                    dict(name="GigaEthernet2.1", dot1q=dict(vlan_id=10, tpid="88a8"))
                ],
                state="merged",
            )
        )
        self.execute_module(
            changed=True,
            commands=["interface GigaEthernet2.1", "encapsulation dot1q 10 tpid 88a8"],
            sort=False,
        )

    # replaced

    def test_replaced_removes_bridge_group_and_keeps_dot1q(self):
        set_module_args(dict(config=[dict(name="GigaEthernet2.1")], state="replaced"))
        result = self.execute_module(
            changed=True,
            commands=["interface GigaEthernet2.1", "no bridge-group 1"],
            sort=False,
        )
        self.assertEqual(len(result["warnings"]), 1)
        self.assertIn("GigaEthernet2.1", result["warnings"][0])
        self.assertIn("no encapsulation dot1q", result["warnings"][0])

    def test_replaced_idempotent(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="GigaEthernet2.1",
                        dot1q=dict(vlan_id=10, tpid="8100"),
                        bridge_group=dict(group=1),
                    )
                ],
                state="replaced",
            )
        )
        self.execute_module(changed=False, commands=[])

    # overridden

    def test_overridden(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="GigaEthernet2.1",
                        dot1q=dict(vlan_id=10),
                        bridge_group=dict(group=5),
                    ),
                    dict(name="GigaEthernet2.2", dot1q=dict(vlan_id=20, tpid="88a8")),
                ],
                state="overridden",
            )
        )
        self.execute_module(
            changed=True,
            commands=[
                "interface GigaEthernet2.0",
                "no bridge-group 1",
                "interface GigaEthernet2.1",
                "no bridge-group 1",
                "bridge-group 5",
            ],
            sort=False,
        )

    def test_overridden_idempotent(self):
        set_module_args(dict(config=GATHERED, state="overridden"))
        self.execute_module(changed=False, commands=[])

    # deleted

    def test_deleted_one(self):
        set_module_args(dict(config=[dict(name="GigaEthernet2.0")], state="deleted"))
        result = self.execute_module(
            changed=True,
            commands=["interface GigaEthernet2.0", "no bridge-group 1"],
            sort=False,
        )
        self.assertEqual(result["warnings"], [])

    def test_deleted_all(self):
        set_module_args(dict(state="deleted"))
        result = self.execute_module(
            changed=True,
            commands=[
                "interface GigaEthernet2.0",
                "no bridge-group 1",
                "interface GigaEthernet2.1",
                "no bridge-group 1",
            ],
            sort=False,
        )
        self.assertIn("GigaEthernet2.1, GigaEthernet2.2", result["warnings"][0])

    def test_deleted_idempotent(self):
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet2.1
              encapsulation dot1q 10 tpid 8100
              no ip address
            """)
        set_module_args(dict(state="deleted"))
        self.execute_module(changed=False, commands=[])

    # gathered / parsed / rendered

    def test_gathered(self):
        set_module_args(dict(state="gathered"))
        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"], GATHERED)

    def test_gathered_empty(self):
        self.execute_show_command.return_value = dedent("""\
            interface GigaEthernet0.0
              ip address 192.168.37.127/24
              no shutdown
            """)
        set_module_args(dict(state="gathered"))
        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"], [])

    def test_parsed(self):
        set_module_args(dict(running_config=RUNNING_CONFIG, state="parsed"))
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], GATHERED)

    def test_rendered(self):
        set_module_args(
            dict(
                config=[
                    dict(name="GigaEthernet0.1", dot1q=dict(vlan_id=100, tpid="88A8")),
                    dict(name="BVI0", bridge_group=dict(group=1)),
                ],
                state="rendered",
            )
        )
        result = self.execute_module(changed=False)
        self.assertEqual(
            result["rendered"],
            [
                "interface GigaEthernet0.1",
                "encapsulation dot1q 100 tpid 88a8",
                "interface BVI0",
                "bridge-group 1",
            ],
        )

    # validation

    def test_dot1q_on_base_interface_fails(self):
        set_module_args(
            dict(
                config=[dict(name="GigaEthernet2.0", dot1q=dict(vlan_id=10))],
                state="merged",
            )
        )
        result = self.execute_module(failed=True)
        self.assertIn("sub-interface", result["msg"])

    def test_vlan_id_out_of_range_fails(self):
        set_module_args(
            dict(
                config=[dict(name="GigaEthernet2.1", dot1q=dict(vlan_id=4096))],
                state="rendered",
            )
        )
        self.execute_module(failed=True)

    def test_tpid_out_of_range_fails(self):
        set_module_args(
            dict(
                config=[
                    dict(name="GigaEthernet2.1", dot1q=dict(vlan_id=10, tpid="5dc"))
                ],
                state="rendered",
            )
        )
        self.execute_module(failed=True)

    def test_tpid_not_hex_fails(self):
        set_module_args(
            dict(
                config=[
                    dict(name="GigaEthernet2.1", dot1q=dict(vlan_id=10, tpid="zz"))
                ],
                state="rendered",
            )
        )
        self.execute_module(failed=True)

    def test_bridge_group_out_of_range_fails(self):
        set_module_args(
            dict(
                config=[dict(name="GigaEthernet2.1", bridge_group=dict(group=0))],
                state="rendered",
            )
        )
        self.execute_module(failed=True)
