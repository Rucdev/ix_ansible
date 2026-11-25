# (c) 2016 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.


import contextlib
import json

from pathlib import Path

import pytest

from ansible_collections.rucdev.ix.tests.unit.modules.utils import (
    AnsibleExitJsonError,
    AnsibleFailJsonError,
    ModuleTestCase,
)

fixture_path = Path(__file__).parent / "fixtures"
fixture_data = {}


def load_fixture(name):
    path = fixture_path / name

    if path in fixture_data:
        return fixture_data[path]

    data = path.read_text()

    with contextlib.suppress(Exception):
        data = json.loads(data)

    fixture_data[path] = data
    return data


class TestIxModule(ModuleTestCase):
    def execute_module(
        self,
        *,
        failed=False,
        changed=False,
        commands=None,
        sort=True,
    ):
        self.load_fixtures(commands)

        if failed:
            result = self.failed()
            assert result["failed"], result
        else:
            result = self.changed(changed=changed)
            assert result["changed"] == changed, result

        if commands is not None:
            if sort:
                assert sorted(commands) == sorted(result["commands"]), result[
                    "commands"
                ]
            else:
                assert commands == result["commands"], result["commands"]

        return result

    def failed(self):
        with pytest.raises(AnsibleFailJsonError) as exc:
            self.module.main()

        result = exc.value.args[0]
        assert result["failed"], result
        return result

    def changed(self, *, changed=False):
        with pytest.raises(AnsibleExitJsonError) as exc:
            self.module.main()

        result = exc.value.args[0]
        assert result["changed"] == changed, result
        return result

    def load_fixtures(self, commands=None) -> None:
        pass
