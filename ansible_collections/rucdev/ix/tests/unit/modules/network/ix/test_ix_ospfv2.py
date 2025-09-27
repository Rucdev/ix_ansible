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
                                            address="",
                                            authentication=dict(
                                                auth_type="text", text_passowrd="password"
                                            ),
                                        )
                                    ],
                                )
                            ],
                            networks=[
                                dict(
                                    address="192.168.0.1"
                                )
                            ]
                        )
                    ]
                ),
                state="merged",
            )
        )

    def test_ix_ospfv2_merged_independent(self):
        """
        Test that the module does not fail when the configuration is merged
        """
        self.execute_show_command.return_value = dedent(
            """\
            ip router
            """,
        )

    def test_ix_ospfv2_replaced(self):
        """"""

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
