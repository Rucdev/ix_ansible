#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2024 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for ix_static_routes
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
RESOURCE: static_routes
COPYRIGHT: Copyright 2024 AP Communications, Inc.
EXAMPLES:
  - static_routes.txt

DOCUMENTATION: |
module: ix_static_routes
short_description: "Configure static routes on NEC IX switches."
description: "This module configures static routes on NEC IX switches."
version_added: "1.1.0"
author:
  - "Chihiro Nakayama (@nakayumc0278)"
notes:
  - Tested against NEC IX2215 Version 10.8.21.
  - This module works with connection network_cli.
options:
  config:
    description: A dictionary of interface options.
    type: list
    elements: dict
    suboptions:
      address_families:
        description: "The destination IP address of the static route."
        type: list
        elements: dict
        suboptions:
          afi:
            description: "The address family of the static route."
            type: str
            choices:
              - ipv4
              - ipv6
            required: true
          routes:
            description: "The destination IP address of the static route."
            type: list
            elements: dict
            suboptions:
              dest:
                description: "The destination IP address of the static route."
                type: str
                required: true
              next_hops:
                description: "The next hop IP address of the static route."
                type: list
                elements: dict
                suboptions:
                  forward_router_address:
                    description: "The forward router IP address of the static route."
                    type: str
                  interface:
                    description: "The interface of the static route."
                    type: str
                  dhcp:
                    description: "The DHCP of the static route."
                    type: bool
                  connected:
                    description: "The connected of the static route."
                    type: bool
                  distance:
                    description: "The distance of the static route."
                    type: int
                  metric:
                    description: "The metric of the static route."
                    type: int
                  tag:
                    description: "Use RA address as next-hop address."
                    type: int
                  ra:
                    description: "(IPv6 only)The Router Advertisement of the static route."
                    type: bool
      vrf:
        description: "The VRF name of the static route."
        type: str
"""

EXAMPLES = """
# Using merged

- name: Merge provided configuration with device configuration
  rucdev.ix.ix_static_routes:
    config:
      - address_families:
          - afi: ipv4
            rotues:
              - dest: 192.0.2.0/24
                next_hops:
                  - foward_router_address: 192.0.2.1
                    interface: GigaEthernet0.0
                    tag: 50
                    metric: 100
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
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.static_routes.static_routes import (
    Static_routesArgs,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.config.static_routes.static_routes import (
    Static_routes,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=Static_routesArgs.argument_spec,
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

    result = Static_routes(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
