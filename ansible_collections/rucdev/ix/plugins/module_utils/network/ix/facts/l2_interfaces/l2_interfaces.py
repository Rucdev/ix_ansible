# -*- coding: utf-8 -*-
# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The ix l2_interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.l2_interfaces.l2_interfaces import (
    L2_interfacesArgs,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.l2_interfaces import (
    L2_interfacesTemplate,
)


class L2_interfacesFacts(object):
    """The ix l2_interfaces facts class"""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = L2_interfacesArgs.argument_spec

    def get_l2_interfaces_data(self, connection):
        return connection.configure_get("show running-config interface")

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate the facts for L2_interfaces network resource

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf

        :rtype: dictionary
        :returns: facts
        """
        if not data:
            data = self.get_l2_interfaces_data(connection)

        parser = L2_interfacesTemplate(lines=data.splitlines(), module=self._module)
        objs = utils.remove_empties(parser.parse())

        # Every interface block matches the "name" parser; keep only the
        # ones that actually carry L2 settings.
        objs = sorted(
            (v for v in objs.values() if set(v) - {"name"}),
            key=lambda x: x["name"],
        )

        ansible_facts["ansible_network_resources"].pop("l2_interfaces", None)

        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )

        ansible_facts["ansible_network_resources"].update(
            {"l2_interfaces": params.get("config", [])}
        )

        return ansible_facts
