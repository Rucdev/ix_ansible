__metaclass__ = type
# -*- coding: utf-8 -*-
# Copyright 2024 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The ix static_routes fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from ansible.module_utils.six import iteritems

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.static_routes.static_routes import (
    Static_routesArgs,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.static_routes import (
    Static_routesTemplate,
)

class Static_routesFacts(object):
    """ The ix static_routes facts class"""

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = Static_routesArgs.argument_spec

    def get_static_route_data(self, connection):
        return connection.configure_get("show running-config")

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for Static_routes network resource
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """
        objs = []

        if not data:
            data = self.get_static_route_data(connection)

        # parse native config using the Static_routes template
        static_routes_parser = Static_routesTemplate(lines=data.splitlines())
        objs = static_routes_parser.parse()

        objs = utils.remove_empties(objs)
        temp = []
        for k, v in iteritems(objs):
            temp.append(v)
        temp = sorted(temp, key=lambda k, sk="name": k[sk])

        objs = temp
        facts = {}
        if objs:
            facts["static_routes"] = []
            params = utils.validate_config(self.argument_spec, {"config": objs})
            for cfg in params["config"]:
                facts["static_routes"].append(utils.remove_empties(cfg))
            facts["static_routes"] = sorted(
                facts["static_routes"], key=lambda k, sk="name": k[sk]
            )
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts
