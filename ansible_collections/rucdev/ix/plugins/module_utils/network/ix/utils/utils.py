#
# Copyright 2023 AP Communications
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


# utils


from ansible.module_utils.common.network import is_masklen, to_netmask


def validate_ipv4(module, value):
    if value:
        address = value.split("/")
        if len(address) != 2:
            module.fail_json(
                msg=f"address format is <ipv4 address>/<mask>, got invalid format {value}",
            )

        if not is_masklen(address[1]):
            module.fail_json(
                msg=f"invalid value for mask: {address[1]}, mask should be in range 0-32",
            )


def validate_ipv6(value, module):
    if value:
        address = value.split("/")
        if len(address) != 2:
            module.fail_json(
                msg=f"address format is <ipv6 address>/<mask>, got invalid format {value}",
            )
        elif not 0 <= int(address[1]) <= 128:
            module.fail_json(
                msg=f"invalid value for mask: {address[1]}, mask should be in range 0-128",
            )


def validate_n_expand_ipv4(module, want):
    # Check if input IPV4 is valid IP and expand IPV4 with its subnet mask
    ip_addr_want = want.get("address")
    if ip_addr_want == "default":
        return f"0.0.0.0 {to_netmask('0')}"
    if len(ip_addr_want.split(" ")) > 1:
        return ip_addr_want
    validate_ipv4(module, ip_addr_want)
    ip = ip_addr_want.split("/")
    if len(ip) == 2:
        ip_addr_want = f"{ip[0]} {to_netmask(ip[1])}"

    return ip_addr_want
