#
# -*- coding: utf-8 -*-
# Copyright 2023 AP Communications
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The ix l3_interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
from ansible.module_utils.six import iteritems

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.l3_interfaces.l3_interfaces import (
    L3_interfacesArgs,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.l3_interfaces import (
    L3_interfacesTemplate,
)


class L3_interfacesFacts(object):
    """The ix l3_interfaces fact class"""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = L3_interfacesArgs.argument_spec

    def get_l3_interfaces_data(self, connection):
        return connection.configure_get("show running-config interface")

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate the facts for l3_interfaces
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        objs = []

        if not data:
            data = self.get_l3_interfaces_data(connection)

        # parse native config using the l3_interfaces template
        l3_interfaces_parser = L3_interfacesTemplate(lines=data.splitlines())
        objs = l3_interfaces_parser.parse()

        objs = utils.remove_empties(objs)
        temp = []
        for k, v in iteritems(objs):
            temp.append(v)
        # sorting the dict by interface name
        temp = sorted(temp, key=lambda k, sk="name": k[sk])

        objs = temp
        facts = {}
        if objs:
            facts["l3_interfaces"] = []
            params = utils.validate_config(self.argument_spec, {"config": objs})
            for cfg in params["config"]:
                facts["l3_interfaces"].append(utils.remove_empties(cfg))
            facts["l3_interfaces"] = sorted(
                facts["l3_interfaces"], key=lambda k, sk="name": k[sk]
            )
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts
