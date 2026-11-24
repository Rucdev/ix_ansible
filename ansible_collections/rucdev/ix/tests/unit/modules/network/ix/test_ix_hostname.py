#
# -*- coding: utf-8 -*-
# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

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
    module = ix_hostname

    def setUp(self):
        super(TestIxHostnameModule, self).setUp()

        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base."
            "get_resource_connection"
        )
        self.get_resource_connection_facts = (
            self.mock_get_resource_connection_facts.start()
        )

        self.mock_execute_show_command = patch(
            "ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.hostname.hostname."
            "HostnameFacts.get_hostname_data"
        )
        self.execute_show_command = self.mock_execute_show_command.start()

    def tearDown(self):
        super(TestIxHostnameModule, self).tearDown()
        self.mock_get_resource_connection_facts.stop()
        self.mock_execute_show_command.stop()

    def test_ix_hostname_merged(self):
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args(dict(config=dict(hostname="Router2"), state="merged"))
        self.execute_module(changed=True, commands=["hostname Router2"])

    def test_ix_hostname_merged_from_empty(self):
        self.execute_show_command.return_value = "timezone +09 00\n"
        set_module_args(dict(config=dict(hostname="Router2"), state="merged"))
        self.execute_module(changed=True, commands=["hostname Router2"])

    def test_ix_hostname_merged_idempotent(self):
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args(dict(config=dict(hostname="Router1"), state="merged"))
        self.execute_module(changed=False, commands=[])

    def test_ix_hostname_replaced(self):
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args(dict(config=dict(hostname="Router2"), state="replaced"))
        self.execute_module(changed=True, commands=["hostname Router2"])

    def test_ix_hostname_replaced_idempotent(self):
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args(dict(config=dict(hostname="Router1"), state="replaced"))
        self.execute_module(changed=False, commands=[])

    def test_ix_hostname_overridden(self):
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args(dict(config=dict(hostname="Router2"), state="overridden"))
        self.execute_module(changed=True, commands=["hostname Router2"])

    def test_ix_hostname_overridden_idempotent(self):
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args(dict(config=dict(hostname="Router1"), state="overridden"))
        self.execute_module(changed=False, commands=[])

    def test_ix_hostname_deleted(self):
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args(dict(state="deleted"))
        self.execute_module(changed=True, commands=["no hostname"])

    def test_ix_hostname_deleted_idempotent(self):
        self.execute_show_command.return_value = "timezone +09 00\n"
        set_module_args(dict(state="deleted"))
        self.execute_module(changed=False, commands=[])

    def test_ix_hostname_rendered(self):
        set_module_args(dict(config=dict(hostname="Router1"), state="rendered"))
        result = self.execute_module(changed=False)
        self.assertEqual(result["rendered"], ["hostname Router1"])

    def test_ix_hostname_parsed(self):
        set_module_args(dict(running_config=RUNNING_CONFIG, state="parsed"))
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], {"hostname": "Router1"})

    def test_ix_hostname_parsed_ignores_indented_lines(self):
        set_module_args(dict(running_config=" hostname NotThis\n", state="parsed"))
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], {})

    def test_ix_hostname_gathered(self):
        self.execute_show_command.return_value = RUNNING_CONFIG
        set_module_args(dict(state="gathered"))
        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"], {"hostname": "Router1"})
