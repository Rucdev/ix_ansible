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
                \s+(?P<afi>ip|ipv6)
                \sospf\scost\s(?P<cost>\S+)
                $""",
                re.VERBOSE
            ),
            "setval": "{{ 'ip' if afi == 'ipv4' else 'ipv6' }} ospf cost {{ cost }}",
            "result": {
                "{{ name }}": {
                    "address_family": {
                        "{{ afi }}": {
                            "afi": "{{ 'ipv4' if afi == 'ip' else 'ipv6' }}",
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
                \s+(?P<afi>ip|ipv6)
                \sospf\sdead-interval\s(?P<dead_interval>\S+)
                $""",
                re.VERBOSE
            ),
            "setval": "{{ 'ip' if afi == 'ipv4' else 'ipv6' }} ospf dead-interval {{ dead_interval }}",
            "result":  {
                "{{ name }}": {
                    "address_family": {
                        "{{ afi }}": {
                            "afi": "{{ 'ipv4' if afi == 'ip' else 'ipv6' }}",
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
                \s+(?P<afi>ip|ipv6)
                \sospf\shello-interval\s(?P<hello_interval>\S+)
                $""",
                re.VERBOSE
            ),
            "setval": "{{ 'ip' if afi == 'ipv4' else 'ipv6' }} ospf hello-interval {{ hello_interval }}",
            "result": {
                "{{ name }}": {
                    "address_family": {
                        "{{ afi }}": {
                            "afi": "{{ 'ipv4' if afi == 'ip' else 'ipv6' }}",
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
                \s+(?P<afi>ip|ipv6)
                \sospf\sneighbor
                \s(?P<address>\S+)
                (\spoll-interval\s(?P<interval>\S+))?
                (\spriority\s(?P<priority>\S+))?
                $""",
                re.VERBOSE
            ),
            "setval": "{{ 'ip' if afi == 'ipv4' else 'ipv6' }} ospf neighbor {{ address }}"
            "{{ (' poll-interval' + interval) if interval is defined else '' }}"
            "{{ (' priority' + priority) if priority is defined else '' }}",
            "result": {
                "{{ name }}": {
                    "address_family": {
                        "{{ afi }}": {
                            "afi": "{{ 'ipv4' if afi == 'ip' else 'ipv6' }}",
                            "neighbor": [
                                {
                                    "address": "{{ address }}",
                                    "interval": "{{ interval }}",
                                    "priority": "{{ priority }}"
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
                \s+ip\sospf\snetwork\s(?P<interface_type>\S+)
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
        },
        {
            "name": "priority",
            "getval": re.compile(
                r"""
                \s+(?P<afi>ip|ipv6)
                \spriority\s(?P<priority>\S+)
                $""",
                re.VERBOSE
            ),
            "setval": "{{ 'ip' if afi == 'ipv4' else 'ipv6' }} ospf priority {{ priority }}",
            "result": {
                "{{ name }}": {
                    "address_family": {
                        "{{ afi }}": {
                            "afi": "{{ 'ipv4' if afi == 'ip' else 'ipv6' }}",
                            "priority": "{{ priority }}"
                        }
                    }
                }
            }
        },
        {
            "name": "retransmit_interval",
            "getval": re.compile(
                r"""
                \s+(?P<afi>ip|ipv6)
                \sospf\sretransmit-interval
                \s(?P<retransmit_interval>\S+)
                $""",
                re.VERBOSE
            ),
            "setval": "{{ 'ip' if afi == 'ipv4' else 'ipv6' }} ospf retransmit-interval {{ retransmit_interval }}",
            "result": {
                "{{ name }}": {
                    "address_family": {
                        "{{ afi }}": {
                            "afi": "{{ 'ipv4' if afi == 'ip' else 'ipv6' }}",
                            "retransmit_interval": "{{ retransmit_interval }}"
                        }
                    }
                }
            }
        },
        {
            "name": "transmit_delay",
            "getval": re.compile(
                r"""
                \s+(?P<afi>ip|ipv6)
                \sospf\stransmit-delay\s(?P<transmit_delay>\S+)
                $""",
                re.VERBOSE
            ),
            "setval": "{{ 'ip' if afi == 'ipv4' else 'ipv6' }} ospf transmit-delay {{ transmit_delay }}",
            "result": {
                "{{ name }}": {
                    "address_family": {
                        "{{ afi }}": {
                            "afi": "{{ 'ipv4' if afi == 'ip' else 'ipv6' }}",
                            "transmit_delay": "{{ transmit_delay }}"
                        }
                    }
                }
            }
        }
    ]
    # fmt: on
