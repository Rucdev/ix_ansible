#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
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
The module file for ix_device_interfaces
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": ["ix-team"],
}

DOCUMENTATION = """
---
module: ix_device_interfaces
short_description: "Configures interfaces on NEC IX switches."
description: "This module configures interfaces on NEC IX switches."
version_added: "1.1.0"
author:
  - "Chihiro Nakayama"
notes:
  - Tested against NEC IX2105 Version 10.2.39.
  - This module works with connection network_cli.
options:
  config:
    description: A dictionary of interface options.
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - The name of the interface, e.g. GitEthernet0.0, Loopback0, etc.
        type: str
        required: true
      duplex:
        description:
          - The duplex mode of the interface.
        type: str
        choices:
          - auto
          - full
          - half
        default: auto
      keepalive:
        description:
          - Enable device keepalive
        type: int
      mdix:
        description:
          - The MDI/MDIX mode of the interface.
        type: str
        choices:
          - mdi
          - mdix
      output-buffer:
        description:
          - The number of output buffers.
        type: int
      sflow:
        description:
          - The sFlow configuration of the interface.
        type: dict
        suboptions:
          max_header_size:
            description:
              - The maximum header size of the sFlow.
            type: int
          polling_interval:
            description:
              - The polling interval of the sFlow.
            type: int
          sampling_rate:
            description:
              - The sampling rate of the sFlow.
            type: int
      speed:
        description:
          - The speed of the interface.
        type: str
        choices:
          - 10
          - 100
          - 1000
          - auto
  reset:
    description:
      - Reset the interface configuration to the default.
    type: dict
    suboptions:
      name:
        description:
          - The name of the interface, e.g. GitEthernet0.0, Loopback0, etc.
        type: str
  state:
    description:
      - The state of the interface configuration.
    type: str
    choices:
      - merged
      - replaced
      - overridden
      - deleted
      - rendered
      - gathered
      - purged
      - parsed
    default: merged
"""
EXAMPLES = """
- name: Example device_interface module
  rucdev.ix.device_interface:
    config:
      name: GigaEthernet0
      duplex: full
      speed: auto


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
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.device_interfaces.device_interfaces import (
    Device_interfacesArgs,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.config.device_interfaces.device_interfaces import (
    Device_interfaces,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=Device_interfacesArgs.argument_spec, supports_check_mode=True
    )

    result = Device_interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
