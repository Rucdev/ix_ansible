# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


"""The ix hostname fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)

from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.hostname.hostname import (
    HostnameArgs,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.hostname import (
    HostnameTemplate,
)


class HostnameFacts:
    """The ix hostname facts class."""

    def __init__(self, module) -> None:
        self._module = module
        self.argument_spec = HostnameArgs.argument_spec

    def get_hostname_data(self, connection):
        return connection.configure_get("show running-config")

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate the facts for Hostname network resource.

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf

        :rtype: dictionary
        :returns: facts
        """
        facts = {}

        if not data:
            data = self.get_hostname_data(connection)

        # Only top-level "hostname" lines are relevant; the template regex is
        # anchored at the start of line so indented lines are ignored.
        hostname_parser = HostnameTemplate(lines=data.splitlines(), module=self._module)
        objs = hostname_parser.parse()

        ansible_facts["ansible_network_resources"].pop("hostname", None)

        params = utils.remove_empties(
            hostname_parser.validate_config(
                self.argument_spec,
                {"config": objs},
                redact=True,
            ),
        )

        facts["hostname"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts
