#
# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#


"""The ix_hostname config file.
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
    """The ix_hostname config class"""

    def __init__(self, module):
        super().__init__(
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
            self._validate_want()
            self.generate_commands()
            self.run_commands()
        return self.result

    def _validate_want(self):
        """IX accepts ``hostname a b`` without error but stores only ``a``,
        which would make the module report success and never converge.
        Reject whitespace up front instead.
        """
        hostname = (self.want or {}).get("hostname")
        if hostname is not None and (
            not hostname or any(c.isspace() for c in hostname)
        ):
            self._module.fail_json(
                msg="hostname must be a non-empty string without whitespace: %r"
                % hostname,
            )

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
