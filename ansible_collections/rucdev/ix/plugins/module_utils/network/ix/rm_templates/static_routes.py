# -*- coding: utf-8 -*-
# Copyright 2024 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The Static_routes parser templates file. This contains
a list of parser definitions and associated functions that
facilitates both facts gathering and native command generation for
the given network resource.
"""

import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)

class Static_routesTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Static_routesTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "ipv4",
            "getval": re.compile(
                r"""
                ^ip\sroute
                (\svrf\s(?P<vrf>\S+))?
                (\s(?P<dest>\S+))?
                (\s(?P<forward_router_address>(?!dhcp|tag)(?!(?<!\d\.)\b\d+\b(?!\.\d))(\d{1,3}(\.\d{1,3}){3}|\S+)))?
                (\s(?P<interface>(Tunnel|Loopback|Null|Dialer|BVI|USB-Serial|BRI|GigaEthernet)\S+))?
                (\s(?P<distance_metric>\d+))?
                (\stag\s(?P<tag>\d+))?
                (\s(?P<dhcp>dhcp))?
                $""", re.VERBOSE,
            ),
            "setval": "ip route"
            "{{ (' vrf ' + ipv4.vrf) if ipv4.vrf is defined else '' }}"
            "{{ (' ' + ipv4.dest) if ipv4.dest is defined else '' }}"
            "{{ (' ' + ipv4.forward_router_address) if ipv4.forward_router_address is defined else '' }}"
            "{{ (' ' + ipv4.interface) if ipv4.interface is defined else '' }}"
            "{{ (' ' + ipv4.distance_metric|string) if ipv4.distance_metric is defined else '' }}"
            "{{ (' tag ' + ipv4.tag|string) if ipv4.tag is defined else '' }}"
            "{{ (' name ' + ipv4.name) if ipv4.name is defined else '' }}"
            "{{ (' dhcp' ) if ipv4.dhcp|d(False) else '' }}",
            "result": {
                "{{ dest }}_{{ vrf|d() }}_ipv4": [
                    {
                        "_vrf": "{{ vrf }}",
                        "_afi": "ipv4",
                        "_dest": "{{ dest }}",
                        "interface": "{{ interface }}",
                        "forward_router_address": "{{ forward_router_address }}",
                        "distance_metric": "{{ distance_metric }}",
                        "tag": "{{ tag }}",
                        "dhcp": "{{ not not dhcp }}",
                    },
                ],
            },
        },
        {
            "name": "ipv6",
            "getval": re.compile(
                r"""
                ^ipv6\sroute
                (\svrf\s(?P<vrf>\S+))?
                (\s(?P<dest>\S+))?
                (\s(?P<forward_router_address>(?!dhcp|tag)(?!(?<!\d\.)\b\d+\b(?!\.\d))(\d{1,3}(\.\d{1,3}){3}|\S+)))?
                (\s(?P<interface>(Tunnel|Loopback|Null|Dialer|BVI|USB-Serial|BRI|GigaEthernet)\S+))?
                (\s(?P<distance_metric>\d+))?
                (\stag\s(?P<tag>\d+))?
                (\s(?P<dhcp>dhcp))?
                $""", re.VERBOSE,
            ),
            "setval": "ipv6 route"
            "{{ (' vrf ' + ipv6.vrf) if ipv6.vrf is defined else '' }}"
            "{{ (' ' + ipv6.dest) if ipv6.dest is defined else '' }}"
            "{{ (' ' + ipv6.forward_router_address) if ipv6.forward_router_address is defined else '' }}"
            "{{ (' ' + ipv6.interface) if ipv6.interface is defined else '' }}"
            "{{ (' ' + ipv6.distance_metric|string) if ipv6.distance_metric is defined else '' }}"
            "{{ (' tag ' + ipv6.tag|string) if ipv6.tag is defined else '' }}"
            "{{ (' name ' + ipv6.name) if ipv6.name is defined else '' }}"
            "{{ (' dhcp' ) if ipv6.dhcp|d(False) else '' }}",
            "result": {
                "{{ dest }}_{{ vrf|d() }}_ipv6": [
                    {
                        "_vrf": "{{ vrf }}",
                        "_afi": "ipv6",
                        "_dest": "{{ dest }}",
                        "interface": "{{ interface }}",
                        "forward_router_address": "{{ forward_router_address }}",
                        "distance_metric": "{{ distance_metric }}",
                        "tag": "{{ tag }}",
                        "dhcp": "{{ not not dhcp }}",
                    },
                ],
            },
        },
    ]
    # fmt: on
