#!/usr/bin/python
# Copyright 2023 AP Communications
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""The module file for ix_facts."""

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "<support_group>",
}


DOCUMENTATION = """
---
module: ix_facts
version_added: 0.2.0
short_description: Get facts about ix devices.
description:
  - Collects facts from network devices running the ix operating
    system. This module places the facts gathered in the fact tree keyed by the
    respective resource name.  The facts module will always collect a
    base set of facts from the device and can enable or disable
    collection of additional facts.
author: Yushi Takeda (@Rucdev)
options:
  gather_subset:
    description:
      - Accepted for compatibility with other network collections, but not used.
        This collection does not gather legacy facts, so only the resources in
        C(gather_network_resources) are collected.
    type: list
    elements: str
    required: false
    default: [min]
  gather_network_resources:
    description:
      - The resources to collect facts for, or C(all) for every resource.
      - Values with an initial C(!), which exclude a resource, are not accepted.
    type: list
    elements: str
    choices:
      - all
      - hostname
      - interfaces
      - l3_interfaces
      - ospf_interfaces
      - ospfv2
      - ospfv3
      - static_routes
    required: false
"""

EXAMPLES = """
# Collect the facts of every resource
- rucdev.ix.ix_facts:
    gather_network_resources: all

# Collect only the interfaces facts
- rucdev.ix.ix_facts:
    gather_network_resources:
      - interfaces
"""

RETURN = """"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.facts.facts import (
    FactsArgs,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.facts import (
    Facts,
)


def main() -> None:
    """Run the module.

    :returns: ansible_facts
    """
    module = AnsibleModule(
        argument_spec=FactsArgs.argument_spec,
        supports_check_mode=True,
    )
    warnings = []

    result = Facts(module).get_facts()

    ansible_facts, additional_warnings = result
    warnings.extend(additional_warnings)

    module.exit_json(ansible_facts=ansible_facts, warnings=warnings)


if __name__ == "__main__":
    main()
