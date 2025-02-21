# -*- coding: utf-8 -*-
# Copyright 2024 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The ix ospfv3 fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.ospfv3 import (
    Ospfv3Template,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.ospfv3.ospfv3 import (
    Ospfv3Args,
)


class Ospfv3Facts(object):
    """The ix ospfv3 facts class"""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Ospfv3Args.argument_spec

    def get_ospfv3_data(self, connection):
        return connection.configure_get("show running-config ospf")

    def dict_to_list(self, ospf_data):
        """Converts areas in each process to list
        :param ospf_data: ospf data
        :rtype: dictionary
        :returns: facts_output
        """

        facts_output = {"processes": []}

        for process in ospf_data.get("processes", []):
            if "areas" in process:
                process["areas"] = list(process["areas"].values())
            facts_output["processes"].append(process)

        return facts_output

    def preprocess_lines(self, lines):
        """Filters input lines to extract only the relevant OSPFv3 configuration
        :param lines: A list of configuration lines.

        :rtypes: list
        :returns: lines
        """
        get_line = False
        filtered_lines = []

        for line in lines:
            if line.startswith("ipv6 router ospf"):
                get_line = True
            if get_line:
                filtered_lines.append(line)
            if line.startswith("!"):
                get_line = False
        return filtered_lines

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate the facts for Ospfv3 network resource

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf

        :rtype: dictionary
        :returns: facts
        """
        facts = {}

        if not data:
            data = self.get_ospfv3_data(connection)

        # pick up
        # parse native config using the Ospfv3 template
        ospfv3_parser = Ospfv3Template(
            lines=self.preprocess_lines(data.splitlines()), module=self._module
        )
        ospfv3_parsed = ospfv3_parser.parse()

        # Convert dict to list
        ospfv3_parsed["processes"] = (
            ospfv3_parsed["processes"].values() if "processes" in ospfv3_parsed else []
        )

        # converts areas, interfaces in each process to list
        facts_output = self.dict_to_list(ospfv3_parsed)

        ansible_facts["ansible_network_resources"].pop("ospfv3", None)

        params = utils.remove_empties(
            ospfv3_parser.validate_config(
                self.argument_spec, {"config": facts_output}, redact=True
            )
        )
        facts["ospfv3"] = params["config"]
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts
