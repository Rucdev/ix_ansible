# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


"""The Hostname parser templates file. This contains
a list of parser definitions and associated functions that
facilitates both facts gathering and native command generation for
the given network resource.
"""

import re

from typing import ClassVar

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class HostnameTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None) -> None:
        super().__init__(lines=lines, tmplt=self, module=module)

    PARSERS: ClassVar[list] = [
        {
            "name": "hostname",
            "getval": re.compile(
                r"""
                ^hostname\s(?P<hostname>\S+)
                \s*$""",
                re.VERBOSE,
            ),
            "setval": "hostname {{ hostname }}",
            "result": {
                "hostname": "{{ hostname }}",
            },
        },
    ]
