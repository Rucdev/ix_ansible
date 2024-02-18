#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2023 AP Communications
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#############################################
#                WARNING                    #
#############################################
#
# This file is auto generated by the resource
#   module builder playbook.
#
# Do not edit this file manually.
#
# Changes to this file will be over written
#   by the resource module builder.
#
# Changes should be made in the model used to
#   generate this file or in the resource module
#   builder template.
#
#############################################

"""
The module file for ix_l3_interfaces
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "<support_group>",
}

DOCUMENTATION = """
---
module: ix_l3_interfaces
short_description: Resource module to configure L3 interfaces.
description:
  - This module provides declarative management of Layer-3 interface on NEC IX devices.
version_added: 1.1.0
author:
  - Yushi Takeda(@Rucdev)
notes:
  - Tested against NEC IX version 10.2.39 on IX 2105.
options:
  config:
    description: A dictionary of Layer-3 interface options.
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Full name of the interface excluding any logical unit number, i.e. GigaEthernet1.1
        type: str
        required: true
      ipv4:
        description:
          - IPv4 address to be set for the Layer-3 interface mentioned in I(name) option.
            The address format is <ipv4 address>/<mask>, the mask is number in range
            0-32 eg. 192.168.0.1/24.
        type: list
        elements: dict
        suboptions:
          address:
            description:
              - Configure ipv4 address for interfaces.
            type: str
          secondary:
            description:
              - Configure the IP address as a secondary address.
            type: bool
          mtu:
            description:
              - MTU for a specific interface. Applicable for Ethernet interfaces only.
              - Refer to vendor documentation for valid values.
            type: int
          dhcp:
            description:
              - IP address negotiated via DHCP.
            type: dict
            suboptions:
              enable:
                description:
                  - Enable DHCP.
                type: bool
      ipv6:
        description:
          - IPv6 address to be set for the Layer-3 logical interface mentioned in I(name) option.
          - The address format is <ipv6 address>/<mask>, the mask is number in range
            0-128 eg. fd5d:12c9:2201:1::1/64
        type: list
        elements: dict
        suboptions:
          address:
            description:
              - Configures the IPv6 address for Interface.
            type: str
          autoconfig:
            description: Obtain address using auto-configuration.
            type: dict
            suboptions:
              enable:
                description: enable auto-configuration.
                type: bool
              default:
                description: Insert default route.
                type: bool
          anycast:
            description: Configure as an anycast
            type: bool
          eui:
            description: Use eui-64 interface identifier
            type: bool
  state:
    choices:
    - merged
    - replaced
    - overridden
    - deleted
    - rendered
    - gathered
    - parsed
    default: merged
    description:
      - The state the configuration should be left in
      - The states I(rendered), I(gathered) and I(parsed) does not perform any change
        on the device.
      - The state I(rendered) will transform the configuration in C(config) option to
        platform specific CLI commands which will be returned in the I(rendered) key
        within the result. For state I(rendered) active connection to remote host is
        not required.
      - The state I(gathered) will fetch the running configuration from device and transform
        it into structured data in the format as per the resource module argspec and
        the value is returned in the I(gathered) key within the result.
      - The state I(parsed) reads the configuration from C(running_config) option and
        transforms it into JSON format as per the resource module parameters and the
        value is returned in the I(parsed) key within the result. The value of C(running_config)
        option should be the same format as the output of command
        I(show running-config | section ^interface) executed on device. For state I(parsed) active
        connection to remote host is not required.
    type: str

"""
EXAMPLES = """
# Using merged
#
#
- name: Merge provided configuration with device configuration
  rucdev.ix.ix_l3_interfaces:
    config:
      - name: GigaEthernet0.0
        ipv4:
          address: 192.168.1.1/24
    state: merged


# Using deleted

#
- name: Delete or return interface parameters to default settings
  rucdev.ix.ix_l3_interfaces:
    config:
      - name: GigaEthernet0.0
    state: deleted



# Using overridden

- name: Overrides all device configuration with provided configuration
  rucdev.ix.ix_l3_interfaces:
    config:
      - name: GigaEthernet0.0
        ipv4:
          address: 192.168.1.1/24
      - name: GigaEthernet1.0
        ipv6:
          autoconfig:
            enable: true
    state: overridden


# Using replaced

- name: Replaces device configuration of listed interfaces with provided configuration
  rucdev.ix.ix_l3_interfaces:
    config:
      - name: GigaEthernet0.0
        ipv4:
          address: 192.168.1.1/24
    state: replaced


"""
RETURN = """
before:
  description: The configuration prior to the model invocation.
  returned: always
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
after:
  description: The resulting configuration model invocation.
  returned: when changed
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
commands:
  description: The set of commands pushed to the remote device.
  returned: always
  type: list
  sample: ['command 1', 'command 2', 'command 3']
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.l3_interfaces.l3_interfaces import (
    L3_interfacesArgs,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.config.l3_interfaces.l3_interfaces import (
    L3_interfaces,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=L3_interfacesArgs.argument_spec, supports_check_mode=True
    )

    result = L3_interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()