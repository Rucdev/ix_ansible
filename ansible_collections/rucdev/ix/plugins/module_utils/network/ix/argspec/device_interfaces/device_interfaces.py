#
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#############################################
#                WARNING                    #
#############################################
#
# This file is auto generated by the resource
#   module builder playbook.
#
# Do not edit this file manually.
#
# Changes to this file will be over written
#   by the resource module builder.
#
# Changes should be made in the model used to
#   generate this file or in the resource module
#   builder template.
#
#############################################

"""
The arg spec for the ix_device_interfaces module
"""


class Device_interfacesArgs(object):  # pylint: disable=R0903
    """The arg spec for the ix_device_interfaces module"""

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "type": "dict",
            "elements": "dict",
            "options": {
                "duplex": {
                    "choices": ["auto", "full", "half"],
                    "default": "auto",
                    "type": "str",
                },
                "keepalive": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "down_notification_time": {"type": "int"},
                        "down_notification_count": {"type": "int"},
                    },
                },
                "mdix": {"choices": ["mdi", "mdix"], "type": "str", "default": "mdix"},
                "name": {"required": True, "type": "str"},
                "output_buffer": {"type": "int"},
                "sflow": {
                    "type": "dict",
                    "options": {
                        "max_header_size": {"type": "int"},
                        "polling_interval": {"type": "int"},
                        "sampling_rate": {
                            "options": {
                                "in": {"type": "int"},
                                "out": {"type": "int"},
                            },
                        },
                    },
                },
                "speed": {"choices": ["10", "100", "1000", "auto"], "type": "str"},
            },
            "type": "list",
        },
        "reset": {"options": {"name": {"type": "str"}}, "type": "dict"},
        "state": {
            "choices": [
                "merged",
                "replaced",
                "overridden",
                "deleted",
                "rendered",
                "gathered",
                "purged",
                "parsed",
            ],
            "default": "merged",
            "type": "str",
        },
    }  # pylint: disable=C0301