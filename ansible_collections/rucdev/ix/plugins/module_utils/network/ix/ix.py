# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# (c) 2016 Red Hat Inc.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

from ansible.module_utils.connection import Connection, ConnectionError
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
