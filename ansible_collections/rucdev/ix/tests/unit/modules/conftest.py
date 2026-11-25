# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


"""Pytest fixtures for the module tests."""

from __future__ import annotations

import json
import tempfile

from typing import TYPE_CHECKING

import pytest

from ansible.module_utils._text import to_bytes
from ansible.module_utils.common._collections_compat import MutableMapping

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def patch_ansible_module(request: pytest.FixtureRequest, mocker: MockerFixture) -> None:
    """Patch the module arguments with the parameters of the test."""
    if isinstance(request.param, str):
        args = request.param
    elif isinstance(request.param, MutableMapping):
        if "ANSIBLE_MODULE_ARGS" not in request.param:
            request.param = {"ANSIBLE_MODULE_ARGS": request.param}
        if "_ansible_remote_tmp" not in request.param["ANSIBLE_MODULE_ARGS"]:
            request.param["ANSIBLE_MODULE_ARGS"][
                "_ansible_remote_tmp"
            ] = tempfile.gettempdir()
        if "_ansible_keep_remote_files" not in request.param["ANSIBLE_MODULE_ARGS"]:
            request.param["ANSIBLE_MODULE_ARGS"]["_ansible_keep_remote_files"] = False
        args = json.dumps(request.param)
    else:
        msg = "Malformed data to the patch_ansible_module pytest fixture"
        raise TypeError(msg)

    mocker.patch("ansible.module_utils.basic._ANSIBLE_ARGS", to_bytes(args))
