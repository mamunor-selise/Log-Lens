import os
import unittest
from pathlib import Path
from app.core.services.log_service import LogService
from app.infrastructure.configuration.remote_ip_config import RemoteIPConfig, Environment

class TestRemoteIPIntegration(unittest.TestCase):
    def setUp(self):
        self.orig_env = os.environ.get("LOG_LENS_ENV")
        self.orig_ip = os.environ.get("LOG_REMOTE_IP")

    def tearDown(self):
        if self.orig_env is not None:
            os.environ["LOG_LENS_ENV"] = self.orig_env
        elif "LOG_LENS_ENV" in os.environ:
            del os.environ["LOG_LENS_ENV"]

        if self.orig_ip is not None:
            os.environ["LOG_REMOTE_IP"] = self.orig_ip
        elif "LOG_REMOTE_IP" in os.environ:
            del os.environ["LOG_REMOTE_IP"]

    def test_log_service_remote_ip_integration(self):
        os.environ["LOG_LENS_ENV"] = "staging"
        service = LogService()
        self.assertEqual(service.remote_ip_config.get_environment(), Environment.STAGING)
        
        unc_path = service.get_remote_unc_path("AKS-Stg-Logs/business-pcx/stg-business-pcx-win/PCXWebHost")
        self.assertEqual(unc_path, r"\\10.11.64.7\AKS-Stg-Logs/business-pcx/stg-business-pcx-win/PCXWebHost")

if __name__ == "__main__":
    unittest.main()
