#
# Copyright 2023 AP Communications
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""The ix interfaces fact class.

It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)

from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.interfaces.interfaces import (
    InterfacesArgs,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.interfaces import (
    InterfacesTemplate,
)

if TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule
    from ansible.module_utils.connection import Connection


class InterfacesFacts:
    """The ios interfaces facts class."""

    def __init__(self, module: AnsibleModule) -> None:
        """Keep the module and the argument spec of the resource."""
        self._module = module
        self.argument_spec = InterfacesArgs.argument_spec

    def get_interfaces_data(self, connection: Connection) -> str:
        """Return the running config of the device."""
        return connection.configure_get("show running-config interface")

    def populate_facts(
        self,
        connection: Connection,
        ansible_facts: dict,
        data: str | None = None,
    ) -> dict:
        """Populate the facts for Interfaces network resource.

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf

        :rtype: dictionary
        :returns: facts
        """
        if not data:
            data = self.get_interfaces_data(connection)

        # parse native config using the Interfaces template
        interfaces_parser = InterfacesTemplate(
            lines=data.splitlines(),
            module=self._module,
        )
        objs = sorted(
            interfaces_parser.parse().values(),
            key=lambda k, sk="name": k[sk],
        )

        ansible_facts["ansible_network_resources"].pop("interfaces", None)
        facts = {"interfaces": []}
        params = utils.remove_empties(
            interfaces_parser.validate_config(
                self.argument_spec,
                {"config": objs},
                redact=True,
            ),
        )

        facts["interfaces"] = params["config"]
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts
