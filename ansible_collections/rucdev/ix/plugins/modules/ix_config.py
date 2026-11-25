#!/usr/bin/python
# Copyright: Contributors to the Ansible project
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


"""The ix_config module."""

DOCUMENTATION = """
module: ix_config
author: Yushi Takeda (@ruc_dev)
short_description: Manage configuration on device of NEC IX
description:
  - This module provides an implementation for manage the configuration
    of NEC IX series.
version_added: 0.1.0
options:
  lines:
    description:
    - The ordered set of commands that should be configured in the section. The commands
        must be the exact same commands as found in the device running-config to ensure
        idempotency and correct diff. Be sure to note the configuration command syntax as
        some commands are automatically modified by the device config parser.
    type: list
    elements: str
    aliases:
    - commands
  parents:
    description:
    - The ordered set of parents that uniquely identify the section or hierarchy the
        commands should be checked against.  If the parents argument is omitted, the
        commands are checked against the set of top level or global commands.
    type: list
    elements: str
  src:
    description:
    - Specifies the source path to the file that contains the configuration or configuration
        template to load.  The path to the source file can either be the full path on
        the Ansible control host or a relative path from the playbook or role root directory. This
        argument is mutually exclusive with I(lines), I(parents). The configuration lines in the
        source file should be similar to how it will appear if present in the running-configuration
        of the device including the indentation to ensure idempotency and correct diff.
    type: str
  before:
    description:
    -  The ordered set of commands to push on to the command stack if a change needs
        to be made.  This allows the playbook designer the opportunity to perform configuration
        commands prior to pushing any changes without affecting how the set of commands
        are matched against the system.
    type: list
    elements: str
  after:
    description:
    - The ordered set of commands to append to the end of the command stack if a change
        needs to be made.  Just like with I(before) this allows the playbook designer
        to append a set of commands to be executed after the command set.
    type: list
    elements: str
  match:
    description:
    - Instructs the module on the way to perform the matching of the set of commands
        against the current device config.  If match is set to I(line), commands are
        matched line by line.  If match is set to I(strict), command lines are matched
        with respect to position.  If match is set to I(exact), command lines must be
        an equal match.  Finally, if match is set to I(none), the module will not attempt
        to compare the source configuration with the running configuration on the remote
        device.
    choices:
    - line
    - strict
    - exact
    - none
    type: str
    default: line
  replace:
    description:
    - Instructs the module on the way to perform the configuration on the device.
        If the replace argument is set to I(line) then the modified lines are pushed
        to the device in configuration mode.  If the replace argument is set to I(block)
        then the entire command block is pushed to the device in configuration mode
        if any line is not correct.
    default: line
    choices:
    - line
    - block
    type: str
  running_config:
    description:
    - The module, by default, will connect to the remote device and retrieve the current
        running-config to use as a base for comparing against the contents of source.
        There are times when it is not desirable to have the task get the current running-config
        for every task in a playbook.  The I(running_config) argument allows the implementer
        to pass in the configuration to use as the base config for comparison.
        The configuration lines for this option should be similar to how it will appear if present
        in the running-configuration of the device including the indentation to ensure idempotency
        and correct diff.
    type: str
    aliases:
    - config
  defaults:
    description:
    - This argument specifies whether or not to collect all defaults when getting
        the remote device running config.  When enabled, the module will get the current
        config by issuing the command C(show running-config all).
    type: bool
    default: no
  save_when:
    description:
      - When changes are made to the device running-configuration, the changes are not
        copied to non-volatile storage by default.  Using this argument will change
        that before.  If the argument is set to I(always), then the running-config will
        always be copied to the startup-config and the I(modified) flag will always
        be set to True.  If the argument is set to I(modified), then the running-config
        will only be copied to the startup-config if it has changed since the last save
        to startup-config.  If the argument is set to I(never), the running-config will
        never be copied to the startup-config.  If the argument is set to I(changed),
        then the running-config will only be copied to the startup-config if the task
        has made a change. I(changed) was added in Ansible 2.5.
    default: never
    choices:
      - always
      - never
      - modified
      - changed
    type: str
  backup:
    description:
      - This argument will cause the module to create a full backup of the current C(running-config)
        from the remote device before any changes are made. If the C(backup_options)
        value is not given, the backup file is written to the C(backup) folder in the
        playbook root directory or role root directory, if playbook is part of an ansible
        role. If the directory does not exist, it is created.
    type: bool
    default: false
  diff_against:
    description:
      - When using the C(ansible-playbook --diff) command line argument the module can
        generate diffs against different sources.
      - When this option is configure as I(startup), the module will return the diff
        of the running-config against the startup-config.
      - When this option is configured as I(intended), the module will return the diff
        of the running-config against the configuration provided in the C(intended_config)
        argument.
      - When this option is configured as I(running), the module will return the before
        and after diff of the running-config with respect to any changes made to the
        device configuration.
    type: str
    choices:
      - running
      - startup
      - intended
  diff_ignore_lines:
    description:
      - Use this argument to specify one or more lines that should be ignored during
        the diff.  This is used for lines in the configuration that are automatically
        updated by the system.  This argument takes a list of regular expressions or
        exact line matches.
    type: list
    elements: str
  intended_config:
    description:
      - The C(intended_config) provides the master configuration that the node should
        conform to and is used to check the final running-config against. This argument
        will not modify any settings on the remote device and is strictly used to check
        the compliance of the current device's configuration against.  When specifying
        this argument, the task should also modify the C(diff_against) value and set
        it to I(intended). The configuration lines for this value should be similar to how it
        will appear if present in the running-configuration of the device including the indentation
        to ensure correct diff.
    type: str
  backup_options:
    description:
      - This is a dict object containing configurable options related to backup file
        path. The value of this option is read only when C(backup) is set to I(yes),
        if C(backup) is set to I(no) this option will be silently ignored.
    suboptions:
      filename:
        description:
          - The filename to be used to store the backup configuration. If the filename
            is not given it will be generated based on the hostname, current time and
            date in format defined by <hostname>_config.<current-date>@<current-time>
        type: str
      dir_path:
        description:
          - This option provides the path ending with directory name in which the backup
            configuration file will be stored. If the directory does not exist it will
            be first created and the filename is either the value of C(filename) or
            default filename as described in C(filename) options description. If the
            path value is not given in that case a I(backup) directory will be created
            in the current working directory and backup configuration will be copied
            in C(filename) within I(backup) directory.
        type: path
    type: dict
"""

EXAMPLES = """
- name: Configure hostname
  rucdev.ix.ix_config:
    lines: hostname {{ inventory_hostname }}

- name: Configure GigaEthernet interface
  rucdev.ix.ix_config:
    lines: ip address 192.168.1.1/24
    parents:
      - interface GigaEthernet0.0
"""

RETURN = """"""

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import ConnectionError as AnsibleConnectionError
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import (
    NetworkConfig,
    dumps,
)

from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.ix import (
    get_config,
    get_connection,
    run_commands,
)


def get_candidate_config(module: AnsibleModule):
    """Return the candidate config built from src, or from lines and parents."""
    candidate = ""
    if module.params["src"]:
        candidate = module.params["src"]
    elif module.params["lines"]:
        candidate_obj = NetworkConfig(indent=1)
        parents = module.params["parents"] or []
        candidate_obj.add(module.params["lines"], parents=parents)
        candidate = dumps(candidate_obj, "raw")
    return candidate


def get_running_config(module: AnsibleModule, current_config=None, flags=None):
    """Return the running config to compare with, reading it from the device if needed."""
    running = module.params["running_config"]
    if not running:
        running = (
            current_config
            if not module.params["defaults"] and current_config
            else get_config(module, flags)
        )
    return running


def save_config(module: AnsibleModule, result) -> None:
    """Copy the running config to the startup config, except in check mode."""
    result["changed"] = True
    if not module.check_mode:
        run_commands(module, "copy running-config startup-config\r", configure=True)
    else:
        module.warn(
            "Skipping command `copy running-config start-config` due to check_mode. Configuration not copied to non-volatile storage",
        )


def argument_spec():
    """Return the argument spec of the module."""
    backup_spec = {"filename": {}, "dir_path": {"type": "path"}}
    return {
        "src": {"type": "str"},
        "lines": {"aliases": ["commands"], "type": "list", "elements": "str"},
        "parents": {"type": "list", "elements": "str"},
        "before": {"type": "list", "elements": "str"},
        "after": {"type": "list", "elements": "str"},
        "match": {"default": "line", "choices": ["line", "strict", "exact", "none"]},
        "replace": {"default": "line", "choices": ["line", "block"]},
        "running_config": {"aliases": ["config"]},
        "intended_config": {},
        "defaults": {"type": "bool", "default": False},
        "backup": {"type": "bool", "default": False},
        "backup_options": {"type": "dict", "options": backup_spec},
        "save_when": {
            "choices": ["always", "never", "modified", "changed"],
            "default": "never",
        },
        "diff_against": {"choices": ["startup", "intended", "running"]},
        "diff_ignore_lines": {"type": "list", "elements": "str"},
    }


def read_running_config(module, flags, result):
    """Read the running config when backup or a diff against it needs it.

    Return the text and the parsed config, or (None, None).
    """
    if not module.params["backup"] and not (
        module._diff and module.params["diff_against"] == "running"
    ):
        return None, None
    contents = get_config(module, flags)
    if module.params["backup"]:
        result["__backup__"] = contents
    return contents, NetworkConfig(indent=1, contents=contents)


def apply_lines(module, connection, contents, flags, result):
    """Send the lines or src that differ from the running config."""
    if not any((module.params["lines"], module.params["src"])):
        return
    candidate = get_candidate_config(module)
    running = get_running_config(module, contents, flags)
    try:
        response = connection.get_diff(
            candidate=candidate,
            running=running,
            diff_match=module.params["match"],
            diff_ignore_lines=module.params["diff_ignore_lines"],
            path=module.params["parents"],
            diff_replace=module.params["replace"],
        )
    except AnsibleConnectionError as exc:
        module.fail_json(msg=to_text(exc, errors="surrogate_then_replace"))

    config_diff = response["config_diff"]
    if not config_diff:
        return
    commands = config_diff.split("\n")
    if module.params["before"]:
        commands[:0] = module.params["before"]
    if module.params["after"]:
        commands.extend(module.params["after"])

    result["commands"] = commands
    result["updates"] = commands

    if not module.check_mode and commands:
        connection.edit_config(candidate=commands)

    result["changed"] = True


def save_when(module, result, diff_ignore_lines):
    """Save the running config as save_when asks.

    Return the running and startup configs that were read for it, if any.
    """
    running_config = module.params["running_config"]
    startup_config = None
    if module.params["save_when"] == "always":
        save_config(module, result)
    elif module.params["save_when"] == "modified":
        output = run_commands(
            module,
            ["show running-config", "show startup-config"],
            configure=True,
        )
        running_config = NetworkConfig(
            indent=1,
            contents=output[0],
            ignore_lines=diff_ignore_lines,
        )
        startup_config = NetworkConfig(
            indent=1,
            contents=output[1],
            ignore_lines=diff_ignore_lines,
        )
        if running_config.sha1 != startup_config.sha1:
            save_config(module, result)

    elif module.params["save_when"] == "changed" and result["changed"]:
        save_config(module, result)
    return running_config, startup_config


def diff_base_contents(module, config, startup_config, running_contents):
    """Return the config to compare the running config with, or None."""
    if module.params["diff_against"] == "running":
        if module.check_mode:
            module.warn(
                "unable to perform diff against running-config due to check mode",
            )
            return None
        return config.config_text
    if module.params["diff_against"] == "startup":
        if not startup_config:
            output = run_commands(module, "show startup-config", configure=True)
            return output[0]
        return startup_config.config_text
    if module.params["diff_against"] == "intended":
        return module.params["intended_config"]
    return running_contents


def report_diff(module, result, config, running_config, startup_config):
    """Add the diff between the running config and diff_against to the result."""
    diff_ignore_lines = module.params["diff_ignore_lines"]
    if not running_config:
        output = run_commands(module, "show running-config", configure=True)
        contents = output[0]
    else:
        contents = running_config

    running_config = NetworkConfig(
        indent=1,
        contents=contents,
        ignore_lines=diff_ignore_lines,
    )
    contents = diff_base_contents(module, config, startup_config, contents)
    if contents is None:
        return
    base_config = NetworkConfig(
        indent=1,
        contents=contents,
        ignore_lines=diff_ignore_lines,
    )
    if running_config.sha1 == base_config.sha1:
        return
    if module.params["diff_against"] == "intended":
        before = running_config
        after = base_config
    elif module.params["diff_against"] in ("startup", "running"):
        before = base_config
        after = running_config

    result.update(
        {
            "changed": True,
            "diff": {"before": str(before), "after": str(after)},
        },
    )


def main() -> None:
    """Run the module."""
    module = AnsibleModule(
        argument_spec=argument_spec(),
        mutually_exclusive=[("lines", "src"), ("parents", "src")],
        required_if=[
            ("match", "strict", ["lines"]),
            ("match", "exact", ["lines"]),
            ("replace", "block", ["lines"]),
            ("diff_against", "intended", ["intended_config"]),
        ],
        supports_check_mode=True,
    )

    result = {"changed": False}
    warnings = []
    result["warnings"] = warnings
    diff_ignore_lines = module.params["diff_ignore_lines"]
    flags = []
    connection = get_connection(module)
    contents, config = read_running_config(module, flags, result)
    apply_lines(module, connection, contents, flags, result)
    running_config, startup_config = save_when(module, result, diff_ignore_lines)
    if module._diff:
        report_diff(module, result, config, running_config, startup_config)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
