# -*- coding: utf-8 -*-
# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The arg spec for the ix_l2_interfaces module
"""


class L2_interfacesArgs(object):  # pylint: disable=R0903
    """The arg spec for the ix_l2_interfaces module"""

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "name": {"type": "str", "required": True},
                "dot1q": {
                    "type": "dict",
                    "options": {
                        "vlan_id": {"type": "int", "required": True},
                        "tpid": {"type": "str"},
                    },
                },
                "bridge_group": {
                    "type": "dict",
                    "options": {
                        "group": {"type": "int", "required": True},
                    },
                },
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": [
                "merged",
                "replaced",
                "overridden",
                "deleted",
                "gathered",
                "rendered",
                "parsed",
            ],
            "default": "merged",
        },
    }  # pylint: disable=C0301
