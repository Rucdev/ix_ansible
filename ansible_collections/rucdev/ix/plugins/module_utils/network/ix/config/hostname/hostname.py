#
# -*- coding: utf-8 -*-
# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The ix_hostname config file.
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to its desired end-state is
created.
"""

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.facts import (
    Facts,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.hostname import (
    HostnameTemplate,
)


class Hostname(ResourceModule):
    """
    The ix_hostname config class
    """

    def __init__(self, module):
        super(Hostname, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="hostname",
            tmplt=HostnameTemplate(),
        )
        self.parsers = ["hostname"]

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

        hostname is a single value, so merged / replaced / overridden all
        behave the same: set the hostname when it differs from the device.
        """
        wantd = self.want or {}
        haved = self.have or {}

        if self.state == "deleted":
            if haved.get("hostname"):
                self.commands.append("no hostname")
            return

        if wantd.get("hostname") and wantd != haved:
            self.compare(parsers=self.parsers, want=wantd, have=haved)
