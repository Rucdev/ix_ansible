#!/usr/bin/python
# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""The module file for ix_hostname."""

DOCUMENTATION = """
module: ix_hostname
short_description: Resource module to configure hostname.
description:
  - This module provides declarative management of hostname on NEC IX devices.
version_added: 0.3.0
author:
  - Yushi Takeda(@Rucdev)
notes:
  - Tested against NEC IX version 10.10.29 on IX 2215.
  - This module works with connection C(network_cli).
  - The hostname must not contain whitespace. IX accepts C(hostname a b) without
    error but stores only C(a), so the module rejects such values.
  - Since hostname is a single value, C(merged), C(replaced) and C(overridden) behave the same.
  - C(deleted) sends C(no hostname), which removes the C(hostname) line from the running-config.
options:
  config:
    description: A dictionary of hostname options.
    type: dict
    suboptions:
      hostname:
        description: Hostname of the device. Must not contain whitespace.
        type: str
  running_config:
    description:
      - This option is used only with state I(parsed).
      - The value of this option should be the output received from the IX device
        by executing the command B(show running-config).
      - The state I(parsed) reads the configuration from C(running_config) option and
        transforms it into Ansible structured data as per the resource module's argspec
        and the value is then returned in the I(parsed) key within the result.
    type: str
  state:
    description:
      - The state the configuration should be left in.
    type: str
    choices:
      - merged
      - replaced
      - overridden
      - deleted
      - gathered
      - rendered
      - parsed
    default: merged
"""

EXAMPLES = """
# Using merged

# Before state:
# -------------
# Router(config)# show running-config
# (no hostname line)

- name: Set hostname
  rucdev.ix.ix_hostname:
    config:
      hostname: Router1
    state: merged

# Commands sent:
# - hostname Router1

# Using deleted

# Before state:
# -------------
# Router1(config)# show running-config
# hostname Router1

- name: Remove hostname
  rucdev.ix.ix_hostname:
    state: deleted

# Commands sent:
# - no hostname

# Using gathered

- name: Gather hostname
  rucdev.ix.ix_hostname:
    state: gathered

# Task Output:
# gathered:
#   hostname: Router1

# Using rendered

- name: Render the commands for provided configuration
  rucdev.ix.ix_hostname:
    config:
      hostname: Router1
    state: rendered

# Task Output:
# rendered:
#   - hostname Router1

# Using parsed

- name: Parse the provided configuration
  rucdev.ix.ix_hostname:
    running_config: |
      hostname Router1
    state: parsed

# Task Output:
# parsed:
#   hostname: Router1
"""

RETURN = """
before:
  description: The configuration prior to the module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: dict
  sample:
    hostname: Router
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: dict
  sample:
    hostname: Router1
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  sample:
    - hostname Router1
rendered:
  description: The provided configuration in the task rendered in device-native format (offline).
  returned: when I(state) is C(rendered)
  type: list
  sample:
    - hostname Router1
gathered:
  description: Facts about the network resource gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: dict
  sample:
    hostname: Router1
parsed:
  description: The device native config provided in I(running_config) option parsed into structured data as per module argspec.
  returned: when I(state) is C(parsed)
  type: dict
  sample:
    hostname: Router1
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.hostname.hostname import (
    HostnameArgs,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.config.hostname.hostname import (
    Hostname,
)


def main() -> None:
    """Run the module.

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=HostnameArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    result = Hostname(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
