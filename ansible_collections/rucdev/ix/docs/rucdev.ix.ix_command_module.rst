.. _rucdev.ix.ix_command_module:


********************
rucdev.ix.ix_command
********************

**Run commands on remote NEC IX devices.**


Version added: 0.1.0

.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Send arbitrary commands to an ix node and returns the results read from the device




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
                    <b>commands</b>
                    <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
                    <div style="font-size: small">
                        <span style="color: purple">list</span>
                         / <span style="color: purple">elements=raw</span>
                         / <span style="color: red">required</span>
                    </div>
                </td>
                <td>
                </td>
                <td>
                        <div></div>
                </td>
            </tr>
    </table>
    <br/>




Examples
--------

.. code-block:: yaml

    - name: Get show running config
      ix_config:
        commands: show running-config

    - name: Run multiple commands
      ix_command:
        commands:
          - show clock
          - show vlans




Status
------


Authors
~~~~~~~

- Yushi Takeda
