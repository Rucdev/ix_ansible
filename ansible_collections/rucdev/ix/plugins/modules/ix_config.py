#!/usr/bin/python
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
#
from __future__ import absolute_import, division, print_function

__metaclass__ = type
DOCUMENTATION = """
module: ix_config
author:
  - Yushi Takeda
short_description: Manage configuration on device of NEC IX
description:
  - This module provides an implementation for manage the configuration
    of NEC IX series.
version_added: 0.1.0
notes: ""
options:
  lines:
    description:
    - ""
    type: list
    elements: str
    aliases:
    - commands
  parents:
    description:
    - ""
    type: list
    elements: str
  src:
    description:
    - ""
    type: str
  before:
    description:
    - ""
    type: list
    elements: str
  after:
    description:
    - ""
    type: list
    elements: str
  match:
    description:
    - ""
    choices:
    - line
    - strict
    - exact
    - none
    type: str
    default: line
  replace:
    description:
    - ""
    default: line
    choices:
    - line
    - block
    type: str
  running_config:
    description:
    - ""
    type: str
    aliases:
    - config
  defaults:
    description:
    - ""
    type: bool
    default: no
"""

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import ConnectionError
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import (
    NetworkConfig,
    dumps,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.ix import (
    run_commands,
    get_config,
    get_connection,
)


def get_candidate_config(module: AnsibleModule):
    candidate = ""
    if module.params["src"]:
        candidate = module.params["src"]
    elif module.params["lines"]:
        candidate_obj = NetworkConfig(indent=1)
        parents = module.params["parents"] or list()
        candidate_obj.add(module.params["lines"], parents=parents)
        candidate = dumps(candidate_obj, "raw")
    return candidate


def get_running_config(module: AnsibleModule, current_config=None, flags=None):
    running = module.params["running_config"]
    if not running:
        if not module.params["defaults"] and current_config:
            running = current_config
        else:
            running = get_config(module, flags)
    return running


def save_config(module: AnsibleModule, result):
    result["changed"] = True
    if not module.check_mode:
        run_commands(module, "copy running-config startup-config\r", configure=True)
    else:
        module.warn(
            "Skipping command `copy running-config start-config` due to check_mode. Configuration not copied to non-volatile storage"
        )


def main():
    """
    main entry point for module execution
    """
    backup_spec = dict(filename=dict(), dir_path=dict(type="path"))
    argument_spec = dict(
        src=dict(type="str"),
        lines=dict(aliases=["commands"], type="list", elements="str"),
        parents=dict(type="list", elements="str"),
        before=dict(type="list", elements="str"),
        after=dict(type="list", elements="str"),
        match=dict(default="line", choices=["line", "strict", "exact", "none"]),
        replace=dict(default="line", choices=["line", "block"]),
        running_config=dict(aliases=["config"]),
        intended_config=dict(),
        defaults=dict(type="bool", default=False),
        backup=dict(type="bool", default=False),
        backup_options=dict(type="dict", options=backup_spec),
        save_when=dict(
            choices=["always", "never", "modified", "changed"], default="never"
        ),
        diff_against=dict(choices=["startup", "intended", "running"]),
        diff_ignore_lines=dict(type="list", elements="str"),
    )

    mutually_exclusive = [("lines", "src"), ("parents", "src")]

    required_if = [
        ("match", "strict", ["lines"]),
        ("match", "exact", ["lines"]),
        ("replace", "block", ["lines"]),
        ("diff_against", "intended", ["intended_config"]),
    ]

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=mutually_exclusive,
        required_if=required_if,
        supports_check_mode=True,
    )

    result = {"changed": False}
    warnings = list()
    result["warnings"] = warnings
    diff_ignore_lines = module.params["diff_ignore_lines"]
    flags = []
    config = None
    contents = None
    connection = get_connection(module)
    if (
        module.params["backup"]
        or module._diff
        and module.params["diff_against"] == "running"
    ):
        contents = get_config(module, flags)
        config = NetworkConfig(indent=1, contents=contents)
        if module.params["backup"]:
            result["__backup__"] = contents

    if any((module.params["lines"], module.params["src"])):
        match = module.params["match"]
        replace = module.params["replace"]
        path = module.params["parents"]
        candidate = get_candidate_config(module)
        running = get_running_config(module, contents, flags)
        try:
            response = connection.get_diff(
                candidate=candidate,
                running=running,
                diff_match=match,
                diff_ignore_lines=diff_ignore_lines,
                path=path,
                diff_replace=replace,
            )
        except ConnectionError as exc:
            module.fail_json(msg=to_text(exc, errors="surrogate_then_replace"))

        config_diff = response["config_diff"]
        if config_diff:
            commands = config_diff.split("\n")
            if module.params["before"]:
                commands[:0] = module.params["before"]
            if module.params["after"]:
                commands.extend(module.params["after"])

            result["commands"] = commands
            result["updates"] = commands

            if not module.check_mode:
                if commands:
                    connection.edit_config(candidate=commands)

            result["changed"] = True

    running_config = module.params["running_config"]
    startup_config = None
    if module.params["save_when"] == "always":
        save_config(module, result)
    elif module.params["save_when"] == "modified":
        output = run_commands(
            module, ["show running-config", "show startup-config"], configure=True
        )
        running_config = NetworkConfig(
            indent=1, contents=output[0], ignore_lines=diff_ignore_lines
        )
        startup_config = NetworkConfig(
            indent=1, contents=output[1], ignore_lines=diff_ignore_lines
        )
        if running_config.sha1 != startup_config.sha1:
            save_config(module, result)

    elif module.params["save_when"] == "changed" and result["changed"]:
        save_config(module, result)

    if module._diff:
        if not running_config:
            output = run_commands(module, "show running-config", configure=True)
            contents = output[0]
        else:
            contents = running_config

        running_config = NetworkConfig(
            indent=1, contents=contents, ignore_lines=diff_ignore_lines
        )
        if module.params["diff_against"] == "running":
            if module.check_mode:
                module.warn(
                    "unable to perform diff against running-config due to check mode"
                )
                contents = None
            else:
                contents = config.config_text
        elif module.params["diff_against"] == "startup":
            if not startup_config:
                output = run_commands(module, "show startup-config", configure=True)
                contents = output[0]
            else:
                contents = startup_config.config_text
        elif module.params["diff_against"] == "intended":
            contents = module.params["intended_config"]

        if contents is not None:
            base_config = NetworkConfig(
                indent=1, contents=contents, ignore_lines=diff_ignore_lines
            )

            if running_config.sha1 != base_config.sha1:
                if module.params["diff_against"] == "intended":
                    before = running_config
                    after = base_config
                elif module.params["diff_against"] in ("startup", "running"):
                    before = base_config
                    after = running_config

                result.update(
                    dict(changed=True, diff=dict(before=str(before), after=str(after)))
                )

        if result.get("changed") and any(module.params["src"], module.params["lines"]):
            msg = ()
            if module.params["src"]:
                msg += ""
            if "warnings" in result:
                result["warnings"].append(msg)
            else:
                result["warnings"] = msg

    module.exit_json(**result)


if __name__ == "__main__":
    main()
