# Copyright 2024 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


"""The ix ospf_interfaces fact class.

It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)

from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.ospf_interfaces.ospf_interfaces import (
    OspfInterfacesArgs,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.ospf_interfaces import (
    OspfInterfacesTemplate,
)

if TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule
    from ansible.module_utils.connection import Connection


class OspfInterfacesFacts:
    """The ix ospf_interfaces facts class."""

    def __init__(self, module: AnsibleModule) -> None:
        """Keep the module and the argument spec of the resource."""
        self._module = module
        self.argument_spec = OspfInterfacesArgs.argument_spec

    def get_ospf_interfaces_data(self, connection: Connection) -> str:
        """Return the running config of the device."""
        return connection.configure_get("show running-config interface")

    def populate_facts(
        self,
        connection: Connection,
        ansible_facts: dict,
        data: str | None = None,
    ) -> dict:
        """Populate the facts for OspfInterfaces network resource.

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf

        :rtype: dictionary
        :returns: facts
        """
        facts = {}
        objs = []

        if not data:
            data = self.get_ospf_interfaces_data(connection)

        # parse native config using the OspfInterfaces template
        ospf_interfaces_parser = OspfInterfacesTemplate(
            lines=data.splitlines(),
            module=self._module,
        )

        objs = ospf_interfaces_parser.parse()
        final_objs = []

        for value in objs.values():
            temp_af = []
            if value["address_family"].get("ip"):
                temp_af.append(value["address_family"].get("ip"))
            if value["address_family"].get("ipv6"):
                temp_af.append(value["address_family"].get("ipv6"))
            if temp_af:
                value["address_family"] = temp_af
            if value:
                final_objs.append(utils.remove_empties(value))

        ansible_facts["ansible_network_resources"].pop("ospf_interfaces", None)

        params = utils.remove_empties(
            ospf_interfaces_parser.validate_config(
                self.argument_spec,
                {"config": final_objs},
                redact=True,
            ),
        )

        facts["ospf_interfaces"] = params.get("config", [])
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts
