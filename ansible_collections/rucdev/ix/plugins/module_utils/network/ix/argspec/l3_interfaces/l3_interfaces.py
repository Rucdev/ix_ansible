__metaclass__ = type
#
# -*- coding: utf-8 -*-
# Copyright 2023 AP Communications
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
The arg spec for the ix_l3_interfaces module
"""


class L3_interfacesArgs(object):  # pylint: disable=R0903
    """The arg spec for the ix_l3_interfaces module"""

    def __init__(self, **kwargs):
        pass

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "ipv4": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "address": {"type": "str"},
                        "dhcp": {
                            "options": {"enable": {"type": "bool"}},
                            "type": "dict",
                        },
                        "mtu": {"type": "int"},
                        "secondary": {"type": "bool"},
                    },
                },
                "ipv6": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "address": {"type": "str"},
                        "anycast": {"type": "bool"},
                        "autoconfig": {
                            "options": {
                                "default": {"type": "bool"},
                                "enable": {"type": "bool"},
                            },
                            "type": "dict",
                        },
                        "eui": {"type": "bool"},
                    },
                },
                "name": {"required": True, "type": "str"},
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "choices": [
                "merged",
                "replaced",
                "overridden",
                "deleted",
                "rendered",
                "gathered",
                "parsed",
            ],
            "default": "merged",
            "type": "str",
        },
    }  # pylint: disable=C0301
