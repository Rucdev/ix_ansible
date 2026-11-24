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
module: ix_static_routes
short_description: Resource module to configure static routes.
description:
  - This module provides declarative management of static routes
    (C(ip route) / C(ipv6 route)) on NEC IX devices.
version_added: "0.2.0"
author:
  - "Chihiro Nakayama (@nakayumc0278)"
notes:
  - Tested against NEC IX2215 Version 10.10.29.
  - This module works with connection C(network_cli).
  - A route is identified by I(vrf), I(afi), I(dest), I(forward_router_address),
    I(interface) and the I(connected) / I(dhcp) / I(ra) flags.
    I(distance), I(metric) and I(tag) are options of that route.
  - B(Default values are treated as not specified.) IX does not show
    C(distance 1) or C(metric 1) in the running-config, so I(distance=1) and
    I(metric=1) are ignored, the same as leaving them out.
  - With I(state=merged), options that are not specified keep the value
    currently on the device. To set an option back to its default, use
    I(state=replaced) or I(state=overridden) and leave the option out.
  - I(state=overridden) removes every static route that is not listed,
    including the default route. List the default route if you need to keep it.
options:
  config:
    description: A list of static route configurations, one per VRF (or global).
    type: list
    elements: dict
    suboptions:
      vrf:
        description:
          - VRF name. Omit for the global routing table.
          - IPv4 only. IX has no VRF form of C(ipv6 route).
        type: str
      address_families:
        description: Static routes per address family.
        type: list
        elements: dict
        suboptions:
          afi:
            description: Address family.
            type: str
            choices:
              - ipv4
              - ipv6
            required: true
          routes:
            description: Static routes.
            type: list
            elements: dict
            suboptions:
              dest:
                description:
                  - Destination prefix, for example C(192.0.2.0/24), or C(default).
                type: str
                required: true
              next_hops:
                description:
                  - Next hops of the route. Each one is a separate route on the device.
                  - With I(state=deleted), omit this to delete every route to I(dest).
                type: list
                elements: dict
                suboptions:
                  forward_router_address:
                    description:
                      - Gateway address.
                      - For IPv6, C(<address>%<interface>) (for example
                        C(fe80::1%GigaEthernet0.0)) is also accepted.
                    type: str
                  interface:
                    description: Outgoing interface, for example C(GigaEthernet0.0) or C(Null0.0).
                    type: str
                  connected:
                    description: (IPv4 only) Inject the route only when the IPv4 subsystem is connected.
                    type: bool
                  dhcp:
                    description: Use the gateway given by DHCP. Requires I(interface).
                    type: bool
                  ra:
                    description: (IPv6 only) Use the address from Router Advertisement as the next hop. Requires I(interface).
                    type: bool
                  distance:
                    description:
                      - Administrative distance (0-255).
                      - The default (1) is treated as not specified.
                    type: int
                  metric:
                    description:
                      - Metric (1-255).
                      - The default (1) is treated as not specified.
                    type: int
                  tag:
                    description: Tag for this route.
                    type: int
  running_config:
    description:
      - This option is used only with state I(parsed).
      - The value of this option should be the output received from the IX device
        by executing the command B(show running-config).
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
      - rendered
      - gathered
      - parsed
    default: merged
"""

EXAMPLES = """
# Using merged

# Before state:
# -------------
# ip route default 192.0.2.254

- name: Merge provided configuration with device configuration
  rucdev.ix.ix_static_routes:
    config:
      - address_families:
          - afi: ipv4
            routes:
              - dest: 198.51.100.0/24
                next_hops:
                  - forward_router_address: 192.0.2.1
                    distance: 10
                    tag: 50
                  - interface: Null0.0
                    distance: 250
    state: merged

# Commands sent:
# - ip route 198.51.100.0/24 192.0.2.1 distance 10 tag 50
# - ip route 198.51.100.0/24 Null0.0 distance 250

# Using merged to change one option

# Before state:
# -------------
# ip route 198.51.100.0/24 192.0.2.1 distance 10 tag 50

- name: Change only the metric; distance and tag are kept
  rucdev.ix.ix_static_routes:
    config:
      - address_families:
          - afi: ipv4
            routes:
              - dest: 198.51.100.0/24
                next_hops:
                  - forward_router_address: 192.0.2.1
                    metric: 5
    state: merged

# Commands sent:
# - ip route 198.51.100.0/24 192.0.2.1 distance 10 metric 5 tag 50

# Using replaced

# Before state:
# -------------
# ip route 198.51.100.0/24 192.0.2.1 distance 10 tag 50
# ip route 198.51.100.0/24 Null0.0 distance 250

- name: Replace the routes to 198.51.100.0/24
  rucdev.ix.ix_static_routes:
    config:
      - address_families:
          - afi: ipv4
            routes:
              - dest: 198.51.100.0/24
                next_hops:
                  - forward_router_address: 192.0.2.2
    state: replaced

# Commands sent:
# - ip route 198.51.100.0/24 192.0.2.2
# - no ip route 198.51.100.0/24 192.0.2.1
# - no ip route 198.51.100.0/24 Null0.0

# Using deleted

- name: Delete every route to 198.51.100.0/24
  rucdev.ix.ix_static_routes:
    config:
      - address_families:
          - afi: ipv4
            routes:
              - dest: 198.51.100.0/24
    state: deleted

# Using gathered

- name: Gather static routes
  rucdev.ix.ix_static_routes:
    state: gathered

# Using parsed

- name: Parse the provided configuration
  rucdev.ix.ix_static_routes:
    running_config: |
      ip route default 192.0.2.254
      ip route vrf blue 198.51.100.0/24 Null0.0 distance 250
      ipv6 route 2001:db8::/32 GigaEthernet0.0 ra
    state: parsed
"""

RETURN = """
before:
  description: The configuration prior to the module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
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
