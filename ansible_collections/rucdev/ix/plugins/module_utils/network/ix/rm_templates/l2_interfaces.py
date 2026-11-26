# -*- coding: utf-8 -*-
# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The L2_interfaces parser templates file. This contains
a list of parser definitions and associated functions that
facilitates both facts gathering and native command generation for
the given network resource.
"""

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class L2_interfacesTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(L2_interfacesTemplate, self).__init__(
            lines=lines, tmplt=self, module=module
        )

    # fmt: off
    PARSERS = [
        {
            "name": "name",
            "getval": re.compile(
                r"""
                ^interface\s(?P<name>\S+)
                \s*$""", re.VERBOSE),
            "setval": "interface {{ name }}",
            "result": {"{{ name }}": {"name": "{{ name }}"}},
            "shared": True,
        },
        {
            # IX always shows the TPID, e.g. "encapsulation dot1q 10 tpid 8100"
            "name": "dot1q",
            "getval": re.compile(
                r"""
                ^\s+encapsulation\sdot1q
                \s(?P<vlan_id>\d+)
                (\stpid\s(?P<tpid>\S+))?
                \s*$""", re.VERBOSE),
            "setval": "encapsulation dot1q {{ dot1q.vlan_id }}"
                      "{{ ' tpid ' + dot1q.tpid if dot1q.tpid is defined and dot1q.tpid else '' }}",
            "result": {
                "{{ name }}": {
                    "dot1q": {
                        "vlan_id": "{{ vlan_id }}",
                        "tpid": "{{ tpid }}",
                    },
                },
            },
        },
        {
            # Only the membership line; "bridge-group N port-protected" and
            # "bridge-group N port-table-size S" are not managed.
            "name": "bridge_group",
            "getval": re.compile(
                r"""
                ^\s+bridge-group\s(?P<group>\d+)
                \s*$""", re.VERBOSE),
            "setval": "bridge-group {{ bridge_group.group }}",
            "result": {
                "{{ name }}": {
                    "bridge_group": {
                        "group": "{{ group }}",
                    },
                },
            },
        },
    ]
    # fmt: on
