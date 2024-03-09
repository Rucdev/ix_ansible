# -*- coding: utf-8 -*-
# Copyright 2024 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The ix static_routes fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.static_routes import (
    Static_routesTemplate,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.static_routes.static_routes import (
    Static_routesArgs,
)

class Static_routesFacts(object):
    """ The ix static_routes facts class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = Static_routesArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for Static_routes network resource

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf

        :rtype: dictionary
        :returns: facts
        """
        facts = {}
        objs = []

        if not data:
            data = connection.get()

        # parse native config using the Static_routes template
        static_routes_parser = Static_routesTemplate(lines=data.splitlines(), module=self._module)
        objs = list(static_routes_parser.parse().values())

        ansible_facts['ansible_network_resources'].pop('static_routes', None)

        params = utils.remove_empties(
            static_routes_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )

        facts['static_routes'] = params['config']
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts
