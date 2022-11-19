from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: ix_command
version_added: "0.0"
authors:
  - Yushi Takeda
short_description: Run commands on remote NEC IX devices.
description:
  - Send arbitrary commands to an ix node and returns the results read from the device
"""
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.parsing import (
    Conditional,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix2105.ix2105 import (
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
                    "Only show commands are supported when using check mode, not"
                    f"executing {item['command']}"
                )
                commands.remove(item)
    return commands


def main():
    print("called command")
    argument_spec = {
        "commands": {"type": "list", "element": "raw", "required": True},
    }
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    warnings = list()
    result = {"changed": False, "warnings": warnings}
    commands = parse_commands(module, warnings)

    responses = run_commands(module, commands)
    result.update({"stdout": responses, "stdout_lines": list(to_lines(responses))})
    module.exit_json(**result)


if __name__ == "__main__":
    main()
