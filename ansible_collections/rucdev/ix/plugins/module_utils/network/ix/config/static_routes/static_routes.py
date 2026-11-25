#
# Copyright 2024 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#


"""The ix_static_routes config file.
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to its desired end-state is
created.

Device behaviour this relies on (verified on IX2215 10.10.29):
- A route is identified by vrf + afi + dest + gateway + interface
  (+ connected / dhcp / ra). See ROUTE_IDENTITY.
- Re-entering an existing route REPLACES its options (distance/metric/tag),
  so changing options needs no "no" command first.
- "no ip route <identity>" removes the route regardless of its options.
- running-config never shows default values (distance 1, metric 1), so they
  are treated as "not specified" here (see DEFAULT_OPTIONS).
"""

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)

from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.facts import (
    Facts,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.static_routes import (
    StaticRoutesTemplate,
)

ROUTE_IDENTITY = (
    "vrf",
    "afi",
    "dest",
    "forward_router_address",
    "interface",
    "connected",
    "dhcp",
    "ra",
)
ROUTE_OPTIONS = ("distance", "metric", "tag")

# IX omits these from running-config, so a value equal to the default is the
# same as not specifying it. Without this, "distance: 1" would never be
# idempotent. To go back to the default, use replaced/overridden (merged keeps
# the device's current value for options that are not specified).
DEFAULT_OPTIONS = {"distance": 1, "metric": 1}


class StaticRoutes(ResourceModule):
    """The ix_static_routes config class."""

    def __init__(self, module) -> None:
        super().__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="static_routes",
            tmplt=StaticRoutesTemplate(),
        )

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
        wantd = self._flatten(self.want, validate=True)
        haved = self._flatten(self.have)

        if self.state == "deleted":
            self._delete(haved)
            return

        if self.state == "merged":
            for key, want in wantd.items():
                have = haved.get(key, {})
                # options not given keep the device value (IX would otherwise
                # reset them, because re-entering a route replaces its options)
                merged = dict(have, **want)
                if self._same(merged, have) is False:
                    self.addcmd(merged, merged["afi"])
            return

        # replaced: only destinations present in want are managed
        # overridden: every route on the device is managed
        if self.state == "replaced":
            scope = {self._dest_of(k) for k in wantd}
            in_scope = {k: v for k, v in haved.items() if self._dest_of(k) in scope}
        else:
            in_scope = haved

        # add/update first, then remove, so a destination is not left
        # without any route while the change is applied
        for key, want in wantd.items():
            if self._same(want, in_scope.get(key)) is False:
                self.addcmd(want, want["afi"])
        for key, have in in_scope.items():
            if key not in wantd:
                self.addcmd(have, have["afi"], negate=True)

    def _delete(self, haved) -> None:
        targets = (
            haved.values()
            if not self.want
            else [
                have for key, have in haved.items() if self._matches_delete_filter(have)
            ]
        )
        for have in targets:
            self.addcmd(have, have["afi"], negate=True)

    def _matches_delete_filter(self, have) -> bool:
        """Deleted with config: a vrf / afi / dest without next_hops selects
        every route below it; a next_hop selects that route only.
        """
        for entry in self.want:
            if (entry.get("vrf") or None) != have.get("vrf"):
                continue
            afs = entry.get("address_families")
            if not afs:
                return True
            for af in afs:
                if af["afi"] == have["afi"] and self._af_matches(entry, af, have):
                    return True
        return False

    def _af_matches(self, entry, af, have):
        """Whether an address family of the deleted config selects the route."""
        routes = af.get("routes")
        if not routes:
            return True
        for route in routes:
            if route["dest"] != have["dest"]:
                continue
            if not route.get("next_hops"):
                return True
            for nh in route["next_hops"]:
                wanted = self._route(
                    entry.get("vrf"),
                    af["afi"],
                    route["dest"],
                    nh,
                )
                if self._key(wanted) == self._key(have):
                    return True
        return False

    @staticmethod
    def _same(want, have):
        """Compare two routes; gateway addresses are case-insensitive (IPv6)."""
        if not have:
            return False

        def norm(route):
            route = dict(route)
            if route.get("forward_router_address"):
                route["forward_router_address"] = route[
                    "forward_router_address"
                ].lower()
            return route

        return norm(want) == norm(have)

    @staticmethod
    def _dest_of(key):
        return key[:3]  # vrf, afi, dest

    @staticmethod
    def _key(route):
        key = []
        for field in ROUTE_IDENTITY:
            value = route.get(field)
            if field == "forward_router_address" and value:
                value = value.lower()
            key.append(value or None)
        return tuple(key)

    def _route(self, vrf, afi, dest, next_hop):
        route = {"afi": afi, "dest": dest}
        if vrf:
            route["vrf"] = vrf
        for field, value in next_hop.items():
            if value is None or value is False:
                continue
            if DEFAULT_OPTIONS.get(field) == value:
                continue
            route[field] = value
        return route

    def _flatten(self, config, *, validate=False):
        """[{vrf, address_families: [{afi, routes: [{dest, next_hops}]}]}]
        -> {identity key: flat route dict}.
        """
        routes = {}
        for entry in config or []:
            vrf = entry.get("vrf")
            for af in entry.get("address_families") or []:
                afi = af["afi"]
                for rt in af.get("routes") or []:
                    for nh in rt.get("next_hops") or []:
                        route = self._route(vrf, afi, rt["dest"], nh)
                        if validate:
                            self._validate(route)
                        routes[self._key(route)] = route
        return routes

    def _validate(self, route) -> None:
        afi = route["afi"]
        where = "{} route {}".format(afi, route["dest"])
        if not route.get("forward_router_address") and not route.get("interface"):
            self._module.fail_json(
                msg=f"{where}: next_hops needs forward_router_address and/or interface",
            )
        if afi == "ipv4" and route.get("ra"):
            self._module.fail_json(msg=f"{where}: ra is only valid for ipv6")
        if afi == "ipv6" and route.get("connected"):
            self._module.fail_json(msg=f"{where}: connected is only valid for ipv4")
        if afi == "ipv6" and route.get("vrf"):
            self._module.fail_json(msg=f"{where}: IX has no vrf for ipv6 route")
        for flag in ("dhcp", "ra"):
            if route.get(flag) and not route.get("interface"):
                self._module.fail_json(msg=f"{where}: {flag} requires interface")
