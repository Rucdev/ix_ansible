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
                \s+area\s(?P<area_id>\S+)
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
            "getval":re.compile(
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
        }
    ]
    # fmt: on
