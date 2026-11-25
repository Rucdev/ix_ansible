#
# Copyright 2023 AP Communications
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""The arg spec for the ix facts module."""


class FactsArgs:  # pylint: disable=R0903
    """The arg spec for the ix facts module."""

    def __init__(self, **kwargs) -> None:
        pass

    choices = [
        "all",
        "hostname",
        "interfaces",
        "l3_interfaces",
        "ospf_interfaces",
        "ospfv2",
        "ospfv3",
        "static_routes",
    ]

    argument_spec = {
        "gather_subset": {"default": ["min"], "type": "list", "elements": "str"},
        "gather_network_resources": {
            "choices": choices,
            "type": "list",
            "elements": "str",
        },
    }
