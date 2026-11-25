# Copyright 2024 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


"""The StaticRoutes parser templates file. This contains
a list of parser definitions and associated functions that
facilitates both facts gathering and native command generation for
the given network resource.

IX syntax (verified on IX2215 10.10.29). Options are keywords; the device
accepts them in any order but shows them in this order in running-config,
and omits default values (distance 1, metric 1):

  ip route [vrf V] <dest|default> [<gateway>] [<interface>]
           [connected] [dhcp] [distance N] [metric N] [tag N]
  ipv6 route <dest|default> [<gateway>[%<interface>]] [<interface>]
           [dhcp] [ra] [distance N] [metric N] [tag N]

A route is identified by dest + gateway + interface (+ connected/dhcp/ra).
Re-entering the same route REPLACES its options, and "no ip route <dest>
<gateway>" removes it regardless of options.
"""

import re

from typing import ClassVar

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)

INTERFACE_RE = r"(?:Tunnel|Loopback|Null|Dialer|BVI|USB-Serial|BRI|GigaEthernet)\S+"

# Parts of a route that identify it (used for deletion, see remval).
IDENTITY_FLAGS = {"ipv4": ("connected", "dhcp"), "ipv6": ("dhcp", "ra")}


def _route_head(data):
    afi = data["afi"]
    cmd = "ip route" if afi == "ipv4" else "ipv6 route"
    if data.get("vrf"):
        cmd += " vrf {vrf}".format(**data)
    cmd += " {dest}".format(**data)
    if data.get("forward_router_address"):
        cmd += " {forward_router_address}".format(**data)
    if data.get("interface"):
        cmd += " {interface}".format(**data)
    for flag in IDENTITY_FLAGS[afi]:
        if data.get(flag):
            cmd += " " + flag
    return cmd


def _tmplt_route(data):
    """Full command in running-config order. Default values are omitted."""
    cmd = _route_head(data)
    for opt in ("distance", "metric", "tag"):
        if data.get(opt) is not None:
            cmd += f" {opt} {data[opt]}"
    return cmd


def _tmplt_route_remove(data):
    """Identity only; IX removes the route regardless of its options."""
    return _route_head(data)


class StaticRoutesTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None) -> None:
        super().__init__(
            lines=lines,
            tmplt=self,
            module=module,
        )

    # fmt: off
    PARSERS: ClassVar[list] = [
        {
            "name": "ipv4",
            "getval": re.compile(
                r"""
                ^ip\sroute
                (\svrf\s(?P<vrf>\S+))?
                \s(?P<dest>\S+)
                (\s(?P<forward_router_address>\d+\.\d+\.\d+\.\d+))?
                (\s(?P<interface>""" + INTERFACE_RE + r"""))?
                (\s(?P<connected>connected))?
                (\s(?P<dhcp>dhcp))?
                (\sdistance\s(?P<distance>\d+))?
                (\smetric\s(?P<metric>\d+))?
                (\stag\s(?P<tag>\d+))?
                \s*$""", re.VERBOSE,
            ),
            "setval": _tmplt_route,
            "remval": _tmplt_route_remove,
            "result": {
                "{{ dest }}_{{ vrf|d() }}_ipv4": [
                    {
                        "_vrf": "{{ vrf }}",
                        "_afi": "ipv4",
                        "_dest": "{{ dest }}",
                        "forward_router_address": "{{ forward_router_address }}",
                        "interface": "{{ interface }}",
                        "connected": "{{ True if connected is defined }}",
                        "dhcp": "{{ True if dhcp is defined }}",
                        "distance": "{{ distance }}",
                        "metric": "{{ metric }}",
                        "tag": "{{ tag }}",
                    },
                ],
            },
        },
        {
            "name": "ipv6",
            "getval": re.compile(
                r"""
                ^ipv6\sroute
                \s(?P<dest>\S+)
                (\s(?P<forward_router_address>[0-9A-Fa-f]*:[0-9A-Fa-f:.]*(%\S+)?))?
                (\s(?P<interface>""" + INTERFACE_RE + r"""))?
                (\s(?P<dhcp>dhcp))?
                (\s(?P<ra>ra))?
                (\sdistance\s(?P<distance>\d+))?
                (\smetric\s(?P<metric>\d+))?
                (\stag\s(?P<tag>\d+))?
                \s*$""", re.VERBOSE,
            ),
            "setval": _tmplt_route,
            "remval": _tmplt_route_remove,
            "result": {
                "{{ dest }}__ipv6": [
                    {
                        "_vrf": None,
                        "_afi": "ipv6",
                        "_dest": "{{ dest }}",
                        "forward_router_address": "{{ forward_router_address }}",
                        "interface": "{{ interface }}",
                        "dhcp": "{{ True if dhcp is defined }}",
                        "ra": "{{ True if ra is defined }}",
                        "distance": "{{ distance }}",
                        "metric": "{{ metric }}",
                        "tag": "{{ tag }}",
                    },
                ],
            },
        },
    ]
    # fmt: on
