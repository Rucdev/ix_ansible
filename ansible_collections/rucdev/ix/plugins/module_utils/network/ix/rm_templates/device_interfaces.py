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
        super(Device_interfacesTemplate, self).__init__(lines, tmplt, prefix, module)

    PARSERS = [
        {
            "name": "device",
            "getval": re.compile(
                r"""
                ^(?P<device>\S+)
                """,
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
            "name": "description",
            "getval": re.compile(
                r"""
                ^\s+description\s+(?P<description>.+)
                """,
                re.VERBOSE,
            ),
            "setval": "description {{ description }}",
            "result": {
                "{{ name }}": {
                    "description": "{{ description }}",
                },
            },
        },
    ]
