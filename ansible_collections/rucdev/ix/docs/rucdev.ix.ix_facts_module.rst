.. _rucdev.ix.ix_facts_module:


******************
rucdev.ix.ix_facts
******************

**Get facts about ix devices.**


Version added: 1.1.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Collects facts from network devices running the ix operating system. This module places the facts gathered in the fact tree keyed by the respective resource name.  The facts module will always collect a base set of facts from the device and can enable or disable collection of additional facts.




Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
            <th width="100%">Comments</th>
        </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>gather_network_resources</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li>all</li>
                                    <li>hostname</li>
                                    <li>interfaces</li>
                                    <li>l3_interfaces</li>
                                    <li>ospf_interfaces</li>
                                    <li>ospfv2</li>
                                    <li>ospfv3</li>
                                    <li>static_routes</li>
                        </ul>
                </td>
                <td>
                        <div>The resources to collect facts for, or <code>all</code> for every resource.</div>
                        <div>Values with an initial <code>!</code>, which exclude a resource, are not accepted.</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>gather_subset</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=string</span>
                    </div>
                </td>
                <td>
                        <b>Default:</b><br/><div style="color: blue">["min"]</div>
                </td>
                <td>
                        <div>Accepted for compatibility with other network collections, but not used. This collection does not gather legacy facts, so only the resources in <code>gather_network_resources</code> are collected.</div>
                </td>
            </tr>
    </table>
    <br/>




Examples
--------

.. code-block:: yaml

    # Collect the facts of every resource
    - rucdev.ix.ix_facts:
        gather_network_resources: all

    # Collect only the interfaces facts
    - rucdev.ix.ix_facts:
        gather_network_resources:
          - interfaces




Status
------


Authors
~~~~~~~

- Yushi Takeda (@Rucdev)
