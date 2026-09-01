import os
import json
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Union

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

    @classmethod
    def normalize(cls, env_str: Optional[str]) -> "Environment":
        if not env_str:
            return cls.DEVELOPMENT
        clean = env_str.strip().lower()
        if clean in ("dev", "development"):
            return cls.DEVELOPMENT
        elif clean in ("stg", "stage", "staging"):
            return cls.STAGING
        elif clean in ("prod", "production"):
            return cls.PRODUCTION
        return cls.DEVELOPMENT

class RemoteIPConfig:
    """Configures remote log server IP addresses dynamically per deployment environment."""

    DEFAULT_MAPPINGS: Dict[Environment, str] = {
        Environment.DEVELOPMENT: "10.11.64.7",
        Environment.STAGING: "10.11.64.7",
        Environment.PRODUCTION: "10.11.64.8",
    }

    def __init__(self, config_file_path: Optional[Union[str, Path]] = None):
        self._environment = self._resolve_environment()
        self._custom_mappings: Dict[str, str] = {}
        if config_file_path:
            self._load_config_file(Path(config_file_path))
        else:
            appdata_config = Path(os.environ.get("APPDATA", "")) / "Log-Lens" / "remote_ips.json"
            if appdata_config.exists():
                self._load_config_file(appdata_config)

    def _resolve_environment(self) -> Environment:
        env_var = (
            os.environ.get("LOG_LENS_ENV")
            or os.environ.get("APP_ENV")
            or os.environ.get("ENVIRONMENT")
        )
        return Environment.normalize(env_var)

    def _load_config_file(self, path: Path) -> None:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self._custom_mappings = {k.lower(): str(v) for k, v in data.items()}
            except Exception:
                pass

    def get_environment(self) -> Environment:
        return self._environment

    def get_remote_ip(self) -> str:
        # Explicit env override takes highest precedence
        override_ip = os.environ.get("LOG_REMOTE_IP")
        if override_ip:
            return override_ip.strip()

        env_key = self._environment.value
        if env_key in self._custom_mappings:
            return self._custom_mappings[env_key]

        return self.DEFAULT_MAPPINGS.get(self._environment, "10.11.64.7")

    def get_share_unc_path(self, share_name: str) -> str:
        ip = self.get_remote_ip()
        clean_share = share_name.lstrip("\\/")
        return f"\\\\{ip}\\{clean_share}"
