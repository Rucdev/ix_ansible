#
# -*- coding: utf-8 -*-
# Copyright 2026 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The ix_l2_interfaces config file.
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to its desired end-state is
created.
"""

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.facts.facts import (
    Facts,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.l2_interfaces import (
    L2_interfacesTemplate,
)

DEFAULT_TPID = "8100"
TPID_MIN = 0x5DD

RESTART_WARNING = (
    "IX may need a router restart before an encapsulation dot1q change takes "
    "effect (it says so when a sub-interface switches between PPPoE and dot1q). "
    "This module does not restart the router."
)


def normalize_tpid(tpid):
    """Return the TPID as IX shows it (lower-case hex without leading zeros),
    or None if it is not a hex number."""
    if tpid is None:
        return DEFAULT_TPID
    value = str(tpid).strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    if not re.match(r"^[0-9a-f]{1,4}$", value):
        return None
    return format(int(value, 16), "x")


class L2_interfaces(ResourceModule):
    """
    The ix_l2_interfaces config class
    """

    def __init__(self, module):
        super(L2_interfaces, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="l2_interfaces",
            tmplt=L2_interfacesTemplate(),
        )
        self._kept_dot1q = []

    def execute_module(self):
        """Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        if self.state not in ["parsed", "gathered"]:
            self._validate_want()
            self.generate_commands()
            if any(c.startswith("encapsulation dot1q ") for c in self.commands):
                self.warnings.append(RESTART_WARNING)
            if self._kept_dot1q:
                self.warnings.append(
                    "encapsulation dot1q was left unchanged on %s: IX has no "
                    "'no encapsulation dot1q' for Ethernet sub-interfaces. "
                    "Remove the sub-interface itself (no interface NAME) to "
                    "drop the VLAN tag." % ", ".join(self._kept_dot1q)
                )
            self.run_commands()
        return self.result

    def _validate_want(self):
        for entry in self.want or []:
            name = entry["name"]
            dot1q = entry.get("dot1q")
            if dot1q:
                if name.endswith(".0"):
                    self._module.fail_json(
                        msg="dot1q can only be set on a sub-interface "
                        "(e.g. GigaEthernet0.1), not on %s" % name
                    )
                if not 1 <= dot1q["vlan_id"] <= 4095:
                    self._module.fail_json(
                        msg="dot1q.vlan_id must be between 1 and 4095: %s (%s)"
                        % (dot1q["vlan_id"], name)
                    )
                tpid = normalize_tpid(dot1q.get("tpid"))
                if tpid is None or int(tpid, 16) < TPID_MIN:
                    self._module.fail_json(
                        msg="dot1q.tpid must be a hex value between 5dd and ffff: "
                        "%s (%s)" % (dot1q.get("tpid"), name)
                    )
                dot1q["tpid"] = tpid
            bridge_group = entry.get("bridge_group")
            if bridge_group and not 1 <= bridge_group["group"] <= 65535:
                self._module.fail_json(
                    msg="bridge_group.group must be between 1 and 65535: %s (%s)"
                    % (bridge_group["group"], name)
                )

    def generate_commands(self):
        """Generate configuration commands to send based on
        want, have and desired state.
        """
        wantd = {entry["name"]: entry for entry in self.want or []}
        haved = {entry["name"]: entry for entry in self.have or []}
        for entry in haved.values():
            if entry.get("dot1q"):
                entry["dot1q"]["tpid"] = normalize_tpid(entry["dot1q"].get("tpid"))

        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        if self.state == "deleted":
            haved = {k: v for k, v in haved.items() if k in wantd or not wantd}
            wantd = {}

        # remove superfluous config
        if self.state in ["overridden", "deleted"]:
            for name, have in haved.items():
                if name not in wantd:
                    self._compare(want={"name": name}, have=have)

        for name, want in wantd.items():
            self._compare(want=want, have=haved.get(name, {"name": name}))

    def _compare(self, want, have):
        begin = len(self.commands)

        wdot1q = want.get("dot1q")
        hdot1q = have.get("dot1q")
        if wdot1q and wdot1q != hdot1q:
            self.addcmd(want, "dot1q")
        elif hdot1q and not wdot1q:
            self._kept_dot1q.append(want["name"])

        # An interface belongs to at most one bridge group; IX rejects a
        # second "bridge-group N" with "Multiple VLAN not supported", so the
        # old membership has to go first.
        wbridge = want.get("bridge_group")
        hbridge = have.get("bridge_group")
        if hbridge and hbridge != wbridge:
            self.addcmd(have, "bridge_group", True)
        if wbridge and wbridge != hbridge:
            self.addcmd(want, "bridge_group")

        if len(self.commands) != begin:
            self.commands.insert(begin, self._tmplt.render(want, "name", False))
