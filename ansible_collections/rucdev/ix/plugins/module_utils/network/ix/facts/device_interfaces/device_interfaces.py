#
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The ix device_interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""
import re
from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.device_interfaces.device_interfaces import (
    Device_interfacesArgs,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.device_interfaces import (
    Device_interfacesTemplate,
)


class Device_interfacesFacts(object):
    """The ix device_interfaces fact class"""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Device_interfacesArgs.argument_spec

    def get_device_interfaces_data(self, connection):
        return connection.configure_get("show running-config device")

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate the facts for device_interfaces
        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf
        :rtype: dictionary
        :returns: facts
        """

        if not data:
            # typically data is populated from the current device configuration
            # data = connection.get('show running-config | section ^interface')
            # using mock data instead
            data = self.get_device_interfaces_data(connection)

        device_interfaces_parser = Device_interfacesTemplate(
            lines=data.splitlines(), module=self._module
        )

        objs = sorted(
            list(device_interfaces_parser.parse().values()),
            key=lambda k, sk="name": k[sk],
        )

        ansible_facts["ansible_network_resources"].pop("device_interfaces", None)
        facts = {"device_interfaces": []}
        params = utils.remove_empties(
            device_interfaces_parser.validate_config(
                self.argument_spec, {"config": objs}, redact=True
            )
        )
        facts["device_interfaces"] = params["config"]
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts
