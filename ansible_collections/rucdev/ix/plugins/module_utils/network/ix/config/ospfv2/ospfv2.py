#
# -*- coding: utf-8 -*-
# Copyright 2024 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The ix_ospfv2 config file.
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to its desired end-state is
created.
"""

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.facts import (
    Facts,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.ospfv2 import (
    Ospfv2Template,
)


class Ospfv2(ResourceModule):
    """
    The ix_ospfv2 config class
    """

    def __init__(self, module):
        super(Ospfv2, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="ospfv2",
            tmplt=Ospfv2Template(),
        )
        self.parsers = [
            "compatible",
            "default_metric",
            "distance",
            "distribute_list",
            "nssa_range",
        ]

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        if self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        """ Generate configuration commands to send based on
            want, have and desired state.
        """
        wantd = dict()
        haved = dict()

        if self.want:
            for entry in self.want.get("processes", []):
                wantd.update({(entry["process_id"]): entry})
        
        if self.have:
            for entry in self.have.get("processes", []):
                haved.update({(entry["process_id"]): entry})

        # turn all lists of dicts into dicts prior to merge
        for each in wantd, haved:
            if each:
                self._list_to_dict(each)

        # if state is merged, merge want onto have and then compare
        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        # if state is deleted, empty out wantd and set haved to wantd
        if self.state == "deleted":
            haved = {
                k: v for k, v in iteritems(haved) if k in wantd or not wantd
            }
            wantd = {}

        # remove superfluous config for overridden and deleted
        if self.state in ["overridden", "deleted"]:
            for k, have in iteritems(haved):
                if k not in wantd:
                    self._compare(want={}, have=have)

        # delete processes first so we do run into "more than one" errors
        if self.state in ["overridden", "deleted"]:
            for k, have in iteritems(haved):
                if k not in wantd:
                    self.addcmd(have, "pid", True)

        for k, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(k, {}))

    def _compare(self, want, have):
        """Leverages the base class `compare()` method and
           populates the list of commands to be run by comparing
           the `want` and `have` data with the `parsers` defined
           for the Ospfv2 network resource.
        """
        if want != have:
            self.addcmd(want or have, "pid", False)
            self.compare(parsers=self.parsers, want=want, have=have)
    
    def _area_compare(self, want, have):
        wareas = want.get("areas", {})
        hareas = have.get("areas", {})
        for name, entry in iteritems(wareas):
            self._area_compare(want=entry, have=hareas.pop(name, {}))
        for name, entry in iteritems(hareas):
            self._area_compare(want={}, have=entry)

    def _area_compare(self, want, have):
        parsers = [
            "authentication",
            "default_cost",
            "nssa",
            "stub",
            "virtual_links",
        ]
        self.compare(parsers=parsers, want=want, have=have)
        self._area_complex_compare(want, have, want.get("area_id"))

    def _list_to_dict(self, param):
        for _pid, proc in param.items():
            # convert list to dict for areas
            for area in proc.get("areas", []):
                area["virtual_links"] = {entry["address"]: entry for entry in area.get("virtual_links", [])}

            proc["areas"] = {entry["area_id"]: entry for entry in proc.get("areas", [])}

            # list to dict for network
            if proc.get("network"):
                proc["network"] = {entry["address"]: entry for entry in proc["network"]}