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
                $""", re.VERBOSE),
            "setval": "",
            "result": {
            },
            "shared": True
        },
    ]
    # fmt: on


