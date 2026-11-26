# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


"""The arg spec for the ix_hostname module."""

from typing import ClassVar


class HostnameArgs:
    """The arg spec for the ix_hostname module."""

    argument_spec: ClassVar[dict] = {
        "config": {
            "type": "dict",
            "options": {
                "hostname": {"type": "str"},
            },
        },
        "running_config": {"type": "str"},
        "state": {
            "type": "str",
            "choices": [
                "merged",
                "replaced",
                "overridden",
                "deleted",
                "gathered",
                "rendered",
                "parsed",
            ],
            "default": "merged",
        },
    }
