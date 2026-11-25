#
# Copyright 2024 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#


"""The ix_ospf_interfaces config file.
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to its desired end-state is
created.
"""

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)

from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.facts import (
    Facts,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.ospf_interfaces import (
    Ospf_interfacesTemplate,
)


class Ospf_interfaces(ResourceModule):
    """The ix_ospf_interfaces config class."""

    # "ip ospf ..." commands that have no "ipv6 ospf ..." form in the IX
    # command reference (OSPFv3 authentication uses IPsec)
    IPV4_ONLY_OPTIONS = (
        "authentication_type",
        "authentication_key",
        "message_digest_key",
        "mtu_ignore",
        "interface_type",
    )

    def __init__(self, module) -> None:
        super().__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="ospf_interfaces",
            tmplt=Ospf_interfacesTemplate(),
        )
        self.parsers = []

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
        self._validate_want()
        wantd = self._list_to_dict(self.want, "want")
        haved = self._list_to_dict(self.have)

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
                    self._compare(want={}, have=have, interface=k)

        for k, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(k, {}), interface=k)

    def _validate_want(self) -> None:
        """Reject IPv4-only options unless afi is ipv4. Their setvals always
        render "ip ospf ...", so under afi ipv6 they would change the OSPFv2
        settings, and without afi they are silently ignored.
        """
        for intf in self.want or []:
            for af in intf.get("address_family") or []:
                if af.get("afi") == "ipv4":
                    continue
                invalid = [
                    opt for opt in self.IPV4_ONLY_OPTIONS if af.get(opt) is not None
                ]
                if invalid:
                    self._module.fail_json(
                        msg="{}: {} can be used only with afi ipv4 (afi: {}); IX "
                        "has no OSPFv3 equivalent".format(
                            intf.get("name"),
                            ", ".join(invalid),
                            af.get("afi") or "not set",
                        ),
                    )

    def _compare(self, want, have, interface) -> None:
        """Leverages the base class `compare()` method and
        populates the list of commands to be run by comparing
        the `want` and `have` data with the `parsers` defined
        for the Ospf_interfaces network resource.
        """
        begin = len(self.commands)
        self._compare_afi(want=want, have=have)
        if len(self.commands) != begin:
            self.commands.insert(
                begin,
                self._tmplt.render({"name": interface}, "name", False),
            )

    def _compare_afi(self, want, have) -> None:
        parsers = [
            "name",
            "authentication_type",
            "authentication_key",
            "cost",
            "dead_interval",
            "hello_interval",
            "interface_type",
            "message_digest_key",
            "mtu_ignore",
            "neighbor_v2",
            "neighbor_v3",
            "priority",
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
