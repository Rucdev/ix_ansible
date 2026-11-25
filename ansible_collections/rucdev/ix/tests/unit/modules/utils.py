import json

from typing import NoReturn
from unittest import TestCase
from unittest.mock import patch

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes


def set_module_args(args) -> None:
    if "_ansible_remote_tmp" not in args:
        args["_ansible_remote_tmp"] = "/tmp"
    if "_ansible_keep_remote_files" not in args:
        args["_ansible_keep_remote_files"] = False

    args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(args)
    # ansible-core 2.19+ also needs the serialization profile; older
    # versions ignore it. "legacy" is what ansible.module_utils.testing uses.
    basic._ANSIBLE_PROFILE = "legacy"


class AnsibleExitJson(Exception):
    pass


class AnsibleFailJson(Exception):
    pass


def exit_json(*args, **kwargs) -> NoReturn:
    if "changed" not in kwargs:
        kwargs["changed"] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs) -> NoReturn:
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


class ModuleTestCase(TestCase):
    def setUp(self) -> None:
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
