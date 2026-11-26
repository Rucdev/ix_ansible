# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Fact gathering of the ix_* resource modules."""

from __future__ import annotations

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts import (
    FactsBase,
)

from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.hostname.hostname import (
    HostnameFacts,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.interfaces.interfaces import (
    InterfacesFacts,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.l3_interfaces.l3_interfaces import (
    L3InterfacesFacts,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.ospf_interfaces.ospf_interfaces import (
    OspfInterfacesFacts,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.ospfv2.ospfv2 import (
    Ospfv2Facts,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.ospfv3.ospfv3 import (
    Ospfv3Facts,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.static_routes.static_routes import (
    StaticRoutesFacts,
)

FACT_RESOURCE_SUBSETS = {
    "hostname": HostnameFacts,
    "interfaces": InterfacesFacts,
    "l3_interfaces": L3InterfacesFacts,
    "ospf_interfaces": OspfInterfacesFacts,
    "ospfv2": Ospfv2Facts,
    "ospfv3": Ospfv3Facts,
    "static_routes": StaticRoutesFacts,
}


class Facts(FactsBase):
    """Gather the facts of the resource modules."""

    VALID_RESOURCE_SUBSETS = frozenset(FACT_RESOURCE_SUBSETS.keys())

    def get_facts(
        self,
        legacy_facts_type: list | None = None,
        resource_facts_type: list | None = None,
        data: str | None = None,
    ) -> tuple[dict, list]:
        """Gather the facts of the requested resources and return them with the warnings."""
        if self.VALID_RESOURCE_SUBSETS:
            self.get_network_resources_facts(
                FACT_RESOURCE_SUBSETS,
                resource_facts_type,
                data,
            )
        return self.ansible_facts, self._warnings
