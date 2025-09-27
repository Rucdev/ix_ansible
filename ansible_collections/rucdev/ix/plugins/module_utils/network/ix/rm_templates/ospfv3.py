# -*- coding: utf-8 -*-
# Copyright 2024 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The Ospfv3 parser templates file. This contains
a list of parser definitions and associated functions that
facilitates both facts gathering and native command generation for
the given network resource.
"""

import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Ospfv3Template(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Ospfv3Template, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "pid",
            "getval": re.compile(
                r"""
                ^ipv6\srouter\sospf\s(?P<pid>\d+)
                $""", re.VERBOSE),
            "setval": "ipv6 router ospf {{ process_id }}",
            "result": {
                "processes": {
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
                "processes": {
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
                "processes": {
                    "{{ pid }}": {
                        "areas": {
                            "{{ area_id }}": {
                                "area_id": "{{ area_id }}",
                                "default_cost": "{{ default_cost }}"
                            }
                        },
                    },
                },
            },
        },
        {
            "name": "ranges",
            "getval": re.compile(
                r"""
                \s+area
                (\s(?P<area_id>\S+))
                (\srange)
                (\s(?P<address>\S+))
                (\s(?P<not_advertise>not-advertise))?
                $""",
                re.VERBOSE
            ),
            "setval": "area {{ area_id }} range {{ address }} {{ 'advertise' if advertise else 'not-advertise' }}",
            "result": {
                "processes": {
                    "{{ pid }}": {
                        "areas": {
                            "{{ area_id }}": {
                                "area_id": "{{ area_id }}",
                                "ranges": [
                                    {
                                        "address": "{{ address }}",
                                        "advertise": "{{ False if not_advertise is defined else True }}"
                                    }
                                ]
                            }
                        },
                    },
                }
            }
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
            "{{ (' no-summary') if stub.no_summary is defined and stub.no_summary else '' }}",
            "result": {
                "processes": {
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
            "name": "distance",
            "getval": re.compile(
                r"""
                \s+distance
                (\sexternal\s(?P<external>\S+))?
                (\sinter-area\s(?P<inter_area>\S+))?
                (\sintra-area\s(?P<intra_area>\S+))?
                $""", re.VERBOSE),
            "setval": "distance"
            "{{ ' external ' + distance.external|string if distance.external is defined }}"
            "{{ ' inter-area ' + distance.inter_area|string if distance.inter_area is defined }}"
            "{{ ' intra-area ' + distance.intra_area|string if distance.intra_area is defined }}",
            "result": {
                "processes": {
                    "{{ pid }}": {
                        "distance": {
                            "external": "{{ external }}",
                            "inter_area": "{{ inter_area }}",
                            "intra_area": "{{ intra_area }}",
                        }
                    },
                },
            },
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
                "processes": {
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
            "name": "originate_default",
            "getval": re.compile(
                r"""
                \s+originate-default
                (\s(?P<always>always))?
                (\smetric\s(?P<metric>\S+))
                (\smetric-type\s(?P<metric_type>\d))?
                (\sroute-map\s(?P<route_map>\S+))?
                $""",
                re.VERBOSE
            ),
            "setval": "originate-default{{ ' always' if originate_default.always is defined and originate_default.always else '' }}"
            " metric {{ originate_default.metric }}"
            " metric-type {{ originate_default.metric_type }}"
            " route-map {{ originate_default.route_map }}",
            "result": {
                "processes": {
                    "{{ pid }}": {
                        "originate_default": {
                            "always": "{{ True if always is defined }}",
                            "metric": "{{ metric }}",
                            "metric_type": "{{ metric_type }}",
                            "route_map": "{{ route_map }}",
                        }
                    }
                }
            }
        },
        {
            "name": "passive_interfaces",
            "getval": re.compile(
                r"""
                \s+passive-interface
                (\s(?P<interface>\S+))?
                $""",
                re.VERBOSE
            ),
            "setval": "passive-interface {{ interface }}",
            "result": {
                "processes": {
                    "{{ pid }}": {
                        "passive_interfaces": [
                            "{{ interface }}",
                        ]
                    }
                }
            }
        },
        {
            "name": "router_id",
            "getval": re.compile(
                r"""
                \s+router-id
                (\s(?P<router_id>\S+))?
                $""",
                re.VERBOSE
            ),
            "setval": "router-id {{ router_id }}",
            "result": {
                "processes": {
                    "{{ pid }}": {
                        "router_id": "{{ router_id }}"
                    }
                }
            }
        },
        {
            "name": "timers",
            "getval": re.compile(
                r"""
                \s+timers
                (\sdelay\s(?P<delay>\S+))?
                (\shold\s(?P<hold>\S+))?
                $""",
                re.VERBOSE
            ),
            "setval": "timers"
            "{{ ' delay ' + timers.delay|string if timers.delay is defined else '' }}"
            "{{ ' hold ' + timers.hold|string if timers.hold is defined else '' }}",
            "result": {
                "processes": {
                    "{{ pid }}": {
                        "timers": {
                            "delay": "{{ delay }}",
                            "hold": "{{ hold }}"
                        }
                    }
                }
            }
        }
    ]
    # fmt: on
