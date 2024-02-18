#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2023 AP Communications
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The module file for ix_facts
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
module: ix_facts
version_added: 1.1.0
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
      - When supplied, this argument will restrict the facts collected
        to a given subset. Possible values for this argument include
        all, min, hardware, config, legacy, and interfaces. Can specify a
        list of values to include a larger subset. Values can also be used
        with an initial C(M(!)) to specify that a specific subset should
        not be collected.
    required: false
    default: 'all'
    version_added: "2.2"
  gather_network_resources:
    description:
      - When supplied, this argument will restrict the facts collected
        to a given subset. Possible values for this argument include
        all and the resources like interfaces, vlans etc.
        Can specify a list of values to include a larger subset. Values
        can also be used with an initial C(M(!)) to specify that a
        specific subset should not be collected.
    required: false
    version_added: "2.9"
"""

EXAMPLES = """
# Gather all facts
- ix_facts:
    gather_subset: all
    gather_network_resources: all

# Collect only the interfaces facts
- ix_facts:
    gather_subset:
      - "!all"
      - "!min"
    gather_network_resources:
      - interfaces

# Do not collect interfaces facts
- ix_facts:
    gather_network_resources:
      - "!interfaces"

# Collect interfaces and minimal default facts
- ix_facts:
    gather_subset: min
    gather_network_resources: interfaces
"""

RETURN = """
See the respective resource module parameters for the tree.
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.facts.facts import (
    FactsArgs,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.facts import (
    Facts,
)


def main():
    """
    Main entry point for module execution

    :returns: ansible_facts
    """
    module = AnsibleModule(
        argument_spec=FactsArgs.argument_spec, supports_check_mode=True
    )
    warnings = []

    result = Facts(module).get_facts()

    ansible_facts, additional_warnings = result
    warnings.extend(additional_warnings)

    module.exit_json(ansible_facts=ansible_facts, warnings=warnings)


if __name__ == "__main__":
    main()
