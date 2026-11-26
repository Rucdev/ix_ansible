#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for ix_l2_interfaces
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: ix_l2_interfaces
short_description: Resource module to configure L2 interfaces.
description:
  - This module provides declarative management of the layer 2 settings of
    NEC IX interfaces, that is the 802.1Q VLAN tag of a sub-interface
    (C(encapsulation dot1q)) and bridge group membership (C(bridge-group)).
version_added: 0.3.0
author:
  - Yushi Takeda(@Rucdev)
notes:
  - Tested against NEC IX version 10.10.29 on IX 2215.
  - This module works with connection C(network_cli).
  - IX has no C(no encapsulation dot1q) for Ethernet sub-interfaces, so the module
    never removes a VLAN tag. With C(replaced), C(overridden) and C(deleted) the tag
    is left as it is and a warning names the interface. To drop the tag, remove the
    sub-interface (C(no interface NAME)), for example with M(rucdev.ix.ix_config).
  - IX may need a router restart before an C(encapsulation dot1q) change takes effect.
    The module sends the command but does not restart the router, and warns when it
    sends one.
  - An interface belongs to at most one bridge group. When the group changes, the
    module sends C(no bridge-group OLD) before C(bridge-group NEW).
  - Only bridge group membership is managed. C(bridge-group N port-protected),
    C(bridge-group N port-table-size), C(bridge-group N permanent-address) and global
    bridge settings such as C(bridge irb enable) are not, and C(no bridge-group N)
    leaves those lines in place.
  - IX ties an interface to the group named in any of its C(bridge-group N ...) lines,
    even without the C(bridge-group N) membership line, and rejects any other group
    with C(% Multiple VLAN not supported). Remove those lines (for example
    C(no bridge-group N port-protected)) before moving such an interface to another
    group; otherwise the task fails with that error.
  - Sub-interfaces are never created or removed on purpose, but setting C(dot1q) or
    C(bridge_group) on a sub-interface that does not exist yet creates it.
options:
  config:
    description: A list of L2 interface options.
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Full name of the interface, e.g. C(GigaEthernet0.1).
        type: str
        required: true
      dot1q:
        description:
          - 802.1Q VLAN tagging of the sub-interface (C(encapsulation dot1q)).
          - Only valid on sub-interfaces, i.e. not on C(GigaEthernetX.0).
        type: dict
        suboptions:
          vlan_id:
            description: VLAN ID, 1 to 4095.
            type: int
            required: true
          tpid:
            description:
              - TPID in hex, C(5dd) to C(ffff). IX uses C(8100) when it is omitted.
            type: str
      bridge_group:
        description:
          - Bridge group the interface belongs to (C(bridge-group)).
          - Valid on Ethernet, BVI and Tunnel interfaces.
        type: dict
        suboptions:
          group:
            description: Bridge group number, 1 to 65535.
            type: int
            required: true
  running_config:
    description:
      - This option is used only with state I(parsed).
      - The value of this option should be the output received from the IX device
        by executing the command B(show running-config interface).
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
# Router(config)# show running-config interface
# interface GigaEthernet2.0
#   no ip address
#   shutdown
# !
# interface GigaEthernet2.1
#   encapsulation pppoe
#   auto-connect
#   no ip address
#   shutdown

- name: Tag GigaEthernet2.1 with VLAN 10 and bridge it with GigaEthernet2.0
  rucdev.ix.ix_l2_interfaces:
    config:
      - name: GigaEthernet2.0
        bridge_group:
          group: 1
      - name: GigaEthernet2.1
        dot1q:
          vlan_id: 10
        bridge_group:
          group: 1
    state: merged

# Commands sent:
# - interface GigaEthernet2.0
# - bridge-group 1
# - interface GigaEthernet2.1
# - encapsulation dot1q 10 tpid 8100
# - bridge-group 1

# After state:
# ------------
# Router(config)# show running-config interface
# interface GigaEthernet2.0
#   no ip address
#   bridge-group 1
#   shutdown
# !
# interface GigaEthernet2.1
#   encapsulation dot1q 10 tpid 8100
#   auto-connect
#   no ip address
#   bridge-group 1
#   shutdown

# Using replaced

# Before state: as the After state above

- name: Move GigaEthernet2.1 to bridge group 2
  rucdev.ix.ix_l2_interfaces:
    config:
      - name: GigaEthernet2.1
        dot1q:
          vlan_id: 10
        bridge_group:
          group: 2
    state: replaced

# Commands sent:
# - interface GigaEthernet2.1
# - no bridge-group 1
# - bridge-group 2

# Using overridden

# Before state: as the After state of merged

- name: Keep bridge groups only on GigaEthernet2.1
  rucdev.ix.ix_l2_interfaces:
    config:
      - name: GigaEthernet2.1
        dot1q:
          vlan_id: 10
        bridge_group:
          group: 1
    state: overridden

# Commands sent:
# - interface GigaEthernet2.0
# - no bridge-group 1

# Using deleted

# Before state: as the After state of merged

- name: Remove L2 settings from GigaEthernet2.1
  rucdev.ix.ix_l2_interfaces:
    config:
      - name: GigaEthernet2.1
    state: deleted

# Commands sent:
# - interface GigaEthernet2.1
# - no bridge-group 1

# The VLAN tag stays (IX cannot remove it) and the module warns about it.

# Using gathered

- name: Gather L2 interface facts
  rucdev.ix.ix_l2_interfaces:
    state: gathered

# Task Output:
# gathered:
#   - name: GigaEthernet2.0
#     bridge_group:
#       group: 1
#   - name: GigaEthernet2.1
#     dot1q:
#       vlan_id: 10
#       tpid: "8100"
#     bridge_group:
#       group: 1

# Using rendered

- name: Render the commands for provided configuration
  rucdev.ix.ix_l2_interfaces:
    config:
      - name: GigaEthernet0.1
        dot1q:
          vlan_id: 100
          tpid: 88a8
    state: rendered

# Task Output:
# rendered:
#   - interface GigaEthernet0.1
#   - encapsulation dot1q 100 tpid 88a8

# Using parsed

- name: Parse the provided configuration
  rucdev.ix.ix_l2_interfaces:
    running_config: |
      interface GigaEthernet0.1
        encapsulation dot1q 100 tpid 88a8
        bridge-group 3
    state: parsed

# Task Output:
# parsed:
#   - name: GigaEthernet0.1
#     dot1q:
#       vlan_id: 100
#       tpid: 88a8
#     bridge_group:
#       group: 3
"""

RETURN = """
before:
  description: The configuration prior to the module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  sample:
    - name: GigaEthernet2.1
      dot1q:
        vlan_id: 10
        tpid: "8100"
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: list
  sample:
    - name: GigaEthernet2.1
      dot1q:
        vlan_id: 10
        tpid: "8100"
      bridge_group:
        group: 1
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  sample:
    - interface GigaEthernet2.1
    - bridge-group 1
rendered:
  description: The provided configuration in the task rendered in device-native format (offline).
  returned: when I(state) is C(rendered)
  type: list
  sample:
    - interface GigaEthernet0.1
    - encapsulation dot1q 100 tpid 8100
gathered:
  description: Facts about the network resource gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: list
  sample:
    - name: GigaEthernet2.1
      dot1q:
        vlan_id: 10
        tpid: "8100"
parsed:
  description: The device native config provided in I(running_config) option parsed into structured data as per module argspec.
  returned: when I(state) is C(parsed)
  type: list
  sample:
    - name: GigaEthernet0.1
      bridge_group:
        group: 3
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.l2_interfaces.l2_interfaces import (
    L2_interfacesArgs,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.config.l2_interfaces.l2_interfaces import (
    L2_interfaces,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=L2_interfacesArgs.argument_spec,
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

    result = L2_interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
