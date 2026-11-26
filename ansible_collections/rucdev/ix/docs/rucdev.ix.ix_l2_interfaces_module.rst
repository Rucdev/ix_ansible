.. _rucdev.ix.ix_l2_interfaces_module:


**************************
rucdev.ix.ix_l2_interfaces
**************************

**Resource module to configure L2 interfaces.**


Version added: 0.3.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- This module provides declarative management of the layer 2 settings of NEC IX interfaces, that is the 802.1Q VLAN tag of a sub-interface (``encapsulation dot1q``) and bridge group membership (``bridge-group``).




Parameters
----------

.. raw:: html

    <table  border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="3">Parameter</th>
            <th>Choices/<font color="blue">Defaults</font></th>
            <th width="100%">Comments</th>
        </tr>
            <tr>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>config</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=dictionary</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>A list of L2 interface options.</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>bridge_group</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Bridge group the interface belongs to (<code>bridge-group</code>).</div>
                        <div>Valid on Ethernet, BVI and Tunnel interfaces.</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>group</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Bridge group number, 1 to 65535.</div>
                </td>
            </tr>

            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>dot1q</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">dictionary</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>802.1Q VLAN tagging of the sub-interface (<code>encapsulation dot1q</code>).</div>
                        <div>Only valid on sub-interfaces, i.e. not on <code>GigaEthernetX.0</code>.</div>
                </td>
            </tr>
                                <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>tpid</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>TPID in hex, <code>5dd</code> to <code>ffff</code>. IX uses <code>8100</code> when it is omitted.</div>
                </td>
            </tr>
            <tr>
                    <td class="elbow-placeholder"></td>
                    <td class="elbow-placeholder"></td>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>vlan_id</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">integer</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>VLAN ID, 1 to 4095.</div>
                </td>
            </tr>

            <tr>
                    <td class="elbow-placeholder"></td>
                <td colspan="2">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>name</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>Full name of the interface, e.g. <code>GigaEthernet0.1</code>.</div>
                </td>
            </tr>

            <tr>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>running_config</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div>This option is used only with state <em>parsed</em>.</div>
                        <div>The value of this option should be the output received from the IX device by executing the command <b>show running-config interface</b>.</div>
                        <div>The state <em>parsed</em> reads the configuration from <code>running_config</code> option and transforms it into Ansible structured data as per the resource module&#x27;s argspec and the value is then returned in the <em>parsed</em> key within the result.</div>
                </td>
            </tr>
            <tr>
                <td colspan="3">
                    <div class="ansibleOptionAnchor" id="parameter-"></div>
                    <b>state</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">string</span>
                    </div>
                </td>
                <td>
                        <ul style="margin: 0; padding: 0"><b>Choices:</b>
                                    <li><div style="color: blue"><b>merged</b>&nbsp;&larr;</div></li>
                                    <li>replaced</li>
                                    <li>overridden</li>
                                    <li>deleted</li>
                                    <li>gathered</li>
                                    <li>rendered</li>
                                    <li>parsed</li>
                        </ul>
                </td>
                <td>
                        <div>The state the configuration should be left in.</div>
                </td>
            </tr>
    </table>
    <br/>


Notes
-----

.. note::
   - Tested against NEC IX version 10.10.29 on IX 2215.
   - This module works with connection ``network_cli``.
   - IX has no ``no encapsulation dot1q`` for Ethernet sub-interfaces, so the module never removes a VLAN tag. With ``replaced``, ``overridden`` and ``deleted`` the tag is left as it is and a warning names the interface. To drop the tag, remove the sub-interface (``no interface NAME``), for example with :ref:`rucdev.ix.ix_config <rucdev.ix.ix_config_module>`.
   - IX may need a router restart before an ``encapsulation dot1q`` change takes effect. The module sends the command but does not restart the router, and warns when it sends one.
   - An interface belongs to at most one bridge group. When the group changes, the module sends ``no bridge-group OLD`` before ``bridge-group NEW``.
   - Only bridge group membership is managed. ``bridge-group N port-protected``, ``bridge-group N port-table-size``, ``bridge-group N permanent-address`` and global bridge settings such as ``bridge irb enable`` are not, and ``no bridge-group N`` leaves those lines in place.
   - IX ties an interface to the group named in any of its ``bridge-group N ...`` lines, even without the ``bridge-group N`` membership line, and rejects any other group with ``% Multiple VLAN not supported``. Remove those lines (for example ``no bridge-group N port-protected``) before moving such an interface to another group; otherwise the task fails with that error.
   - Sub-interfaces are never created or removed on purpose, but setting ``dot1q`` or ``bridge_group`` on a sub-interface that does not exist yet creates it.



Examples
--------

.. code-block:: yaml

    # Using merged

    # Before state:
    # -------------
    # Router(config)# show running-config interface
    # interface GigaEthernet2.0
    #   no ip address
    #   shutdown
    # !
    # interface GigaEthernet2.1
    #   encapsulation pppoe
    #   auto-connect
    #   no ip address
    #   shutdown

    - name: Tag GigaEthernet2.1 with VLAN 10 and bridge it with GigaEthernet2.0
      rucdev.ix.ix_l2_interfaces:
        config:
          - name: GigaEthernet2.0
            bridge_group:
              group: 1
          - name: GigaEthernet2.1
            dot1q:
              vlan_id: 10
            bridge_group:
              group: 1
        state: merged

    # Commands sent:
    # - interface GigaEthernet2.0
    # - bridge-group 1
    # - interface GigaEthernet2.1
    # - encapsulation dot1q 10 tpid 8100
    # - bridge-group 1

    # After state:
    # ------------
    # Router(config)# show running-config interface
    # interface GigaEthernet2.0
    #   no ip address
    #   bridge-group 1
    #   shutdown
    # !
    # interface GigaEthernet2.1
    #   encapsulation dot1q 10 tpid 8100
    #   auto-connect
    #   no ip address
    #   bridge-group 1
    #   shutdown

    # Using replaced

    # Before state: as the After state above

    - name: Move GigaEthernet2.1 to bridge group 2
      rucdev.ix.ix_l2_interfaces:
        config:
          - name: GigaEthernet2.1
            dot1q:
              vlan_id: 10
            bridge_group:
              group: 2
        state: replaced

    # Commands sent:
    # - interface GigaEthernet2.1
    # - no bridge-group 1
    # - bridge-group 2

    # Using overridden

    # Before state: as the After state of merged

    - name: Keep bridge groups only on GigaEthernet2.1
      rucdev.ix.ix_l2_interfaces:
        config:
          - name: GigaEthernet2.1
            dot1q:
              vlan_id: 10
            bridge_group:
              group: 1
        state: overridden

    # Commands sent:
    # - interface GigaEthernet2.0
    # - no bridge-group 1

    # Using deleted

    # Before state: as the After state of merged

    - name: Remove L2 settings from GigaEthernet2.1
      rucdev.ix.ix_l2_interfaces:
        config:
          - name: GigaEthernet2.1
        state: deleted

    # Commands sent:
    # - interface GigaEthernet2.1
    # - no bridge-group 1

    # The VLAN tag stays (IX cannot remove it) and the module warns about it.

    # Using gathered

    - name: Gather L2 interface facts
      rucdev.ix.ix_l2_interfaces:
        state: gathered

    # Task Output:
    # gathered:
    #   - name: GigaEthernet2.0
    #     bridge_group:
    #       group: 1
    #   - name: GigaEthernet2.1
    #     dot1q:
    #       vlan_id: 10
    #       tpid: "8100"
    #     bridge_group:
    #       group: 1

    # Using rendered

    - name: Render the commands for provided configuration
      rucdev.ix.ix_l2_interfaces:
        config:
          - name: GigaEthernet0.1
            dot1q:
              vlan_id: 100
              tpid: 88a8
        state: rendered

    # Task Output:
    # rendered:
    #   - interface GigaEthernet0.1
    #   - encapsulation dot1q 100 tpid 88a8

    # Using parsed

    - name: Parse the provided configuration
      rucdev.ix.ix_l2_interfaces:
        running_config: |
          interface GigaEthernet0.1
            encapsulation dot1q 100 tpid 88a8
            bridge-group 3
        state: parsed

    # Task Output:
    # parsed:
    #   - name: GigaEthernet0.1
    #     dot1q:
    #       vlan_id: 100
    #       tpid: 88a8
    #     bridge_group:
    #       group: 3



Return Values
-------------
Common return values are documented `here <https://docs.ansible.com/projects/ansible/latest/reference_appendices/common_return_values.html#common-return-values>`_, the following are the fields unique to this module:

.. raw:: html

    <table border=0 cellpadding=0 class="documentation-table">
        <tr>
            <th colspan="1">Key</th>
            <th>Returned</th>
            <th width="100%">Description</th>
        </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>after</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                    </div>
                </td>
                <td>when changed</td>
                <td>
                            <div>The resulting configuration after module execution.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">[{&#x27;name&#x27;: &#x27;GigaEthernet2.1&#x27;, &#x27;dot1q&#x27;: {&#x27;vlan_id&#x27;: 10, &#x27;tpid&#x27;: &#x27;8100&#x27;}, &#x27;bridge_group&#x27;: {&#x27;group&#x27;: 1}}]</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>before</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                    </div>
                </td>
                <td>when <em>state</em> is <code>merged</code>, <code>replaced</code>, <code>overridden</code> or <code>deleted</code></td>
                <td>
                            <div>The configuration prior to the module execution.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">[{&#x27;name&#x27;: &#x27;GigaEthernet2.1&#x27;, &#x27;dot1q&#x27;: {&#x27;vlan_id&#x27;: 10, &#x27;tpid&#x27;: &#x27;8100&#x27;}}]</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>commands</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                    </div>
                </td>
                <td>when <em>state</em> is <code>merged</code>, <code>replaced</code>, <code>overridden</code> or <code>deleted</code></td>
                <td>
                            <div>The set of commands pushed to the remote device.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">[&#x27;interface GigaEthernet2.1&#x27;, &#x27;bridge-group 1&#x27;]</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>gathered</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                    </div>
                </td>
                <td>when <em>state</em> is <code>gathered</code></td>
                <td>
                            <div>Facts about the network resource gathered from the remote device as structured data.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">[{&#x27;name&#x27;: &#x27;GigaEthernet2.1&#x27;, &#x27;dot1q&#x27;: {&#x27;vlan_id&#x27;: 10, &#x27;tpid&#x27;: &#x27;8100&#x27;}}]</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>parsed</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                    </div>
                </td>
                <td>when <em>state</em> is <code>parsed</code></td>
                <td>
                            <div>The device native config provided in <em>running_config</em> option parsed into structured data as per module argspec.</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">[{&#x27;name&#x27;: &#x27;GigaEthernet0.1&#x27;, &#x27;bridge_group&#x27;: {&#x27;group&#x27;: 3}}]</div>
                </td>
            </tr>
            <tr>
                <td colspan="1">
                    <div class="ansibleOptionAnchor" id="return-"></div>
                    <b>rendered</b>
                    <a class="ansibleOptionLink" href="#return-" title="Permalink to this return value"></a>
                    <div style="font-size: small">
                      <span style="color: purple">list</span>
                    </div>
                </td>
                <td>when <em>state</em> is <code>rendered</code></td>
                <td>
                            <div>The provided configuration in the task rendered in device-native format (offline).</div>
                    <br/>
                        <div style="font-size: smaller"><b>Sample:</b></div>
                        <div style="font-size: smaller; color: blue; word-wrap: break-word; word-break: break-all;">[&#x27;interface GigaEthernet0.1&#x27;, &#x27;encapsulation dot1q 100 tpid 8100&#x27;]</div>
                </td>
            </tr>
    </table>
    <br/><br/>


Status
------


Authors
~~~~~~~

- Yushi Takeda(@Rucdev)
