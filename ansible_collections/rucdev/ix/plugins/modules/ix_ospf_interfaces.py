#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2024 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for ix_ospf_interfaces
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: ix_ospf_interfaces
short_description: Resource module to configure OSPF interfaces.
description:
  - This module provides declarative management of OSPF on NEC IX devices.
version_added: 1.1.0
author:
  - Yushi Takeda(@Rucdev)
notes:
  - Tested against NEC IX version 10.2.39 on IX 2105.
options:
  config:
    description: A dictionary of OSPF options.
    type: list
    elements: dict
    suboptions:
      name:
        description: Full name of the interface including subinterface.
        type: str
        required: true
      address_family:
        description: OSPF interfaces settings on the interfaces in addres-family context.
        type: list
        elements: dict
        suboptions:
          afi:
            description: Address Family Identifier (AFI) for OSPF interfaces settings on the interfaces.
            type: str
            choices:
              - ipv4
              - ipv6
          authentication:
            description: Enable authentication
            type: str
          authentication_key:
            description: Sets the password if encryption is not used.
            type: str
          cost:
            description: Sets the value of cost on the interface.(1~65535)
            type: int
          hello_interval:
            description: Sets the value of hello-interval on the interface.
            type: int
          dead_interval:
            description: Configure the value of dead-interval on the interface.
            type: int
          message_digest_key:
            description: Configure of md5 password.(when you use this, the authentication must be message-digest.)
            type: dict
            suboptions:
              key_id:
                description: md5 key id(1~255)
                type: int
              password:
                description: md5 password
                type: str
          mtu_ignore:
            description: Ignore MTU mismatch
            type: bool
          neighbor:
            description: 
              - Register adjacent routers on the NBMA(Non-Broadcast Multiple Access) interface.
              - Unicast transmission is performed only when the interface type is NBMA.
            type: list
            elements: dict
            suboptions:
              address:
                description: Neighbor router IP address
                type: str
              interval:
                description: The polling interval when adjacent router is down
                type: int
                default: 120
              priority:
                description: Neighboring router priority
                type: int
                default: 1
          interface_type:
            description: Configure type of the interface
            type: str
            choices:
              - broadcast
              - default
              - non-broadcast
              - point-to-point
          priority:
            description: Router priority on interface
            type: int
          retransmit_interval:
            description: Configuration of retransmit-interval on the interface
            type: int
          transmit_delay:
            description: Configuration of transmit-delay on the interface
            type: int
  running_config:
    description: 
      - This option is used only with state I(parsed).
      - The value of this option should be the output received from the ix
        device by executing the command B(show running-config interfaces <name>).
      - The state I(parsed) reads the configuration from C(running_config)
        option and transforms it into Ansible structured data as per the
        resource module's argspec and the value is then returned in the
        I(parsed) key within the result.
    type: str
  state:
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
        option should be the same format as the output of command I(show running-config ospf)
        executed on device. For state I(parsed) active
        connection to remote host is not required.
    type: str
    choice:
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
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.ospf_interfaces.ospf_interfaces import (
    Ospf_interfacesArgs,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.config.ospf_interfaces.ospf_interfaces import (
    Ospf_interfaces,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=Ospf_interfacesArgs.argument_spec,
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

    result = Ospf_interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
