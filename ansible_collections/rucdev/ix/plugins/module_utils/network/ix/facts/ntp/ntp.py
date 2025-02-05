# -*- coding: utf-8 -*-
# Copyright 2025 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The ix ntp fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.rm_templates.ntp import (
    NtpTemplate,
)
from ansible_collections.rucdev.ix.plugins.module_utils.network.ix.argspec.ntp.ntp import (
    NtpArgs,
)

class NtpFacts(object):
    """ The ix ntp facts class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = NtpArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for Ntp network resource

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf

        :rtype: dictionary
        :returns: facts
        """
        facts = {}
        objs = []

        if not data:
            data = connection.get()

        # parse native config using the Ntp template
        ntp_parser = NtpTemplate(lines=data.splitlines(), module=self._module)
        objs = list(ntp_parser.parse().values())

        ansible_facts['ansible_network_resources'].pop('ntp', None)

        params = utils.remove_empties(
            ntp_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )

        facts['ntp'] = params['config']
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts
