#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2024 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for ix_ospfv2
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
    description: A dictionary of OSPF options.
    type: dict
    suboptions:
      processes:
        description:
          - List of OSPF instance.
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
              nssa:
                description:
                  - Settings for configuring the area as a nssa
                type: dict
                suboptions:
                  no_summary:
                    description: Do not send summary LSA to Not-So-Stubby area
                    type: bool
                  translate:
                    description: Always convert Type-7 LSA to Type-5 LSA
                    type: bool
                  stability_interval:
                    description: The time to keep translations running after you are no longer a Translator
                    type: int
                  default_metric:
                    description: The cost of Type-7 default route advertised to NSSA
                    type: int
                  default_metric_type:
                    description: Type-7 default route type to be advertised to NSSA
                    type: int
                    choices:
                      - 1
                      - 2
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
              virtual_links:
                description:
                  - Setting configuration for virtual-link
                  - The maximum number of Virtual-links that can be configured is 16
                type: list
                elements: dict
                suboptions:
                  address:
                    description: Opposite address of the virtual link
                    type: str
                  authentication:
                    description: Virtual link authentication
                    type: dict
                    suboptions:
                      auth_type:
                        description: Virtual link authentication type
                        type: str
                        default: "null"
                        choices:
                          - "text"
                          - "message-digest"
                          - "null"
                      text_password:
                        description: Authentication text password
                        type: str
                      message_digest_key_id:
                        description: Message digest key id(1~255)
                        type: int
                      message_digest_password:
                        description: Message digest password
                        type: str
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
          nssa_range:
            type: list
            elements: dict
            suboptions:
              range:
                description: The range of aggregated route
                type: str
              not_advertise:
                description: Whether to distribute aggregated route
                type: bool
              tag:
                description: The tag to attach to aggregated route
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
          rib:
            description:
              - Setting of rib
              - A process restart is required for the settings to take effect
            type: dict
            suboptions:
              max_entries:
                description: Setting of the max entries(64 ~ 65535)
                type: int
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

  state:
    description:
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
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.ospfv2.ospfv2 import (
    Ospfv2Args,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.config.ospfv2.ospfv2 import (
    Ospfv2,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=Ospfv2Args.argument_spec,
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

    result = Ospfv2(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
