# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


"""The L3 Interfaces parser templates file.

This contains
a list of parser definitions and associated functions that
facilitates both facts gathering and native command generation for
the given network resource.
"""

import re

from typing import ClassVar

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class L3InterfacesTemplate(NetworkTemplate):
    """Parsers and command templates of the ix_l3_interfaces module."""

    def __init__(self, lines=None, module=None) -> None:
        """Set up the template with the parsers of the resource."""
        super().__init__(
            lines=lines,
            tmplt=self,
            module=module,
        )

    PARSERS: ClassVar[list] = [
        {
            "name": "name",
            "getval": re.compile(
                r"""^interface
                    (\s(?P<name>\S+))
                    $""",
                re.VERBOSE,
            ),
            "compval": "name",
            "setval": "interface {{ name }}",
            "result": {"{{ name }}": {"name": "{{ name }}"}},
            "shared": True,
        },
        {
            "name": "ipv4.address",
            "getval": re.compile(
                r"""\s+ip\saddress
                    (\s(?P<ipv4>\S+))
                    (\s(?P<secondary>secondary))?
                    $""",
                re.VERBOSE,
            ),
            "setval": "ip address {{ ipv4.address }}"
            "{{ ' secondary' if ipv4.secondary|d(False) else ''}}",
            "result": {
                "{{ name }}": {
                    "ipv4": [
                        {
                            "address": "{{ ipv4 }}",
                            "secondary": "{{ True if secondary is defined }}",
                        },
                    ],
                },
            },
        },
        {
            "name": "ipv6.address",
            "getval": re.compile(
                r"""\s+ipv6\saddress
                    (\s(?P<ipv6>\S+))
                    (\s(?P<anycast>anycast))?
                    (\s(?P<eui>eui-64))?
                    $""",
                re.VERBOSE,
            ),
            "setval": "ipv6 address {{ ipv6.address }}{{ ' anycast' if ipv6.anycast|d(False) else ''}}"
            "{{' eui-64' if ipv6.eui|d(False) else ''}}",
            "result": {
                "{{ name }}": {
                    "ipv6": [
                        {
                            "address": "{{ ipv6 }}",
                            "anycast": "{{ True if anycast is defined }}",
                            "eui": "{{ True if eui is defined }}",
                        },
                    ],
                },
            },
        },
        {
            "name": "ipv6.autoconfig",
            "getval": re.compile(
                r"""\s+ipv6\saddress
                    (\s(?P<enable>autoconfig))
                    (\s(?P<default>receive-default))?
                    $""",
                re.VERBOSE,
            ),
            "setval": "{{ 'ipv6 address autoconfig' if ipv6.autoconfig.enable|d(False) or ipv6.autoconfig.default|d(False) else ''}}"
            "{{ ' receive-default' if ipv6.autoconfig.default|d(False) else ''}}",
            "result": {
                "{{ name }}": {
                    "ipv6": [
                        {
                            "autoconfig": {
                                "enable": "{{ True if enable is defined }}",
                                "default": "{{ True if default is defined }}",
                            },
                        },
                    ],
                },
            },
        },
    ]
