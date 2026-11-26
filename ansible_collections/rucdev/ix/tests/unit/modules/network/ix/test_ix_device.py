#
# -*- coding: utf-8 -*-
# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from textwrap import dedent
from unittest.mock import patch

from ansible_collections.rucdev.ix.plugins.modules import ix_device
from ansible_collections.rucdev.ix.tests.unit.modules.utils import set_module_args

from .ix_module import TestIxModule

# "show running-config device" on IX2215 (10.10.29). GigaEthernet2 is an
# 8-port switch, so IX writes speed/duplex/mdi-mdix once per port.
RUNNING_CONFIG = dedent("""\
    device GigaEthernet0
    !
    device GigaEthernet1
    !
    device GigaEthernet2
      port 1 mdi-mdix mdi
      port 1 speed 100
      port 1 duplex full
      port 2 mdi-mdix mdi
      port 2 speed 100
      port 2 duplex full
      keepalive 10 3
      output-buffer 100
    !
    device BRI0
      isdn switch-type hsd128k
    !
    device USB0
      shutdown
    !
    """)

GE2 = {
    "name": "GigaEthernet2",
    "duplex": "full",
    "keepalive": {"down_notification_time": 10, "down_notification_count": 3},
    "mdix": "mdi",
    "output_buffer": 100,
    "speed": "100",
}

PARSED = [
    {"name": "BRI0"},
    {"name": "GigaEthernet0"},
    {"name": "GigaEthernet1"},
    GE2,
    {"name": "USB0"},
]


class TestIxDeviceModule(TestIxModule):
    module = ix_device

    def setUp(self):
        super(TestIxDeviceModule, self).setUp()
        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base."
            "get_resource_connection"
        )
        self.mock_get_resource_connection.start()
        self.mock_get_data = patch(
            "ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.device.device."
            "DeviceFacts.get_device_data"
        )
        self.get_data = self.mock_get_data.start()
        self.get_data.return_value = RUNNING_CONFIG
        self.maxDiff = None

    def tearDown(self):
        super(TestIxDeviceModule, self).tearDown()
        self.mock_get_resource_connection.stop()
        self.mock_get_data.stop()

    # ---- read ----
    def test_parsed(self):
        set_module_args(dict(running_config=RUNNING_CONFIG, state="parsed"))
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], PARSED)

    def test_parsed_no_device(self):
        set_module_args(dict(running_config="hostname ix\n", state="parsed"))
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], [])

    def test_gathered(self):
        set_module_args(dict(state="gathered"))
        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"], PARSED)

    def test_gathered_does_not_invent_defaults(self):
        # Devices without explicit settings must not report duplex/mdix
        # values, or deleted/overridden would try to negate them.
        self.get_data.return_value = "device GigaEthernet2\n!\n"
        set_module_args(dict(state="gathered"))
        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"], [{"name": "GigaEthernet2"}])

    def test_rendered(self):
        set_module_args(dict(config=[GE2], state="rendered"))
        result = self.execute_module(changed=False)
        self.assertEqual(
            result["rendered"],
            [
                "device GigaEthernet2",
                "duplex full",
                "mdi-mdix mdi",
                "output-buffer 100",
                "speed 100",
                "keepalive 10 3",
            ],
        )

    def test_sflow_parsed_and_rendered(self):
        cfg = dedent("""\
            device GigaEthernet2
              sflow max-header-size 64
              sflow polling-interval 30
              sflow sampling-rate 512 in
              sflow sampling-rate 1024 out
            !
            """)
        sflow = {
            "max_header_size": 64,
            "polling_interval": 30,
            "sampling_rate": {"in": 512, "out": 1024},
        }
        set_module_args(dict(running_config=cfg, state="parsed"))
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], [{"name": "GigaEthernet2", "sflow": sflow}])

        set_module_args(
            dict(config=[{"name": "GigaEthernet2", "sflow": sflow}], state="rendered")
        )
        result = self.execute_module(changed=False)
        self.assertEqual(
            result["rendered"],
            [
                "device GigaEthernet2",
                "sflow max-header-size 64",
                "sflow polling-interval 30",
                "sflow sampling-rate 512 in",
                "sflow sampling-rate 1024 out",
            ],
        )

    # ---- merged ----
    def test_merged(self):
        set_module_args(
            dict(
                config=[
                    {"name": "GigaEthernet1", "speed": "1000", "duplex": "full"},
                    {
                        "name": "GigaEthernet2",
                        "keepalive": {
                            "down_notification_time": 20,
                            "down_notification_count": 5,
                        },
                    },
                ],
                state="merged",
            )
        )
        self.execute_module(
            changed=True,
            commands=[
                "device GigaEthernet1",
                "duplex full",
                "speed 1000",
                "device GigaEthernet2",
                "keepalive 20 5",
            ],
            sort=False,
        )

    def test_merged_keepalive_restore_default(self):
        # "no keepalive" would disable keepalive; the defaults clear the line
        set_module_args(
            dict(
                config=[
                    {
                        "name": "GigaEthernet2",
                        "keepalive": {
                            "down_notification_time": 4,
                            "down_notification_count": 3,
                        },
                    }
                ],
                state="merged",
            )
        )
        self.execute_module(
            changed=True,
            commands=["device GigaEthernet2", "keepalive 4 3"],
            sort=False,
        )

    def test_merged_idempotent(self):
        set_module_args(dict(config=[GE2], state="merged"))
        self.execute_module(changed=False, commands=[])

    def test_merged_partial_idempotent(self):
        set_module_args(
            dict(config=[{"name": "GigaEthernet2", "speed": "100"}], state="merged")
        )
        self.execute_module(changed=False, commands=[])

    # ---- replaced ----
    def test_replaced(self):
        set_module_args(
            dict(config=[{"name": "GigaEthernet2", "mdix": "mdi"}], state="replaced")
        )
        self.execute_module(
            changed=True,
            commands=[
                "device GigaEthernet2",
                "no duplex full",
                "keepalive 4 3",
                "no output-buffer 100",
                "no speed 100",
            ],
        )

    def test_replaced_idempotent(self):
        set_module_args(dict(config=[GE2], state="replaced"))
        self.execute_module(changed=False, commands=[])

    # ---- overridden ----
    def test_overridden(self):
        set_module_args(
            dict(config=[{"name": "GigaEthernet1", "speed": "100"}], state="overridden")
        )
        self.execute_module(
            changed=True,
            commands=[
                "device GigaEthernet2",
                "no duplex full",
                "keepalive 4 3",
                "no mdi-mdix mdi",
                "no output-buffer 100",
                "no speed 100",
                "device GigaEthernet1",
                "speed 100",
            ],
        )

    def test_overridden_idempotent(self):
        set_module_args(dict(config=PARSED, state="overridden"))
        self.execute_module(changed=False, commands=[])

    # ---- deleted ----
    def test_deleted_one(self):
        set_module_args(dict(config=[{"name": "GigaEthernet2"}], state="deleted"))
        self.execute_module(
            changed=True,
            commands=[
                "device GigaEthernet2",
                "no duplex full",
                "keepalive 4 3",
                "no mdi-mdix mdi",
                "no output-buffer 100",
                "no speed 100",
            ],
        )

    def test_deleted_all(self):
        set_module_args(dict(state="deleted"))
        self.execute_module(
            changed=True,
            commands=[
                "device GigaEthernet2",
                "no duplex full",
                "keepalive 4 3",
                "no mdi-mdix mdi",
                "no output-buffer 100",
                "no speed 100",
            ],
        )

    def test_deleted_idempotent(self):
        self.get_data.return_value = (
            "device GigaEthernet2\n!\ndevice USB0\n  shutdown\n!\n"
        )
        set_module_args(dict(state="deleted"))
        self.execute_module(changed=False, commands=[])

    def test_purged_not_supported(self):
        # IX rejects "no device X" (verified on IX2215 10.10.29)
        set_module_args(dict(config=[{"name": "GigaEthernet2"}], state="purged"))
        self.execute_module(failed=True)
