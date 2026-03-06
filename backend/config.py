"""
AIaaS Backend Configuration
Loads settings from YAML files with environment variable overrides.
"""
import json
import os
import secrets
import yaml
from pathlib import Path
from typing import Any
from pydantic import Field, field_validator

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ModuleNotFoundError:
    # Minimal compatibility fallback for environments where
    # `pydantic-settings` is not installed.
    from pydantic import BaseModel

    class BaseSettings(BaseModel):
        model_config = {"extra": "ignore"}

    def SettingsConfigDict(**kwargs):
        return kwargs


def load_yaml_config() -> dict:
    """Load YAML config with environment-specific overrides."""
    base_dir = Path(__file__).parent
    config = {}

    # Load default settings
    default_path = base_dir / "settings.yaml"
    if default_path.exists():
        with open(default_path, "r") as f:
            config = yaml.safe_load(f) or {}

    # Load environment-specific overrides
    env = os.getenv("APP_ENV", "local")
    env_path = base_dir / f"settings-{env}.yaml"
    if env_path.exists():
        with open(env_path, "r") as f:
            env_config = yaml.safe_load(f) or {}
            _deep_merge(config, env_config)

    return config


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base dict."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


_yaml_config = load_yaml_config()


def _normalize_origin(origin: str) -> str:
    """Normalize a single origin entry from env/config input."""
    return origin.strip().strip('"').strip("'")


def _parse_cors_origins(value: Any, fallback: list[str] | None = None) -> list[str]:
    """
    Parse CORS origins from list/JSON/csv forms.
    Accepts:
    - list[str]
    - JSON string: ["https://a.com","https://b.com"]
    - CSV string: https://a.com,https://b.com
    """
    if value is None:
        return list(fallback or [])

    if isinstance(value, list):
        return [origin for origin in (_normalize_origin(str(v)) for v in value) if origin]

    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return []

        # Handle accidental extra wrapping quotes from dashboard paste.
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
            raw = raw[1:-1].strip()

        if raw.startswith("[") and raw.endswith("]"):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [origin for origin in (_normalize_origin(str(v)) for v in parsed) if origin]
            except json.JSONDecodeError:
                pass

        return [origin for origin in (_normalize_origin(part) for part in raw.split(",")) if origin]

    raise ValueError("APP_CORS_ORIGINS must be a list or string")


class DatabaseSettings(BaseSettings):
    url: str = Field(
        default=os.getenv(
            "DATABASE_URL",
            _yaml_config.get("database", {}).get(
                "url", "postgresql://postgres:postgres@localhost:5432/aiaas"
            ),
        )
    )
    echo: bool = Field(
        default=_yaml_config.get("database", {}).get("echo", False)
    )


class RedisSettings(BaseSettings):
    url: str = Field(
        default=os.getenv(
            "REDIS_URL",
            _yaml_config.get("redis", {}).get(
                "url", "redis://localhost:6379/0"
            ),
        )
    )


class AuthSettings(BaseSettings):
    jwt_secret: str = Field(
        default=os.getenv(
            "JWT_SECRET",
            _yaml_config.get("auth", {}).get("jwt_secret", ""),
        )
    )
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiry_minutes: int = Field(
        default=_yaml_config.get("auth", {}).get("jwt_expiry_minutes", 60)
    )
    google_client_id: str = Field(
        default=os.getenv(
            "GOOGLE_CLIENT_ID",
            _yaml_config.get("auth", {}).get("google_client_id", ""),
        )
    )


class AIServiceSettings(BaseSettings):
    url: str = Field(
        default=_yaml_config.get("ai_service", {}).get(
            "url", "http://localhost:8001"
        )
    )
    api_key: str = Field(
        default=_yaml_config.get("ai_service", {}).get("api_key", "")
    )


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", extra="ignore")

    name: str = "AIaaS"
    version: str = "0.1.0"
    env: str = Field(default=os.getenv("APP_ENV", "local"))
    debug: bool = Field(
        default=_yaml_config.get("app", {}).get("debug", True)
    )
    demo_mode: bool = Field(
        default=os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")
    )
    cors_origins: list[str] = Field(
        default_factory=lambda: _parse_cors_origins(
            os.getenv("APP_CORS_ORIGINS"),
            _yaml_config.get("app", {}).get("cors_origins", ["http://localhost:3000"]),
        )
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def validate_cors_origins(cls, value: Any):
        return _parse_cors_origins(
            value,
            _yaml_config.get("app", {}).get("cors_origins", ["http://localhost:3000"]),
        )


class Settings:
    """Central settings object combining all sub-settings."""

    def __init__(self):
        self.app = AppSettings()
        self.database = DatabaseSettings()
        self.redis = RedisSettings()
        self.auth = AuthSettings()
        self.ai_service = AIServiceSettings()
        self._validate_security_defaults()

    def _validate_security_defaults(self):
        """Enforce safe auth secret behavior by environment."""
        if self.app.debug and not self.auth.jwt_secret:
            # Local/dev convenience only: ephemeral secret avoids hardcoded defaults.
            self.auth.jwt_secret = secrets.token_urlsafe(48)

        if (not self.app.debug) and (
            (not self.auth.jwt_secret) or len(self.auth.jwt_secret) < 32
        ):
            raise ValueError("JWT_SECRET must be set to a strong value (at least 32 chars) in non-debug environments.")


settings = Settings()
