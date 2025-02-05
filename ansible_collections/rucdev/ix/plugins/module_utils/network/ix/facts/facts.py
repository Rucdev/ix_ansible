from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts import (
    FactsBase,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.interfaces.interfaces import (
    InterfacesFacts,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.l3_interfaces.l3_interfaces import (
    L3_interfacesFacts,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.ospf_interfaces.ospf_interfaces import (
    Ospf_interfacesFacts
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.ospfv2.ospfv2 import (
    Ospfv2Facts
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.ospfv3.ospfv3 import (
    Ospfv3Facts
)

FACT_RESOURCE_SUBSETS = dict(
    interfaces=InterfacesFacts,
    l3_interfaces=L3_interfacesFacts,
    ospf_interfaces=Ospf_interfacesFacts,
    ospfv2=Ospfv2Facts,
    ospfv3=Ospfv3Facts,
)


class Facts(FactsBase):
    VALID_RESOURCE_SUBSETS = frozenset(FACT_RESOURCE_SUBSETS.keys())

    def __init__(self, module):
        super().__init__(module)

    def get_facts(self, legacy_facts_type=None, resource_facts_type=None, data=None):
        if self.VALID_RESOURCE_SUBSETS:
            self.get_network_resources_facts(
                FACT_RESOURCE_SUBSETS, resource_facts_type, data
            )
        return self.ansible_facts, self._warnings
