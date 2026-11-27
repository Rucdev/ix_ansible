#
# Copyright 2023 AP Communications
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


# utils


"""Address validation helpers."""

from __future__ import annotations

import ipaddress
import re

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule

# An address with a prefix length, "<address>/<length>", splits into two parts.
ADDRESS_PARTS = 2
MAX_PREFIX_LENGTH = {4: 32, 6: 128}
PREFIX_LENGTH_RE = re.compile(r"[0-9]+")


def validate_ipv4(module: AnsibleModule, value: str) -> None:
    """Fail the module unless value is an IPv4 address with a prefix length."""
    if value:
        _validate_address(module, value, version=4)


def validate_ipv6(value: str, module: AnsibleModule) -> None:
    """Fail the module unless value is an IPv6 address with a prefix length."""
    if value:
        _validate_address(module, value, version=6)


def _validate_address(module: AnsibleModule, value: str, *, version: int) -> None:
    """Fail the module unless value is "<address>/<prefix length>" of the IP version."""
    parts = value.split("/")
    if len(parts) != ADDRESS_PARTS:
        module.fail_json(
            msg=f"address format is <ipv{version} address>/<mask>, got invalid format {value}",
        )
        return

    address, length = parts
    max_length = MAX_PREFIX_LENGTH[version]
    if not PREFIX_LENGTH_RE.fullmatch(length) or int(length) > max_length:
        module.fail_json(
            msg=f"invalid value for mask: {length}, mask should be in range 0-{max_length}",
        )
        return

    try:
        parsed = ipaddress.ip_address(address)
    except ValueError:
        parsed = None
    if parsed is None or parsed.version != version:
        module.fail_json(
            msg=f"invalid value for address: {address}, address should be an IPv{version} address",
        )
