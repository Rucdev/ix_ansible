# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type

"""
The Interfaces parser templates file. This contains
a list of parser definitions and associated functions that
facilitates both facts gathering and native command generation for
the given network resource.
"""

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Device_interfacesTemplate(NetworkTemplate):
    def __init__(self, lines=None, tmplt=None, prefix=None, module=None):
        super(Device_interfacesTemplate, self).__init__(
            lines, tmplt=self, module=module
        )

    PARSERS = [
        {
            "name": "device",
            "getval": re.compile(
                r"""
                ^device\s(?P<name>\S+)$""",
                re.VERBOSE,
            ),
            "setval": "device {{ name }}",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                },
            },
            "shared": True,
        },
        {
            "name": "duplex",
            "getval": re.compile(
                r"""
                ^\s+(port\s\d\s)?duplex\s(?P<duplex>.+)$""",
                re.VERBOSE,
            ),
            "setval": "duplex {{ duplex }}",
            "result": {
                "{{ name }}": {
                    "duplex": "{{ duplex }}",
                },
            },
        },
        {
            "name": "keepalive",
            "getval": re.compile(
                r"""
                    ^\s+(port\s\d\s)?keepalive\s(?P<down_notification_time>\d+)\s(?P<down_notification_count>\d+)$""",
                re.VERBOSE,
            ),
            "setval": "keepalive {{ down_notification_time }} {{ down_notification_count }}",
            "result": {
                "{{ name }}": {
                    "keepalive": [
                        {
                            "down_notification_time": "{{ down_notification_time }}",
                            "down_notification_count": "{{ down_notification_count }}",
                        }
                    ],
                },
            },
        },
        {
            "name": "mdix",
            "getval": re.compile(
                r"""
                ^\s+(port\s\d\s)?mdi-mdix\s(?P<mdix>.+)$""",
                re.VERBOSE,
            ),
            "setval": "mdi-mdix {{ mdix }}",
            "result": {
                "{{ name }}": {
                    "mdix": "{{ mdix }}",
                },
            },
        },
        {
            "name": "output_buffer",
            "getval": re.compile(
                r"""
                ^\s+output-buffer\s(?P<output_buffer>.+)$""",
                re.VERBOSE,
            ),
            "setval": "output-buffer {{ output_buffer }}",
            "result": {
                "{{ name }}": {
                    "output_buffer": "{{ output_buffer }}",
                }
            },
        },
        {
            "name": "sflow.max_header_size",
            "getval": re.compile(
                r"""
                ^\s+(port\s\d\s)?sflow\smax-header-size\s(?P<max_header_size>.+)$""",
                re.VERBOSE,
            ),
            "setval": "sflow max-header-size {{ sflow.max_header_size }}",
            "result": {
                "{{ name }}": {
                    "sflow": {
                        "max_header_size": "{{ max_header_size }}",
                    },
                },
            },
        },
        {
            "name": "sflow.polling_interval",
            "getval": re.compile(
                r"""
                ^\s+(port\s\d\s)?sflow\spolling-interval\s(?P<polling_interval>.+)$""",
                re.VERBOSE,
            ),
            "setval": "sflow polling-interval {{ sflow.polling_interval }}",
            "result": {
                "{{ name }}": {
                    "sflow": {
                        "polling_interval": "{{ polling_interval }}",
                    },
                },
            },
        },
        {
            "name": "sflow.sampling_rate.in",
            "getval": re.compile(
                r"""
                ^\s+(port\s\d\s)?sflow\ssampling-rate\s(?P<sampling_rate_in>.+)\sin$""",
                re.VERBOSE,
            ),
            "setval": "sflow sampling-rate {{ sflow.sampling_rate.in }} in",
            "result": {
                "{{ name }}": {
                    "sflow": {
                        "sampling_rate": {
                            "in": "{{ sampling_rate_in }}",
                        }
                    },
                },
            },
        },
        {
            "name": "sflow.sampling_rate.out",
            "getval": re.compile(
                r"""
                ^\s+(port\s\d\s)?sflow\ssampling-rate\s(?P<sampling_rate_out>.+)\sout$""",
                re.VERBOSE,
            ),
            "setval": "sflow sampling-rate {{ sflow.sampling_rate.out }} out",
            "result": {
                "{{ name }}": {
                    "sflow": {
                        "sampling_rate": {
                            "out": "{{ sampling_rate_out }}",
                        }
                    },
                },
            },
        },
        {
            "name": "speed",
            "getval": re.compile(
                r"""
                ^\s+(port\s\d\s)?speed\s(?P<speed>.+)$""",
                re.VERBOSE,
            ),
            "setval": "speed {{ speed }}",
            "result": {
                "{{ name }}": {
                    "speed": "{{ speed }}",
                },
            },
        },
    ]
