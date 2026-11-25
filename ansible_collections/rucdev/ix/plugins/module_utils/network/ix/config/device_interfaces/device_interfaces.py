#
# Copyright 2023 AP Communications
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""The ix_Device_interfaces class
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to it's desired end-state is
created.
"""

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)

from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.facts import (
    Facts,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.device_interfaces import (
    DeviceInterfacesTemplate,
)


class DeviceInterfaces(ResourceModule):
    """The ix_Device_interfaces class."""

    def __init__(self, module) -> None:
        super().__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="device_interfaces",
            tmplt=DeviceInterfacesTemplate(),
        )
        self.parsers = [
            "duplex",
            "keepalive",
            "mdix",
            "output_buffer",
            "sflow.max_header_size",
            "sflow.polling_interval",
            "sflow.sampling_rate.in",
            "sflow.sampling_rate.out",
            "speed",
        ]

    def execute_module(self):
        """Execute the module.

        :rtype: A dictionary
        :returns: The result from module execution
        """
        if self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self) -> None:
        """Generate configuration commands to send based on
        want, have and desired state.
        """
        wantd = {entry["name"]: entry for entry in self.want}
        haved = {entry["name"]: entry for entry in self.have}

        # if state is merged, merge want onto have and then compare
        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        # if state is deleted, empty out wantd and set haved to wantd
        if self.state in ["deleted", "purged"]:
            haved = {k: v for k, v in haved.items() if k in wantd or not wantd}
            wantd = {}

        # remove superfluous config for overridden and deleted
        if self.state in ["overridden", "deleted"]:
            for k, have in haved.items():
                if k not in wantd:
                    self._compare(want={}, have=have)

        if self.state == "purged":
            for have in haved.values():
                self.purge(have)
        else:
            for k, want in wantd.items():
                self._compare(want=want, have=haved.pop(k, {}))

    def _compare(self, want, have) -> None:
        """Leverages the base class `compare()` method and
        populates the list of commands to be run by comparing
        the `want` and `have` data with the `parsers` defined
        for the DeviceInterfaces network resource.
        """
        begin = len(self.commands)
        self.compare(parsers=self.parsers, want=want, have=have)

        if len(self.commands) != begin:
            self.commands.insert(
                begin,
                self._tmplt.render(want or have, "device", negate=False),
            )

    def purge(self, have) -> None:
        """Handle operation for purged state."""
        self.commands.append(self._tmplt.render(have, "device", negate=True))

    def normalize_interface_names(self, param):
        return param
