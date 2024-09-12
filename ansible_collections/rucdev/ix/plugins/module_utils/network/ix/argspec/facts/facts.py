__metaclass__ = type
#
# -*- coding: utf-8 -*-
# Copyright 2023 AP Communications
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The arg spec for the ix facts module.
"""


class FactsArgs(object):  # pylint: disable=R0903
    """The arg spec for the ix facts module"""

    def __init__(self, **kwargs):
        pass

    choices = ["all", "interfaces", "l3_interfaces", "ospfv2"]

    argument_spec = {
        "gather_subset": dict(default=["min"], type="list"),
        "gather_network_resources": dict(choices=choices, type="list"),
    }
