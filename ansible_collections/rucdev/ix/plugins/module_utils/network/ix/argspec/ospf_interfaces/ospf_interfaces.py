# -*- coding: utf-8 -*-
# Copyright 2025 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

#############################################
#                WARNING                    #
#############################################
#
# This file is auto generated by the
# cli_rm_builder.
#
# Manually editing this file is not advised.
#
# To update the argspec make the desired changes
# in the module docstring and re-run
# cli_rm_builder.
#
#############################################

"""
The arg spec for the ix_ospf_interfaces module
"""


class Ospf_interfacesArgs(object):  # pylint: disable=R0903
    """The arg spec for the ix_ospf_interfaces module
    """

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "name": {"type": "str", "required": True},
                "address_family": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "afi": {"type": "str", "choices": ["ipv4", "ipv6"]},
                        "authentication": {"type": "str"},
                        "authentication_key": {"type": "str"},
                        "cost": {"type": "int"},
                        "hello_interval": {"type": "int"},
                        "dead_interval": {"type": "int"},
                        "message_digest_key": {
                            "type": "dict",
                            "options": {
                                "key_id": {"type": "int"},
                                "password": {"type": "str"},
                            },
                        },
                        "mtu_ignore": {"type": "bool"},
                        "neighbor_v2": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "interval": {"type": "int", "default": 120},
                                "priority": {"type": "int", "default": 1},
                                "router_id": {"type": "str"},
                            },
                        },
                        "neighbor_v3": {
                            "type": "list",
                            "elements": "dict",
                            "options": {
                                "address": {"type": "str"},
                                "interval": {"type": "int", "default": 120},
                                "priority": {"type": "int", "default": 1},
                                "process_id": {"type": "int"},
                                "router_id": {"type": "str"},
                            },
                        },
                        "interface_type": {
                            "type": "str",
                            "choices": [
                                "broadcast",
                                "default",
                                "non-broadcast",
                                "point-to-point",
                            ],
                        },
                        "priority": {"type": "int"},
                        "retransmit_interval": {"type": "int"},
                        "transmit_delay": {"type": "int"},
                    },
                },
            },
        },
        "running_config": {"type": "str"},
        "state": {"type": "str", "default": "merged"},
    }  # pylint: disable=C0301
