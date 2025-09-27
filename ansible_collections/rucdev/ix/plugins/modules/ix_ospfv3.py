#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2024 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for ix_ospfv3
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: ix_ospfv2
short_description: Resource module to configure OSPF.
description:
  - This module provides declarative management of OSPF on NEC IX devices.
version_added: 1.1.0
author:
  - Yushi Takeda(@Rucdev)
notes:
  - Tested against NEC IX version 10.2.39 on IX 2105.
options:
  config:
    description: A dictionary of OSPFv3 options.
    type: dict
    suboptions:
      processes:
        description:
          - List of OSPFv3 instance.
        type: list
        elements: dict
        suboptions:
          process_id:
            description: Process ID
            required: true
            type: int
          areas:
            description:
              - OSPF area parameters
            type: list
            elements: dict
            suboptions:
              area_id:
                description:
                  - The Area ID (0-4294967295 or A.B.C.D)
                type: str
              default_cost:
                description:
                  - The default cost vaule of area
                type: int
              ranges:
                description: Setting configuration of address range for area
                type: list
                elements: dict
                suboptions:
                  address:
                    description: IP address range (A.B.C.D/<0-32>)
                    type: str
                  advertise:
                    description: Advertise this range (default)
                    type: bool
                    default: true
              stub:
                description:
                  - Settings for configuring the area as a stub
                type: dict
                suboptions:
                  set:
                    description: Enable a stub area
                    type: bool
                  no_summary:
                    description: Do not send summary LSA to stub area
                    type: bool
                  dead_interval:
                    description: Dead interval (seconds)
                    type: int
                    default: 40
                  hello_interval:
                    description: Hello interval (seconds)
                    type: int
                    default: 10
                  retransmit_interval:
                    description: Retransmit interval (seconds)
                    type: int
                  transmit_delay:
                    description: Transit delay (seconds)
                    type: int
          compatible:
            description: OSPF router compatibility list
            type: dict
            suboptions:
              rfc1583:
                description: compatible with RFC 1583
                type: bool
          default_metric:
            description: Set metric of redistributed routes
            type: int
          distance:
            description:
              - Define an administrative distance
              - A process restart is required for the settings to take effect
            type: dict
            suboptions:
              external:
                description: OSPF external routes
                type: int
              inter_area:
                description: OSPF inter-area routes
                type: int
              intra_area:
                description: OSPF intra-area routes
                type: int
              nssa_external:
                description: OSPF nssa-external routes
                type: int
          distribute_list:
            description:
              - Used for filtering when storing contents in the routing table
              - Specify a prefix list or route map
              - The OSPF process must be restarted for the settings to take effectJJ;W
            type: dict
            suboptions:
              prefix:
                description: Use the prefix list
                type: str
              route_map:
                description: Use the route map
                type: str
          network:
            description: Enable routing on an OSPF network
            type: list
            elements: dict
            suboptions:
              address:
                description: Network number
                type: str
              area:
                description: Set the OSPF area ID
                type: str
          originate_default:
            description: Setting of configure the default route
            type: dict
            suboptions:
              always:
                description: Always advertise default route
                type: bool
              metric:
                description: OSPF default metric
                type: int
                default: 1
              metric_type:
                description: OSPF metric type for default routes
                type: int
                default: 2
              route_map:
                description: Route-map reference name
                type: str
          passive_interface:
            description:
              - Setting of configure the specified interface not to send or receive OSPF packets
            type: str
          router_id:
            description: 
              - Setting of router id
              - A process restart is required for the settings to take effect
            type: str
          timers:
            description: Adjust routing timers
            type: dict
            suboptions:
              delay:
                description: The time between receipt of topology change and recalculation
                type: int 
              hold:
                description: Consecutive calculation intervals
                type: int
  running_config:
    description: 
      - This option is used only with state I(parsed).
      - The value of this option should be the output received from the ix
        device by executing the command B(show running-config ospf).
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
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.ospfv3.ospfv3 import (
    Ospfv3Args,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.config.ospfv3.ospfv3 import (
    Ospfv3,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=Ospfv3Args.argument_spec,
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

    result = Ospfv3(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
