#
# -*- coding: utf-8 -*-
# Copyright 2024 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The ix_ospf_interfaces config file.
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
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.ospf_interfaces import (
    Ospf_interfacesTemplate,
)


class Ospf_interfaces(ResourceModule):
    """
    The ix_ospf_interfaces config class
    """

    def __init__(self, module):
        super(Ospf_interfaces, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="ospf_interfaces",
            tmplt=Ospf_interfacesTemplate(),
        )
        self.parsers = [ ]

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
        wantd = self._list_to_dict(self.want, "want")
        haved = self._list_to_dict(self.have)

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

        for k, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(k, {}), interface=k)

    def _compare(self, want, have, interface):
        """Leverages the base class `compare()` method and
           populates the list of commands to be run by comparing
           the `want` and `have` data with the `parsers` defined
           for the Ospf_interfaces network resource.
        """
        begin = len(self.commands)
        self._compare_afi(want=want, have=have)
        if len(self.commands) != begin:
            self.commands.insert(begin, self._tmplt.render({"name": interface}, "name", False))
    
    def _compare_afi(self, want, have):
        parsers=[
            "name",
            "interface_type",
            "retransmit_interval",
            "transmit_delay",
        ]
        for afi in ("ipv4", "ipv6"):
            wafis = want.pop(afi, {})
            hafis = have.pop(afi, {})

            self.compare(parsers=parsers, want=wafis, have=hafis)

    def _list_to_dict(self, entry, attr_type=None):
        if self.state == "deleted" and attr_type == "want":
            del_list = {}
            for intf in entry:
                del_list[intf.get("name")] = {}
            return del_list
        
        list_to_dict = {}
        for intf in entry:
            if intf.get("address_family"):
                list_to_dict[intf.get("name")] = self.process_list_attr(intf)
        return list_to_dict

    def process_list_attr(self, add_fam):
        item = {}
        for ag in add_fam.get("address_family", []):
            item[ag.get("afi")] = ag
        return item