from ansible.module_utils.connection import Connection, ConnectionError
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_text, to_bytes
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_list,
)
import json

_DEVICE_CONFIGS = {}


def get_connection(module):
    print("called get connection")
    if hasattr(module, "_ix_connection"):
        return module._ix_connection

    capabilities = get_capabilities(module)
    network_api = capabilities.get("network_api")
    if network_api == "cliconf":
        module._ix_connection = Connection(module._socket_path)
    else:
        module.fail_json(msg=f"Invalid connection type {network_api}")

    return module._ix_connection


def get_capabilities(module):
    if hasattr(module, "_ix_capabilities"):
        return module._ix_capabilities

    try:
        capabilities = Connection(module._socket_path).get_capabilities()
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc, errors="surrogate_then_replace"))
    module._ix_capabilities = json.loads(capabilities)
    return module._ix_capabilities


def get_defaults_flag(module):
    connection = get_connection(module)
    try:
        out = connection.get_defaults_flag()
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc, errors="surrogate_then_replace"))

    return to_text(out, errors="surrogate_then_replace").strip()


def get_config(module, flags=None):
    flags = to_list(flags)

    section_filter = False
    if flags and "section" in flags[-1]:
        section_filter = True

    flag_str = " ".join(flags)

    try:
        return _DEVICE_CONFIGS[flag_str]
    except KeyError:
        connection = get_connection(module)
        try:
            out = connection.get_config(flags=flags)
        except ConnectionError as exc:
            if section_filter:
                out = get_config(module, flags=flags[:-1])
            else:
                module.fail_json(msg=to_text(exc, errors="surrogate_then_replace"))
        cfg = to_text(out, errors="surrogate_then_replace").strip()
        _DEVICE_CONFIGS[flag_str] = cfg
        return cfg


def run_commands(module, commands, check_rc=True, configure=False):
    connection = get_connection(module)
    try:
        if configure:
            return connection.run_configs(commands=commands, check_rc=check_rc)
        else:
            return connection.run_commands(commands=commands, check_rc=check_rc)
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc))
