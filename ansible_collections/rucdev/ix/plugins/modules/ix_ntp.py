#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2025 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for ix_ntp
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
ANSIBLE_METADATA: |
  {
      'metadata_version':'1.1',
      'status': ['preview'],
      'supported_by': ['ix-team']
  }
NETWORK_OS: ix
RESOURCE: ntp
COPYRIGHT: Copyright 2024 AP Communications, Inc.
EXAMPLES:
  - ntp.txt

DOCUMENTATION: |
module: ix_ntp
short_description: "Configure ntp on NEC IX switches."
description: "This module configures ntp on NEC IX switches."
version_added: "1.1.0"
author:
  - "Chihiro Nakayama (@nakayumc0278)"
notes:
  - Tested against NEC IX2215 Version 10.8.21.
  - This module works with connection network_cli.
options:
  config:
    description: A dictionary of ntp options.
    type: dict
    suboptions:
      address_families:
        description: "The address family of the ntp."
        type: str
        choices:
          - ipv4
          - ipv6
        suboptions:
          enable:
            description: "Enable the ntp."
            type: bool
          access_list:
            description: "The access list of the ntp."
            type: str
      master:
        description: "The master of the ntp."
        default: 8
        type: int
      retry:
        description: "The retry of the ntp."
        type: int
      servers:
        description: "The server of the ntp."
        type: list
        elements: dict
        suboptions:
          address:
            description: "The address of the ntp."
            type: str
          priority:
            description: "The priority of the ntp."
            default: 1
            type: int
          retry:
            description: "The retry of the ntp."
            default: 0
            type: int
          source:
            description: "The source of the ntp."
            type: str
          timeout:
            description: "The timeout of the ntp."
            default: 64
            type: int
          version:
            description: "The version of the ntp."
            default: 3
            type: int
      source:
        description: "The source of the ntp."
        type: str
      vrf:
        description: "The VRF name of the static route."
        type: str
      interval:
        description: "The interval of the ntp."
        type: int
"""

EXAMPLES = """
# Using merged

- name: Merge provided configuration with device configuration
  rucdev.ix.ix_ntp:
    config:
      - address_families:
          - afi: ipv4
            enable: true
            access_list: ntp-acl
        servers:
          - address: 192.0.2.1
            timeout: 64
            version: 3
    state: merged
"""

RETURN = """
before:
  description: The configuration prior to the module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted) or C(purged)
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted) or C(purged)
  type: list
  sample:
    - sample command 1
    - sample command 2
    - sample command 3
rendered:
  description: The provided configuration in the task rendered in device-native format (offline).
  returned: when I(state) is C(rendered)
  type: list
  sample:
    - sample command 1
    - sample command 2
    - sample command 3
gathered:
  description: Facts about the network resource gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
parsed:
  description: The device native config provided in I(running_config) option parsed into structured data as per module argspec.
  returned: when I(state) is C(parsed)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.ntp.ntp import (
    NtpArgs,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.config.ntp.ntp import (
    Ntp,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=NtpArgs.argument_spec,
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

    result = Ntp(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
