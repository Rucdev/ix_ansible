# -*- coding: utf-8 -*-
# Copyright 2024 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The Ospf_interfaces parser templates file. This contains
a list of parser definitions and associated functions that
facilitates both facts gathering and native command generation for
the given network resource.
"""

import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)

class Ospf_interfacesTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Ospf_interfacesTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "name",
            "getval": re.compile(
                r"""
                ^interface\s(?P<name>\S+)
                $""", re.VERBOSE),
            "setval": "interface {{ name }}",
            "result": {
                "{{ name }}": {
                    "name": "{{ name }}",
                    "address_family": {}
                }
            },
            "shared": True
        },
        {
            "name": "authentication",
            "getval": re.compile(
                r"""
                \s+ip\sospf\sauthentication
                (\s(?P<message_digest>message-digest))?
                (\s(?P<isnull>null))?
                $""", re.VERBOSE),
            "setval": "ip ospf authentication"
                "{{ (' ' + message-digest) if authentication.message_digest is defined else '' }}"
                "{{ (' ' + null) if authentication.null is defined else '' }}",
            "result": {
                "{{ name }}": {
                    "address_family": {
                        "ip": {
                            "afi": "ipv4",
                            "authentication": {
                                "message_digest": "{{ not not message_digest }}",
                                "null": "{{ not not isnull }}",
                            },
                        },
                    },
                },
            },
        },
        {
            "name": "cost",
            "getval": re.compile(
                r"""
                \s+ip\sospf\scost\s(?P<cost>\S+)
                $""",
                re.VERBOSE
            ),
            "setval": "ip ospf cost {{ cost }}",
            "result": {
                "{{ name }}": {
                    "address_family": {
                        "ip": {
                            "afi": "ipv4",
                            "cost": "{{ cost }}"
                        }
                    }
                }
            }
        },
        {
            "name": "dead_interval",
            "getval": re.compile(
                r"""
                \s+ip\sospf\sdead-interval\s(?P<dead_interval>\S+)
                $""",
                re.VERBOSE
            ),
            "setval": "ip ospf dead-interval {{ dead_interval }}",
            "result":  {
                "{{ name }}": {
                    "address_family": {
                        "ip": {
                            "afi": "ipv4",
                            "dead_interval": "{{ dead_interval }}"
                        }
                    }
                }
            }
        },
        {
            "name": "hello_interval",
            "getval": re.compile(
                r"""
                \s+ip\sospf\shello-interval\s(?P<hello_interval>\S+)
                $""",
                re.VERBOSE
            ),
            "setval": "ip ospf hello-interval {{ hello_interval }}",
            "result": {
                "{{ name }}": {
                    "address_family": {
                        "ip": {
                            "afi": "ipv4",
                            "hello_interval": "{{ hello_interval }}"
                        }
                    }
                }
            }
        },
        {
            "name": "message_digest_key",
            "getval": re.compile(
                r"""
                \s+ip\sospf\smessage-digest
                \s(?P<key_id>\S+)
                \s(?P<password>\S+)
                $""",
                re.VERBOSE
            ),
            "setval": "ip ospf message-digest {{ key_id }} {{ password}}",
            "result": {
                "{{ name }}": {
                    "address_family": {
                        "ip": {
                            "afi": "ipv4",
                            "message_digest_key": {
                                "key_id": "{{ key_id }}",
                                "password": "{{ password }}"
                            }
                        }
                    }
                }
            }
        },
        {
            "name": "mtu_ignore",
            "getval": re.compile(
                r"""
                \s+ip\sospf\s(?P<mtu_ignore>mtu-ignore)
                $""",
                re.VERBOSE
            ),
            "setval": "ip ospf mtu-ignore",
            "result": {
                "{{ name }}": {
                    "address_family": {
                        "ip": {
                            "afi": "ipv4",
                            "mtu_ignore": "{{ true if mtu_ignore is defined else false }}"
                        }
                    }
                }
            }
        },
        {
            "name": "neighbor",
            "getval": re.compile(
                r"""
                \sip\sospf\sneighbor
                \s(?P<address>\S+)
                (\spoll-interval(?P<interval>\S+))?
                (\spriority(?P<priority>\S+))?
                $""",
                re.VERBOSE
            ),
            "setval": "ip ospf neighbor {{ address }}"
            "{{ (' poll-interval' + interval) if interval is defined else '' }}"
            "{{ (' priority' + priority) if priority is defined else '' }}",
            "result": {
                "{{ name }}": {
                    "address_family": {
                        "ip": {
                            "neighbor": [
                                {
                                    "address": "{{ address }}",
                                    "interval": "{{ interval }}",
                                    "interval": "{{ interval }}"
                                }
                            ]
                        }
                    }
                }
            }
        },
        {
            "name": "interface_type",
            "getval": re.compile(
                r"""
                \sip\sospf\snetwork\s(?P<interface_type>\S+)
                $""",
                re.VERBOSE
            ),
            "setval": "ip ospf network {{ interface_type }}",
            "result": {
                "{{ name }}": {
                    "address_family": {
                        "ip": {
                            "interface_type": "{{ interface_type }}"
                        }
                    }
                }
            }
        }
    ]
    # fmt: on
