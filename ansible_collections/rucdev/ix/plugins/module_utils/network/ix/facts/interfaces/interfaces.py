__metaclass__ = type
#
# -*- coding: utf-8 -*-
# Copyright 2023 AP Communications
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The ix interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.interfaces.interfaces import (
    InterfacesArgs,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.interfaces import (
    InterfacesTemplate,
)


class InterfacesFacts(object):
    """The ios interfaces facts class"""

    def __init__(self, module):
        self._module = module
        self.argument_spec = InterfacesArgs.argument_spec

    def get_interfaces_data(self, connection):
        return connection.configure_get("show running-config")

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate the facts for Interfaces network resource

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
            lines=data.splitlines(), module=self._module
        )
        objs = sorted(
            list(interfaces_parser.parse().values()), key=lambda k, sk="name": k[sk]
        )

        ansible_facts["ansible_network_resources"].pop("interfaces", None)
        facts = {"interfaces": []}
        params = utils.remove_empties(
            interfaces_parser.validate_config(
                self.argument_spec, {"config": objs}, redact=True
            ),
        )

        facts["interfaces"] = params["config"]
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts
