import os
import json
import tempfile
import unittest
from pathlib import Path
from app.infrastructure.configuration.remote_ip_config import RemoteIPConfig, Environment

class TestRemoteIPConfig(unittest.TestCase):
    def setUp(self):
        # Save original env vars
        self.orig_env = os.environ.get("LOG_LENS_ENV")
        self.orig_ip = os.environ.get("LOG_REMOTE_IP")
        if "LOG_LENS_ENV" in os.environ:
            del os.environ["LOG_LENS_ENV"]
        if "LOG_REMOTE_IP" in os.environ:
            del os.environ["LOG_REMOTE_IP"]

    def tearDown(self):
        # Restore env vars
        if self.orig_env is not None:
            os.environ["LOG_LENS_ENV"] = self.orig_env
        elif "LOG_LENS_ENV" in os.environ:
            del os.environ["LOG_LENS_ENV"]

        if self.orig_ip is not None:
            os.environ["LOG_REMOTE_IP"] = self.orig_ip
        elif "LOG_REMOTE_IP" in os.environ:
            del os.environ["LOG_REMOTE_IP"]

    def test_default_environment_and_ip_resolution(self):
        config = RemoteIPConfig()
        self.assertEqual(config.get_environment(), Environment.DEVELOPMENT)
        self.assertEqual(config.get_remote_ip(), "10.11.64.7")

    def test_environment_variable_detection(self):
        os.environ["LOG_LENS_ENV"] = "staging"
        config = RemoteIPConfig()
        self.assertEqual(config.get_environment(), Environment.STAGING)
        self.assertEqual(config.get_remote_ip(), "10.11.64.7")

        os.environ["LOG_LENS_ENV"] = "production"
        config_prod = RemoteIPConfig()
        self.assertEqual(config_prod.get_environment(), Environment.PRODUCTION)
        self.assertEqual(config_prod.get_remote_ip(), "10.11.64.8")

    def test_explicit_ip_override_via_env(self):
        os.environ["LOG_REMOTE_IP"] = "192.168.1.100"
        config = RemoteIPConfig()
        self.assertEqual(config.get_remote_ip(), "192.168.1.100")

    def test_custom_json_config_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "remote_ips.json"
            config_file.write_text(json.dumps({
                "development": "10.0.0.1",
                "staging": "10.0.0.2",
                "production": "10.0.0.3"
            }), encoding="utf-8")

            os.environ["LOG_LENS_ENV"] = "production"
            config = RemoteIPConfig(config_file_path=config_file)
            self.assertEqual(config.get_remote_ip(), "10.0.0.3")

    def test_unc_path_formatting(self):
        os.environ["LOG_LENS_ENV"] = "staging"
        config = RemoteIPConfig()
        unc_path = config.get_share_unc_path("AKS-Stg-Logs")
        self.assertEqual(unc_path, r"\\10.11.64.7\AKS-Stg-Logs")

if __name__ == "__main__":
    unittest.main()
