# Ansible Collection - rucdev.ix

Documentation for the collection.

<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.13.5**.

For collections that support Ansible 2.9, please ensure you update your `network_os` to use the
fully qualified collection name (for example, `cisco.ios.ios`).
Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
<!--end requires_ansible-->

<!--start collection content-->
### Cliconf plugins
Name | Description
--- | ---
[rucdev.ix.ix](https://github.com/Rucdev/ix_ansible/blob/main/docs/rucdev.ix.ix_cliconf.rst)|Use ix cliconf to run command on NEC IX platform

### Modules
Name | Description
--- | ---
[rucdev.ix.ix_command](https://github.com/Rucdev/ix_ansible/blob/main/docs/rucdev.ix.ix_command_module.rst)|Run commands on remote NEC IX devices.
[rucdev.ix.ix_config](https://github.com/Rucdev/ix_ansible/blob/main/docs/rucdev.ix.ix_config_module.rst)|Manage configuration on device of NEC IX

<!--end collection content-->
