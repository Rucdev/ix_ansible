#
# Copyright 2023 AP Communications
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""The ix_l3_interfaces class.

It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to it's desired end-state is
created.
"""

from __future__ import annotations

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
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.l3_interfaces import (
    L3InterfacesTemplate,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.utils.utils import (
    validate_ipv4,
    validate_ipv6,
)

if TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule


class L3Interfaces(ResourceModule):
    """The ix_l3_interfaces class."""

    def __init__(self, module: AnsibleModule) -> None:
        """Set up the resource module with the argument spec and the template."""
        super().__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="l3_interfaces",
            tmplt=L3InterfacesTemplate(),
        )
        self.parsers = [
            "ipv4.address",
            # "ipv4.dhcp",
            "ipv6.address",
            "ipv6.autoconfig",
        ]

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
        wantd = {each["name"]: each for each in self.want or []}
        haved = {each["name"]: each for each in self.have or []}

        for each in wantd, haved:
            self.list_to_dict(each)

        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        if self.state == "deleted":
            haved = {k: v for k, v in haved.items() if k in wantd or not wantd}
            wantd = {}

        # remove superfluous config
        if self.state in ["overridden", "deleted"]:
            for k, have in haved.items():
                if k not in wantd:
                    self._compare(want={}, have=have)

        for k, want in wantd.items():
            self._compare(want=want, have=haved.pop(k, {}))

    def _compare(self, want: dict, have: dict) -> None:
        begin = len(self.commands)
        self._compare_lists(want=want, have=have)
        if len(self.commands) != begin:
            self.commands.insert(
                begin,
                self._tmplt.render(want or have, "name", negate=False),
            )

    def _compare_lists(self, want: dict, have: dict) -> None:
        for afi in ("ipv4", "ipv6"):
            wacls = want.pop(afi, {})
            hacls = have.pop(afi, {})
            self._compare_primaries(afi, wacls, hacls)
            self._compare_secondaries(afi, wacls, hacls)
            # remove remaining items in have for replaced
            # these can be subnets that are no longer used
            # or secondaries that have moved to primary
            # or primary that has moved to secondary
            for entry in hacls.values():
                self.validate_ips(afi, have=entry)
                self.compare(parsers=self.parsers, want={}, have={afi: entry})

    def _compare_primaries(self, afi: str, wacls: dict, hacls: dict) -> None:
        """Compare the primary addresses; matched ones are removed from hacls."""
        for key, entry in wacls.items():
            if entry.get("secondary", False) is True:
                continue
            # entry is set as primary
            hacl = hacls.get(key, {})
            if hacl.get("secondary", False) is True:
                hacl = {}
            self.validate_ips(afi, want=entry, have=hacl)

            if hacl:
                hacls.pop(key, {})

            self.compare(
                parsers=self.parsers,
                want={afi: entry},
                have={afi: hacl},
            )

    def _compare_secondaries(self, afi: str, wacls: dict, hacls: dict) -> None:
        """Compare the secondary addresses; matched ones are removed from hacls."""
        for key, entry in wacls.items():
            if entry.get("secondary", False) is False:
                continue
            # entry is set as secondary
            hacl = hacls.get(key, {})
            # hacl is set as primary, if wacls has no other primary entry we must keep
            # this entry as primary (so we'll compare entry to hacl and not
            # generate commands)
            if hacl.get("secondary", False) is False and list(
                filter(
                    lambda w: w.get("secondary", False) is False,
                    wacls.values(),
                ),
            ):
                # another primary is in wacls
                hacl = {}
            self.validate_ips(afi, want=entry, have=hacl)

            if hacl:
                hacls.pop(key, {})

            self.compare(
                parsers=self.parsers,
                want={afi: entry},
                have={afi: hacl},
            )

    def purge(self, have: dict) -> None:
        """Handle operation for purged state."""
        self.commands.append(self._tmplt.render(have, "interface", negate=True))

    def normalize_interface_names(self, param: dict) -> dict:
        """Return param unchanged; IX interface names need no normalization."""
        return param

    def validate_ips(
        self,
        afi: str,
        want: dict | None = None,
        have: dict | None = None,
    ) -> None:
        """Fail the module unless the address in want and in have has a valid prefix length.

        Each address must be "<address>/<prefix length>" with a prefix length in
        range for afi. The address part itself is not checked.
        """
        for entry in (want, have):
            if not entry or not entry.get("address"):
                continue
            if afi == "ipv4":
                validate_ipv4(self._module, entry["address"])
            elif afi == "ipv6":
                validate_ipv6(entry["address"], self._module)

    def list_to_dict(self, param: dict) -> None:
        """Turn the address lists of each interface into dicts keyed by address."""
        if param:
            for val in param.values():
                if "ipv4" in val:
                    val["ipv4"] = self._ipv4_to_dict(val["ipv4"])
                if "ipv6" in val:
                    val["ipv6"] = self._ipv6_to_dict(val["ipv6"])

    @staticmethod
    def _ipv4_to_dict(entries: list) -> dict:
        """Key the IPv4 address entries by address."""
        temp = {}
        for each in entries:
            if each.get("address") and each.get("address") != "dhcp":
                temp.update({each["address"]: each})
            elif each.get("address") == "dhcp":
                # deprecated attribute
                temp.update(
                    {
                        "dhcp": {
                            "dhcp": {
                                "client_id": each.get("dhcp_client"),
                                "hostname": each.get("dhcp_hostname"),
                            },
                        },
                    },
                )
            if not each.get("address"):
                temp.update({next(iter(each.keys())): each})
        return temp

    @staticmethod
    def _ipv6_to_dict(entries: list) -> dict:
        """Key the IPv6 address entries by lower-case address."""
        temp = {}
        for each in entries:
            if each.get("address"):
                each["address"] = each["address"].lower()
                temp.update({each["address"]: each})
            if not each.get("address"):
                temp.update({next(iter(each.keys())): each})
        return temp
