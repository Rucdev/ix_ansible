# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Helpers that run modules in unit tests."""

import json
import tempfile

from typing import NoReturn
from unittest import TestCase
from unittest.mock import patch

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes


def set_module_args(args) -> None:
    """Set the arguments that the next AnsibleModule reads."""
    if "_ansible_remote_tmp" not in args:
        args["_ansible_remote_tmp"] = tempfile.gettempdir()
    if "_ansible_keep_remote_files" not in args:
        args["_ansible_keep_remote_files"] = False

    args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(args)
    # ansible-core 2.19+ also needs the serialization profile; older
    # versions ignore it. "legacy" is what ansible.module_utils.testing uses.
    basic._ANSIBLE_PROFILE = "legacy"


class AnsibleExitJsonError(Exception):
    """Raised instead of exiting when the module calls exit_json."""


class AnsibleFailJsonError(Exception):
    """Raised instead of exiting when the module calls fail_json."""


def exit_json(*_args, **kwargs) -> NoReturn:
    """Raise AnsibleExitJsonError with the result."""
    if "changed" not in kwargs:
        kwargs["changed"] = False
    raise AnsibleExitJsonError(kwargs)


def fail_json(*_args, **kwargs) -> NoReturn:
    """Raise AnsibleFailJsonError with the result."""
    kwargs["failed"] = True
    raise AnsibleFailJsonError(kwargs)


class ModuleTestCase(TestCase):
    """Test case that catches exit_json and fail_json."""

    def setUp(self) -> None:
        """Patch exit_json, fail_json and time.sleep."""
        self.mock_module = patch.multiple(
            basic.AnsibleModule,
            exit_json=exit_json,
            fail_json=fail_json,
        )
        self.mock_module.start()
        self.mock_sleep = patch("time.sleep")
        self.mock_sleep.start()
        set_module_args({})
        self.addCleanup(self.mock_module.stop)
        self.addCleanup(self.mock_sleep.stop)
