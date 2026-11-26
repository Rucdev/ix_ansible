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

from __future__ import annotations

import ipaddress

from typing import TYPE_CHECKING

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
    OspfInterfacesTemplate,
)

if TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule

# fields that identify a neighbor entry; the other fields are its options
NEIGHBOR_KEYS = {
    "neighbor_v2": ("router_id",),
    "neighbor_v3": ("process_id", "router_id", "address"),
}


class OspfInterfaces(ResourceModule):
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

    def __init__(self, module: AnsibleModule) -> None:
        """Set up the resource module with the argument spec and the template."""
        super().__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="ospf_interfaces",
            tmplt=OspfInterfacesTemplate(),
        )
        self.parsers = []

    def execute_module(self) -> dict:
        """Execute the module.

        :rtype: A dictionary
        :returns: The result from module execution
        """
        if self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self) -> None:
        """Generate the commands to send based on want, have and the state."""
        self._validate_want()
        wantd = self._list_to_dict(self.want, "want")
        haved = self._list_to_dict(self.have)

        # if state is merged, merge want onto have and then compare
        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        # if state is deleted, empty out wantd and set haved to wantd
        if self.state == "deleted":
            haved = {k: v for k, v in haved.items() if k in wantd or not wantd}
            wantd = {}

        # remove superfluous config for overridden and deleted
        if self.state in ["overridden", "deleted"]:
            for k, have in haved.items():
                if k not in wantd:
                    self._compare(want={}, have=have, interface=k)

        for k, want in wantd.items():
            self._compare(want=want, have=haved.pop(k, {}), interface=k)

    def _validate_want(self) -> None:
        """Reject IPv4-only options unless afi is ipv4.

        Their setvals always render "ip ospf ...", so under afi ipv6 they would
        change the OSPFv2 settings, and without afi they are silently ignored.
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

    def _compare(self, want: dict, have: dict, interface: str) -> None:
        """Add the commands that change have into want, using the parsers."""
        begin = len(self.commands)
        self._compare_afi(want=want, have=have)
        if len(self.commands) != begin:
            self.commands.insert(
                begin,
                self._tmplt.render({"name": interface}, "name", negate=False),
            )

    def _compare_afi(self, want: dict, have: dict) -> None:
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
            "priority",
            "retransmit_interval",
            "transmit_delay",
        ]
        for afi in ("ipv4", "ipv6"):
            wafis = want.pop(afi, {})
            hafis = have.pop(afi, {})

            self.compare(parsers=parsers, want=wafis, have=hafis)
            self._compare_neighbors(want=wafis, have=hafis)

    def _compare_neighbors(self, want: dict, have: dict) -> None:
        """Add the commands that turn the neighbors of have into those of want.

        process_list_attr() keys the neighbors by their NEIGHBOR_KEYS fields.
        Re-entering a neighbor replaces all of its options on IX, so a changed
        entry is simply sent again; removal needs only the key.
        """
        for attr in NEIGHBOR_KEYS:
            wnbrs = want.get(attr, {})
            hnbrs = have.get(attr, {})
            for key, entry in wnbrs.items():
                if entry != hnbrs.get(key):
                    self.addcmd(entry, attr, negate=False)
            for key, entry in hnbrs.items():
                if key not in wnbrs:
                    self.addcmd(entry, attr, negate=True)

    def _list_to_dict(self, entry: list, attr_type: str | None = None) -> dict:
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

    def process_list_attr(self, add_fam: dict) -> dict:
        """Return the address families of an interface keyed by AFI."""
        item = {}
        for entry in add_fam.get("address_family", []):
            ag = dict(entry)
            for attr, keys in NEIGHBOR_KEYS.items():
                if ag.get(attr):
                    nbrs = [self._normalize_neighbor(nbr) for nbr in ag[attr]]
                    ag[attr] = {tuple(nbr.get(k) for k in keys): nbr for nbr in nbrs}
            item[ag.get("afi")] = ag
        return item

    @staticmethod
    def _normalize_neighbor(nbr: dict) -> dict:
        """Return nbr with its address in the form IX shows (lower case, compressed)."""
        nbr = dict(nbr)
        if nbr.get("address"):
            try:
                nbr["address"] = ipaddress.ip_address(str(nbr["address"])).compressed
            except ValueError:
                nbr["address"] = nbr["address"].lower()
        return nbr
