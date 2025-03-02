from __future__ import absolute_import, division, print_function


__metaclass__ = type
from textwrap import dedent
from unittest.mock import patch

from ansible_collections.rucdev.ix.plugins.modules import ix_ospfv2
from ansible_collections.rucdev.ix.tests.unit.modules.utils import set_module_args

from .ix_module import TestIxModule


class TestIxOspfv2Module(TestIxModule):
    module = ix_ospfv2

    def setUp(self):
        super(TestIxOspfv2Module, self).setUp()

        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base."
            "get_resource_connection",
        )
        self.mock_get_resource_connection_facts = (
            self.mock_get_resource_connection_facts.start()
        )

        self.mock_execute_show_command = patch(
            "ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.ospfv2.ospfv2."
            "Ospfv2Facts.get_ospfv2_data",
        )
        self.execute_show_command = self.mock_execute_show_command.start()

    def tearDown(self):
        super(TestIxModule, self).tearDown()
        self.mock_get_resource_connection_facts.stop()
        self.mock_execute_show_command.stop()

    def test_ix_ospfv2_merged(self):
        self.execute_show_command.return_value = dedent(
            """\
            ip router ospf 1
              compatible rfc1583
              rib max-entries 128
              default metric 100
              area 0
            """
        )
        set_module_args(
            dict(
                config=dict(
                    processes=[
                        dict(
                            process_id=1,
                            rib=(dict(max_entries=256)),
                            default_metric=100,
                            passive_interfaces=["GigaEthernet1.0"],
                            areas=[
                                dict(
                                    area_id=0,
                                    virtual_links=[
                                        dict(
                                            address="192.0.2.1",
                                            authentication=dict(
                                                auth_type="text",
                                                text_passowrd="password",
                                            ),
                                        )
                                    ],
                                )
                            ],
                            networks=[
                                dict(
                                    address="192.0.2.128/25",
                                    area=0,
                                )
                            ],
                        )
                    ]
                ),
                state="merged",
            )
        )
        commands = [
            "ip router ospf 1",
            "network 192.0.2.128/25 area 0",
            "passive-interface GigaEthernet1.0",
            "area 0",
            "area 0 virtual-link 192.0.2.1 authentication authentication-key password dead-interval 40 hello-interval 10",
        ]
        result = self.execute_module(changed=True)
        self.assertEqual(sorted(commands), sorted(result["commands"]))

    def test_ix_ospfv2_merged_independent(self):
        self.execute_show_command.return_value = dedent(
            """\
            ip router ospf 1
              compatible rfc1583
              default-metric 100
              rib max-entries 128
              passive-interface GigaEthernet1.0
              area 0
              area 1
              area 2
              area 2 nssa
              area 0 virtual-link 192.0.2.1 hello-interval 20 dead-interval 100 authentication message-digest message-digest-key 1 ABCDEFGHIJK
              network 192.0.2.128/25 area 0
              network 198.51.100.0/24 area 1
            """,
        )

    def test_ix_ospfv2_replaced(self):
        self.execute_show_command.return_value = dedent(
            """\
            ip router ospf 1
              compatible rfc1583
              default-metric 100
              rib max-entries 128
              passive-interface GigaEthernet1.0
              area 0
              area 1
              area 2
              area 2 nssa
              area 0 virtual-link 192.0.2.1 hello-interval 20 dead-interval 100 authentication message-digest message-digest-key 1 ABCDEFGHIJK
              network 192.0.2.128/25 area 0
              network 198.51.100.0/24 area 1
            """,
        )

    def test_ix_ospfv2_replaced_independent(self):
        """"""

    def test_ix_ospfv2_overriden(self):
        """"""

    def test_ix_ospfv2_overriden_independent(self):
        """"""

    def test_ix_ospfv2_deleted(self):
        """"""

    def test_ix_ospfv2_parsed(self):
        """"""

    def test_ix_ospfv2_rendered(self):
        """"""
