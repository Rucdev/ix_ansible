from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: ix_command
author: Yushi Takeda
short_description: Run commands on remote NEC IX devices.
description:
  - Send arbitrary commands to an ix node and returns the results read from the device
version_added: 0.1.0
options:
  commands:
    description:
      - List of commands to send to the remote ix device.
        The resulting output from the command is returned.
        If the I(wait_for) argument is provided, the module
        is not returned until the condition is satisfied or
        the number of retries has expired. If a command sent
        to the device requires answering a prompt, it is
        possible to pass a dict containing I(command), I(answer)
        and I(prompt).
    required: true
    type: list
    elements: raw
  wait_for:
    description:
      - List of conditions to evaluate against the output of the
        command. The task will wait for each condition to be true
        before moving forward. If the conditional is not true within
        the configured number of retries, the task fails. See examples.
    type: list
    element: str
  retries:
    description:
      - Specifies the number of retries a command should by tried before it is considered
        failed. The command is run on the target device every retry and evaluated against
        the I(wait_for) conditions.
    default: 9
    type: int
  interval:
    description:
      - Configures the interval in seconds to wait between retries of the command. If
        the command does not pass the specified conditions, the interval indicates how
        long to wait before trying the command again.
    default: 1
    type: int
"""

EXAMPLES = """
- name: Get show running config
  ix.ix.ix_config:
    commands: show running-config

- name: Run multiple commands
  ix.ix.ix_command:
    commands:
      - show clock
      - show vlans

- name: Run show version and check to see if output contains IX
  ix.ix.ix_command:
    commands: show version
    wait_for: result[0] contains IX

"""

import time

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.parsing import (
    Conditional,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.ix import (
    run_commands,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    transform_commands,
    to_lines,
)


def parse_commands(module: AnsibleModule, warnings: list):
    commands = transform_commands(module)

    if module.check_mode:
        for item in list(commands):
            if not item["command"].startswith("show"):
                warnings.append(
                    f"Only show commands are supported when using check mode, not executing {item['command']}"
                )
                commands.remove(item)
    return commands


def main():
    print("called command")
    argument_spec = dict(
        commands=dict(type="list", elements="raw", required=True),
        wait_for=dict(type="list", elements="str", alias="waitfor"),
        retries=dict(default=9, type="int"),
        interval=dict(default=1, type="int"),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    warnings = list()
    result = dict(changed=False, warnings=warnings)
    commands = parse_commands(module, warnings)
    wait_for = module.params["wait_for"] or list()
    conditionals = []

    try:
        conditionals = [Conditional(c) for c in wait_for]
    except AttributeError as exc:
        module.fail_json(msg=exc)

    retries = module.params["retries"]
    interval = module.params["interval"]

    while retries >= 0:
        responses = run_commands(module, commands)
        for item in list(conditionals):
            if item(responses):
                conditionals.remove(item)
        if not (conditionals):
            break
        time.sleep(interval)
        retries -= 1

    if conditionals:
        failed_conditions = [item.raw for item in conditionals]
        msg = "One or more conditional statements have not been satisfied"
        module.fail_json(msg=msg, failed_conditions=failed_conditions)

    result.update(dict(stdout=responses, stdout_lines=list(to_lines(responses))))
    module.exit_json(**result)


if __name__ == "__main__":
    main()
