# -*- coding: utf-8 -*-
# Copyright 2024 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The Ospfv2 parser templates file. This contains
a list of parser definitions and associated functions that
facilitates both facts gathering and native command generation for
the given network resource.
"""

import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


def _tmplt_ospf_virtual_link(config_data):
    if "virtual_link" in config_data:
        virtual_link_data = config_data["virtual_link"]
        command = "area {area_id} virtual-link {address}".format(**virtual_link_data)
        if "authentication" in virtual_link_data:
            command += " authentication {authentication}".format(**virtual_link_data)
        if (
            "message_digest" in virtual_link_data
            and virtual_link_data.get("authentication") == "message-digest"
        ):
            command += " message-digest-key {key_id} {password}".format(
                **virtual_link_data["message_digest"]
            )
        if "dead_interval" in virtual_link_data:
            command += " dead_interval {dead_interval}".format(**virtual_link_data)
        if "hello_interval" in virtual_link_data:
            command += " hello_interval {hello_interval}".format(**virtual_link_data)
        if "retransmit_interval" in virtual_link_data:
            command += " retransmit_interval {retransmit_interval}".format(
                **virtual_link_data
            )
        if "transmit_delay" in virtual_link_data:
            command += " transmit_delay {transmit_delay}".format(**virtual_link_data)
        return command


class Ospfv2Template(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Ospfv2Template, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "pid",
            "getval": re.compile(
                r"""
                ^ip\srouter\sospf
                (\s(?P<pid>\d+))
                $""", re.VERBOSE),
            "setval": "ip router ospf {{ process_id }}",
            "result": {
                "processes":{
                    "{{ pid }}": {"process_id": "{{ pid | int }}"}
                }
            },
            "shared": True
        },
        {
            "name": "area_id",
            "getval": re.compile(
                r"""
                \s+area
                (\s(?P<area_id>\S+))
                $""", re.VERBOSE),
            "setval": "area {{ area_id }}",
            "result": {
                "processes":{
                    "{{ pid }}": {
                        "areas": {
                            "{{ area_id }}": {
                                "area_id": "{{ area_id }}"
                            }
                        },
                    },
                },
            },
        },
        {
            "name": "default_cost",
            "getval": re.compile(
                r"""
                \s+area\s(?P<area_id>\S+)
                \sdefault-cost
                (\s(?P<default_cost>\S+))?
                $""", re.VERBOSE),
            "setval": "area {{ area_id }} default-cost {{ default_cost }}",
            "result": {
                "processes":{
                    "{{ pid }}": {
                        "areas": {
                            "{{ area_id }}": {
                                "area_id": "{{ area_id }}",
                                "default_cost": "{{ default_cost | int }}"
                            }
                        },
                    },
                },
            },
        },
        {
            "name":"nssa",
            "getval": re.compile(
                r"""
                \s+area\s(?P<area_id>\S+)
                (\s(?P<nssa>nssa))?
                (\s(?P<no_summary>no-summary))?
                (\sstability-interval\s(?P<stability_interval>\d+))?
                (\s(?P<translate>translate))?
                (\sdefault-metric\s(?P<default_metric>\d+))?
                (\sdefault-metric-type\s(?P<default_metric_type>\d))?
                $""",
                re.VERBOSE,
            ),
            "result": {
                "processes":{
                    "{{ pid }}": {
                        "areas": {
                            "{{ area_id }}": {
                                "area_id": "{{ area_id }}",
                                "nssa": {
                                    "no_summary": "{{ True if no_summary is defined }}",
                                    "stability_interval": "{{ stability_interval }}",
                                    "translate": "{{ True if translate is defined }}",
                                    "default_metric": "{{ default_metric }}",
                                }
                            }
                        },
                    },
                },
            },
        },
        {
            "name": "stub",
            "getval": re.compile(
                r"""
                \s+area
                (\s(?P<area_id>\S+))
                (\s(?P<stub>stub))?
                (\s(?P<no_sum>no-summary))?
                $""",
                re.VERBOSE,
            ),
            "setval": "area {{ area_id }} stub"
            "{{ (' no-summary') if stub.no_summary else '' }}",
            "result": {
                "processes":{
                    "{{ pid }}": {
                        "areas": {
                            "{{ area_id }}": {
                                "area_id": "{{ area_id }}",
                                "stub": {
                                    "set": "{{ True if stub is defined and no_sum is undefined }}",
                                    "no_summary": "{{ True if no_sum is defined }}"
                                }
                            }
                        },
                    },
                },
            }
        },
        {
            "name": "virtual_links",
            "getval": re.compile(
                r"""
                \s+area
                (\s(?P<area_id>\S+))
                \svirtual-link
                (\s(?P<address>\S+))
                (\s(?P<authentication>authentication)(\s(?P<auth_type>\S+))?)?
                (\sauthentication-key\s(?P<password>\S+))?
                (\smessage-digest-key\s(?P<message_digest_key_id>\d+)\s(?P<message_digest_password>\S+))?
                (\shello-interval\s(?P<hello_interval>\S+))?
                (\sdead-interval\s(?P<dead_interval>\S+))?
                (\sretransmit-interval\s(?P<retransmit_interval>\S+))?
                (\stransmit-delay\s(?P<transmit_delay>\S+))?
                $""",
                re.VERBOSE,
            ),
            "setval": _tmplt_ospf_virtual_link,
            "result": {
                "processes": {
                    "{{ pid }}": {
                        "areas": {
                            "{{ area_id }}": {
                                "area_id": "{{ area_id }}",
                                "virtual_links": [
                                    {
                                        "address": "{{ address }}",
                                        "authentication": {
                                            "auth_type": "{{ auth_type if auth_type is defined else 'text' if authentication is defined }}",
                                            "text_password": "{{ password }}",
                                            "message_digest_key_id": "{{ message_digest_key_id }}",
                                            "message_digest_password": "{{ message_digest_password }}",
                                        },
                                        "hello_interval": "{{ hello_interval }}",
                                        "dead_interval": "{{ dead_interval }}",
                                    }
                                ]
                            }
                        },
                    },
                },
            }
        },
        {
            "name": "compatible",
            "getval": re.compile(
                r"""
                \s+compatible(\s(?P<rfc1583>rfc1583))
                $""",
                re.VERBOSE
                ),
            "setval": "compatible {{ 'rfc1583' if rfc1583 }}",
            "result": {
                "processes": {
                    "{{ pid }}": {
                        "compatible": {
                            "rfc1583": "{{ true if rfc1583 is defined }}"
                        }
                    }
                }
            },
        },
        {
            "name": "default_metric",
            "getval": re.compile(
                r"""
                \s+default-metric\s(?P<metric>\S+)
                $""", re.VERBOSE),
            "setval": "default-metric {{ default_metric }}",
            "result": {
                "processes":{
                    "{{ pid }}": {
                            "default_metric": "{{ metric }}"
                        },
                    },
                },
        },
        {
            "name": "distance",
            "getval": re.compile(
                r"""
                \s+distance
                (\sexternal\s(?P<external>\S+))?
                (\sinter-area\s(?P<inter_area>\S+))?
                (\sintra-area\s(?P<intra_area>\S+))?
                (\snssa-external\s(?P<nssa_external>\S+))?
                $""", re.VERBOSE),
            "setval": "default-metric {{ metric }}",
            "result": {
                "processes":{
                    "{{ pid }}": {
                            "distance": {
                                "external": "{{ external }}",
                                "inter_area": "{{ inter_area }}",
                                "intra_area": "{{ intra_area }}",
                                "nssa_external": "{{ nssa_external }}",
                            }
                        },
                    },
                },
        },
        {
            "name": "distribute_list",
            "getval": re.compile(
                r"""
                \s+distribute-list\s
                (prefix\s(?P<prefix_list>\S+))?
                (route-map\s(?P<route_map>\S+))?
                $""",
                re.VERBOSE
            ),
            "setval": "",
            "result": {
                "processes":{
                    "{{ pid }}": {
                        "distribute_list": {
                            "prefix": "{{ prefix_list}}",
                            "route_map": "{{ route_map }}",
                        }
                    }
                }
            }
        },
        {
            "name": "network",
            "getval": re.compile(
                r"""
                \s+network
                \s(?P<address>\S+)
                \sarea\s(?P<area>\S+)
                $""",
                re.VERBOSE
            ),
            "setval": "network {{ address }} area {{ area }}",
            "result": {
                "processes":{
                    "{{ pid }}": {
                        "network": [
                            {
                                "address": "{{ address }}",
                                "area": "{{ area }}"
                            }
                        ]
                    }
                }
            }
        },
        {
            "name": "nssa_range",
            "getval": re.compile(
                r"""
                \s+nssa-range
                \s(?P<range>\S+)
                (\s(?P<not_advertise>not-advertise))?
                (\stag\s(?P<tag>\S+))?
                $""",
                re.VERBOSE
            ),
            "setval": "nssa-range {{ range }}{{ ' not-advertise' if not_advertise }}{{ ' ' + tag if tag is defined}}",
            "result": {
                "processes":{
                    "{{ pid }}": {
                        "nssa_range": [
                            {
                                "range": "{{ range }}",
                                "not_advertise": "{{ True if not_advertise is defined }}",
                                "tag": "{{ tag if tag is defined }}"
                            }
                        ]
                    }
                }
            }
        }
    ]
    # fmt: on
