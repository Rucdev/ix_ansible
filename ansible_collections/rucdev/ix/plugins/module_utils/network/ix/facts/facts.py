from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts import (
    FactsBase,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.interfaces.interfaces import (
    InterfacesFacts,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.device_interfaces.device_interfaces import (
    Device_interfacesFacts,
)

FACT_RESOURCE_SUBSETS = dict(
    interfaces=InterfacesFacts, device_interfaces=Device_interfacesFacts
)


class Facts(FactsBase):
    VALID_RESOURCE_SUBSETS = frozenset(FACT_RESOURCE_SUBSETS.keys())

    def __init__(self, module):
        super().__init__(module)

    def get_facts(self, legacy_facts_type=None, resource_facts_type=None, data=None):
        # raise ValueError(self.VALID_RESOURCE_SUBSETS)
        if self.VALID_RESOURCE_SUBSETS:
            self.get_network_resources_facts(
                FACT_RESOURCE_SUBSETS, resource_facts_type, data
            )
        return self.ansible_facts, self._warnings
