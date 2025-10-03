from __future__ import absolute_import, division, print_function


__metaclass__ = type

import json

from os import path


try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from unittest import TestCase

from ansible.module_utils._text import to_bytes

from ansible_collections.rucdev.ix.plugins.cliconf import ix


b_FIXTURE_DIR = b"%s/fixtures/ix" % (
    to_bytes(path.dirname(path.abspath(__file__)), errors="surrogate_or_strict")
)


def _connection_side_effect(*args, **kwargs):
    try:
        if args:
            value = args[0]
        else:
            value = kwargs.get("command")

        fixture_path = path.abspath(
            b"%s/%s" % (b_FIXTURE_DIR, b"_".join(value.split(b" "))),
        )
        with open(fixture_path, "rb") as file_desc:
            return file_desc.read()
    except (OSError, IOError):
        if args:
            value = args[0]
            return value
        elif kwargs.get("command"):
            value = kwargs.get("command")
            return value

        return "Nope"


class TestPluginCLIConfIOS(TestCase):
    """Test class for IX CLI Conf Methods"""

    def setUp(self):
        self._mock_connection = MagicMock()
        self._mock_connection.send.side_effect = _connection_side_effect
        self._cliconf = ix.Cliconf(self._mock_connection)
        self.maxDiff = None

    def tearDown(self):
        pass

    def test_get_device_info(self):
        """Test get_device_info"""
        device_info = self._cliconf.get_device_info()

        mock_device_info = {
            "network_os": "ix",
            "network_os_model": "IX2105",
            "network_os_version": "10.2.39",
            "network_os_image": "ix2105-ms-10.2.39.ldc",
        }

        self.assertEqual(device_info, mock_device_info)

    def test_get_capabilities(self):
        """Test get_capabilities"""
        capabilities = json.loads(self._cliconf.get_capabilities())
        mock_capabilities = {
            "device_info": {
                "network_os": "ix",
                "network_os_model": "IX2105",
                "network_os_version": "10.2.39",
                "network_os_hostname": "ix-dev",
                "network_os_image": "bootflash:packages.conf",
            },
            "device_operations": {
                "supports_commit": False,
                "supports_commit_comment": False,
                "supports_defaults": True,
                "supports_diff_ignore_lines": True,
                "supports_diff_match": True,
                "supports_diff_replace": True,
                "supports_generate_diff": True,
                "supports_multiline_delimiter": True,
                "supports_onbox_diff": False,
                "supports_replace": False,
                "supports_rollback": False,
            },
            "diff_match": ["line", "strict", "exact", "none"],
            "diff_replace": ["line", "block"],
            "format": ["text"],
            "network_api": "cliconf",
            "output": [],
            "rpc": [
                "edit_config",
                "enable_response_logging",
                "get",
                "get_capabilities",
                "get_config",
                "disable_response_logging",
                "run_commands",
                "edit_banner",
                "get_diff",
                "run_commands",
                "get_defaults_flag",
            ],
        }
        self.assertEqual(sorted(mock_capabilities), sorted(capabilities))
