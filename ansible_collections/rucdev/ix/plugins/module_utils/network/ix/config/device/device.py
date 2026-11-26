#
# -*- coding: utf-8 -*-
# Copyright 2023 AP Communications
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The ix_Device class
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to it's desired end-state is
created
"""

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_list,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.facts import (
    Facts,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.device import (
    DeviceTemplate,
)

KEEPALIVE_DEFAULT = "keepalive 4 3"


class Device(ResourceModule):
    """
    The ix_Device class
    """

    def __init__(self, module):
        super(Device, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="device",
            tmplt=DeviceTemplate(),
        )
        self.parsers = [
            "duplex",
            "mdix",
            "output_buffer",
            "sflow.max_header_size",
            "sflow.polling_interval",
            "sflow.sampling_rate.in",
            "sflow.sampling_rate.out",
            "speed",
        ]

    def execute_module(self):
        """Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        if self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        """Generate configuration commands to send based on
        want, have and desired state.
        """
        wantd = {entry["name"]: entry for entry in self.want}
        haved = {entry["name"]: entry for entry in self.have}

        # for each in wantd, haved:
        #     self.normalize_interface_names(each)

        # if state is merged, merge want onto have and then compare
        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        # if state is deleted, empty out wantd and set haved to wantd
        if self.state == "deleted":
            haved = {k: v for k, v in iteritems(haved) if k in wantd or not wantd}
            wantd = {}

        # remove superfluous config for overridden and deleted
        if self.state in ["overridden", "deleted"]:
            for k, have in iteritems(haved):
                if k not in wantd:
                    self._compare(want={}, have=have)

        for k, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(k, {}))

    def _compare(self, want, have):
        """Leverages the base class `compare()` method and
        populates the list of commands to be run by comparing
        the `want` and `have` data with the `parsers` defined
        for the Device network resource.
        """
        begin = len(self.commands)
        self.compare(parsers=self.parsers, want=want, have=have)
        self._compare_keepalive(want, have)

        # if want.get("enabled") != have.get("enabled"):
        #     if want.get("enabled"):
        #         self.addcmd(want, "enabled", True)
        #     else:
        #         if want:
        #             self.addcmd(want, "enabled", False)
        #         elif have.get("enabled"):
        #             # handles deleted as want be blank and only
        #             # negates if no shutdown
        #             self.addcmd(have, "enabled", False)

        if len(self.commands) != begin:
            self.commands.insert(
                begin, self._tmplt.render(want or have, "device", False)
            )

    def _compare_keepalive(self, want, have):
        """ "no keepalive" disables keepalive on IX, so removing a configured
        value sets the IX defaults (4 3) instead, which shows as no line in the
        running-config.
        """
        want_ka = want.get("keepalive")
        have_ka = have.get("keepalive")
        if want_ka == have_ka:
            return
        if want_ka:
            self.addcmd(want, "keepalive", False)
        elif have_ka:
            self.commands.append(KEEPALIVE_DEFAULT)

    def normalize_interface_names(self, param):
        # if param:
        #     for _k, val in iteritems(param):
        #         val["name"] = normalize_interface(val["name"])
        return param
