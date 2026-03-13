"""
VidyaOS Backend Configuration
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


def _parse_csv_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return []
        return [part.strip() for part in raw.split(",") if part.strip()]
    return []


class DatabaseSettings(BaseSettings):
    url: str = Field(
        default=os.getenv(
            "DATABASE_URL",
            _yaml_config.get("database", {}).get(
                "url", "postgresql://postgres:postgres@localhost:5432/vidyaos"
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
    saml_sp_base_url: str = Field(
        default=os.getenv(
            "SAML_SP_BASE_URL",
            _yaml_config.get("auth", {}).get("saml_sp_base_url", "http://localhost:8000"),
        )
    )
    saml_strict: bool = Field(
        default=os.getenv("SAML_STRICT", "true").lower() in ("true", "1", "yes")
    )
    saml_debug: bool = Field(
        default=os.getenv("SAML_DEBUG", "false").lower() in ("true", "1", "yes")
    )


class AIServiceSettings(BaseSettings):
    url: str = Field(
        default=os.getenv(
            "AI_SERVICE_URL",
            _yaml_config.get("ai_service", {}).get(
                "url", "http://localhost:8001"
            ),
        )
    )
    urls: list[str] = Field(
        default_factory=lambda: _parse_csv_list(
            os.getenv("AI_SERVICE_URLS") or _yaml_config.get("ai_service", {}).get("urls", [])
        )
    )
    api_key: str = Field(
        default=os.getenv(
            "AI_SERVICE_KEY",
            _yaml_config.get("ai_service", {}).get("api_key", ""),
        )
    )
    timeout_seconds: int = Field(
        default=int(_yaml_config.get("ai_service", {}).get("timeout_seconds", 90))
    )

    def resolved_urls(self) -> list[str]:
        urls = [url for url in self.urls if url]
        if not urls and self.url:
            urls = [self.url]
        return urls


class AIQueueSettings(BaseSettings):
    enabled: bool = Field(
        default=os.getenv("AI_QUEUE_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    pending_key: str = Field(
        default=os.getenv(
            "AI_QUEUE_PENDING_KEY",
            _yaml_config.get("ai_queue", {}).get("pending_key", "ai_jobs:pending"),
        )
    )
    processing_key: str = Field(
        default=os.getenv(
            "AI_QUEUE_PROCESSING_KEY",
            _yaml_config.get("ai_queue", {}).get("processing_key", "ai_jobs:processing"),
        )
    )
    result_ttl_seconds: int = Field(
        default=int(
            os.getenv(
                "AI_QUEUE_RESULT_TTL_SECONDS",
                _yaml_config.get("ai_queue", {}).get("result_ttl_seconds", 86400),
            )
        )
    )
    max_retries: int = Field(
        default=int(
            os.getenv(
                "AI_QUEUE_MAX_RETRIES",
                _yaml_config.get("ai_queue", {}).get("max_retries", 2),
            )
        )
    )
    poll_timeout_seconds: int = Field(
        default=int(
            os.getenv(
                "AI_QUEUE_POLL_TIMEOUT_SECONDS",
                _yaml_config.get("ai_queue", {}).get("poll_timeout_seconds", 5),
            )
        )
    )
    stuck_after_seconds: int = Field(
        default=int(
            os.getenv(
                "AI_QUEUE_STUCK_AFTER_SECONDS",
                _yaml_config.get("ai_queue", {}).get("stuck_after_seconds", 300),
            )
        )
    )
    metrics_window_seconds: int = Field(
        default=int(
            os.getenv(
                "AI_QUEUE_METRICS_WINDOW_SECONDS",
                _yaml_config.get("ai_queue", {}).get("metrics_window_seconds", 3600),
            )
        )
    )
    max_pending_jobs: int = Field(
        default=int(
            os.getenv(
                "AI_QUEUE_MAX_PENDING_JOBS",
                _yaml_config.get("ai_queue", {}).get("max_pending_jobs", 1000),
            )
        )
    )
    max_pending_jobs_per_tenant: int = Field(
        default=int(
            os.getenv(
                "AI_QUEUE_MAX_PENDING_JOBS_PER_TENANT",
                _yaml_config.get("ai_queue", {}).get("max_pending_jobs_per_tenant", 200),
            )
        )
    )


class StartupCheckSettings(BaseSettings):
    enabled: bool = Field(
        default=os.getenv(
            "STARTUP_CHECKS_ENABLED",
            str(_yaml_config.get("startup_checks", {}).get("enabled", True)),
        ).lower() in ("true", "1", "yes")
    )
    strict: bool = Field(
        default=os.getenv(
            "STARTUP_CHECKS_STRICT",
            str(_yaml_config.get("startup_checks", {}).get("strict", False)),
        ).lower() in ("true", "1", "yes")
    )
    timeout_seconds: int = Field(
        default=int(
            os.getenv(
                "STARTUP_CHECKS_TIMEOUT_SECONDS",
                _yaml_config.get("startup_checks", {}).get("timeout_seconds", 5),
            )
        )
    )


class WorkerHealthSettings(BaseSettings):
    enabled: bool = Field(
        default=os.getenv(
            "WORKER_HEALTH_ENABLED",
            str(_yaml_config.get("worker_health", {}).get("enabled", True)),
        ).lower() in ("true", "1", "yes")
    )
    host: str = Field(
        default=os.getenv(
            "WORKER_HEALTH_HOST",
            _yaml_config.get("worker_health", {}).get("host", "0.0.0.0"),
        )
    )
    port: int = Field(
        default=int(
            os.getenv(
                "WORKER_HEALTH_PORT",
                _yaml_config.get("worker_health", {}).get("port", 8010),
            )
        )
    )
    heartbeat_stale_seconds: int = Field(
        default=int(
            os.getenv(
                "WORKER_HEALTH_HEARTBEAT_STALE_SECONDS",
                _yaml_config.get("worker_health", {}).get("heartbeat_stale_seconds", 60),
            )
        )
    )


class LLMSettings(BaseSettings):
    url: str = Field(
        default=os.getenv(
            "OLLAMA_URL",
            _yaml_config.get("llm", {}).get("url", "http://localhost:11434"),
        )
    )
    model: str = Field(
        default=os.getenv(
            "OLLAMA_MODEL",
            _yaml_config.get("llm", {}).get("model", "llama3.2"),
        )
    )
    fallback_model: str = Field(
        default=os.getenv(
            "OLLAMA_FALLBACK_MODEL",
            _yaml_config.get("llm", {}).get("fallback_model", "llama3.2"),
        )
    )
    temperature: float = Field(
        default=float(_yaml_config.get("llm", {}).get("temperature", 0.1))
    )
    max_new_tokens: int = Field(
        default=int(_yaml_config.get("llm", {}).get("max_new_tokens", 800))
    )
    timeout_seconds: int = Field(
        default=int(_yaml_config.get("llm", {}).get("timeout_seconds", 60))
    )


class EmbeddingSettings(BaseSettings):
    url: str = Field(
        default=os.getenv(
            "OLLAMA_URL",
            _yaml_config.get("embedding", {}).get(
                "url",
                _yaml_config.get("llm", {}).get("url", "http://localhost:11434"),
            ),
        )
    )
    model: str = Field(
        default=os.getenv(
            "EMBED_MODEL",
            _yaml_config.get("embedding", {}).get("model", "nomic-embed-text"),
        )
    )
    embed_dim: int = Field(
        default=int(_yaml_config.get("embedding", {}).get("embed_dim", 768))
    )


class StorageSettings(BaseSettings):
    project_root: Path = Field(default=Path(__file__).resolve().parents[1])
    root: Path = Field(
        default=Path(
            os.getenv(
                "VidyaOS_STORAGE_ROOT",
                str(Path(__file__).resolve().parents[1]),
            )
        )
    )
    vector_store_dir: Path = Field(
        default=Path(
            os.getenv(
                "VidyaOS_VECTOR_STORE_DIR",
                str(Path(__file__).resolve().parents[1] / "vector_store"),
            )
        )
    )
    compliance_export_dir: Path = Field(
        default=Path(
            os.getenv(
                "VidyaOS_COMPLIANCE_EXPORT_DIR",
                str(Path(__file__).resolve().parents[1] / "compliance_exports"),
            )
        )
    )


class VectorBackendSettings(BaseSettings):
    provider: str = Field(
        default=os.getenv(
            "VECTOR_BACKEND_PROVIDER",
            _yaml_config.get("vector_backend", {}).get("provider", "faiss"),
        )
    )
    qdrant_url: str = Field(
        default=os.getenv(
            "QDRANT_URL",
            _yaml_config.get("vector_backend", {}).get("qdrant_url", "http://localhost:6333"),
        )
    )
    qdrant_api_key: str = Field(
        default=os.getenv(
            "QDRANT_API_KEY",
            _yaml_config.get("vector_backend", {}).get("qdrant_api_key", ""),
        )
    )
    collection_prefix: str = Field(
        default=os.getenv(
            "VECTOR_COLLECTION_PREFIX",
            _yaml_config.get("vector_backend", {}).get("collection_prefix", "tenant_"),
        )
    )
    timeout_seconds: int = Field(
        default=int(
            os.getenv(
                "VECTOR_BACKEND_TIMEOUT_SECONDS",
                _yaml_config.get("vector_backend", {}).get("timeout_seconds", 20),
            )
        )
    )


class ComplianceSettings(BaseSettings):
    export_retention_days: int = Field(
        default=int(
            os.getenv(
                "COMPLIANCE_EXPORT_RETENTION_DAYS",
                _yaml_config.get("compliance", {}).get("export_retention_days", 30),
            )
        )
    )
    default_data_retention_days: int = Field(
        default=int(
            os.getenv(
                "COMPLIANCE_DATA_RETENTION_DAYS",
                _yaml_config.get("compliance", {}).get("default_data_retention_days", 365),
            )
        )
    )


class EmailSettings(BaseSettings):
    enabled: bool = Field(
        default=os.getenv(
            "EMAIL_ENABLED",
            str(_yaml_config.get("email", {}).get("enabled", False)),
        ).lower() in ("true", "1", "yes")
    )
    host: str = Field(
        default=os.getenv(
            "SMTP_HOST",
            _yaml_config.get("email", {}).get("host", ""),
        )
    )
    port: int = Field(
        default=int(
            os.getenv(
                "SMTP_PORT",
                _yaml_config.get("email", {}).get("port", 587),
            )
        )
    )
    username: str = Field(
        default=os.getenv(
            "SMTP_USERNAME",
            _yaml_config.get("email", {}).get("username", ""),
        )
    )
    password: str = Field(
        default=os.getenv(
            "SMTP_PASSWORD",
            _yaml_config.get("email", {}).get("password", ""),
        )
    )
    use_tls: bool = Field(
        default=os.getenv(
            "SMTP_USE_TLS",
            str(_yaml_config.get("email", {}).get("use_tls", True)),
        ).lower() in ("true", "1", "yes")
    )
    from_email: str = Field(
        default=os.getenv(
            "SMTP_FROM_EMAIL",
            _yaml_config.get("email", {}).get("from_email", "no-reply@vidyaos.local"),
        )
    )
    from_name: str = Field(
        default=os.getenv(
            "SMTP_FROM_NAME",
            _yaml_config.get("email", {}).get("from_name", "VidyaOS"),
        )
    )


class DigestEmailSettings(BaseSettings):
    enabled: bool = Field(
        default=os.getenv(
            "DIGEST_EMAIL_ENABLED",
            str(_yaml_config.get("digest_email", {}).get("enabled", False)),
        ).lower() in ("true", "1", "yes")
    )
    interval_minutes: int = Field(
        default=int(
            os.getenv(
                "DIGEST_EMAIL_INTERVAL_MINUTES",
                _yaml_config.get("digest_email", {}).get("interval_minutes", 10080),
            )
        )
    )


class SmsSettings(BaseSettings):
    enabled: bool = Field(
        default=os.getenv(
            "SMS_ENABLED",
            str(_yaml_config.get("sms", {}).get("enabled", False)),
        ).lower() in ("true", "1", "yes")
    )
    provider: str = Field(
        default=os.getenv(
            "SMS_PROVIDER",
            _yaml_config.get("sms", {}).get("provider", "twilio"),
        )
    )
    account_sid: str = Field(
        default=os.getenv(
            "SMS_ACCOUNT_SID",
            _yaml_config.get("sms", {}).get("account_sid", ""),
        )
    )
    auth_token: str = Field(
        default=os.getenv(
            "SMS_AUTH_TOKEN",
            _yaml_config.get("sms", {}).get("auth_token", ""),
        )
    )
    from_number: str = Field(
        default=os.getenv(
            "SMS_FROM_NUMBER",
            _yaml_config.get("sms", {}).get("from_number", ""),
        )
    )


class DocWatchSettings(BaseSettings):
    enabled: bool = Field(
        default=os.getenv(
            "DOC_WATCH_ENABLED",
            str(_yaml_config.get("doc_watch", {}).get("enabled", False)),
        ).lower() in ("true", "1", "yes")
    )
    dirs: list[str] = Field(
        default_factory=lambda: _parse_csv_list(
            os.getenv("DOC_WATCH_DIRS") or _yaml_config.get("doc_watch", {}).get("dirs", [])
        )
    )
    poll_interval_seconds: int = Field(
        default=int(
            os.getenv(
                "DOC_WATCH_INTERVAL",
                _yaml_config.get("doc_watch", {}).get("poll_interval_seconds", 30),
            )
        )
    )
    tenant_id: str = Field(
        default=os.getenv(
            "DOC_WATCH_TENANT_ID",
            _yaml_config.get("doc_watch", {}).get("tenant_id", ""),
        )
    )
    uploader_id: str = Field(
        default=os.getenv(
            "DOC_WATCH_UPLOADER_ID",
            _yaml_config.get("doc_watch", {}).get("uploader_id", ""),
        )
    )


class IncidentSettings(BaseSettings):
    auto_create_from_alerts: bool = Field(
        default=os.getenv("INCIDENT_AUTO_CREATE_FROM_ALERTS", "true").lower() in ("true", "1", "yes")
    )
    default_escalation_minutes: int = Field(
        default=int(
            os.getenv(
                "INCIDENT_DEFAULT_ESCALATION_MINUTES",
                _yaml_config.get("incidents", {}).get("default_escalation_minutes", 30),
            )
        )
    )


class ObservabilitySettings(BaseSettings):
    enabled: bool = Field(
        default=os.getenv("OBSERVABILITY_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    service_name: str = Field(
        default=os.getenv(
            "OBSERVABILITY_SERVICE_NAME",
            _yaml_config.get("observability", {}).get("service_name", "vidyaos-api"),
        )
    )
    log_level: str = Field(
        default=os.getenv(
            "OBSERVABILITY_LOG_LEVEL",
            _yaml_config.get("observability", {}).get("log_level", "INFO"),
        )
    )
    log_path: str = Field(
        default=os.getenv(
            "OBSERVABILITY_LOG_PATH",
            _yaml_config.get("observability", {}).get("log_path", ""),
        )
    )
    metrics_enabled: bool = Field(
        default=os.getenv("OBSERVABILITY_METRICS_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    metrics_token: str = Field(
        default=os.getenv(
            "OBSERVABILITY_METRICS_TOKEN",
            _yaml_config.get("observability", {}).get("metrics_token", ""),
        )
    )
    alerting_enabled: bool = Field(
        default=os.getenv("OBSERVABILITY_ALERTING_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    queue_depth_warn_threshold_pct: int = Field(
        default=int(
            os.getenv(
                "OBSERVABILITY_QUEUE_DEPTH_WARN_THRESHOLD_PCT",
                _yaml_config.get("observability", {}).get("queue_depth_warn_threshold_pct", 80),
            )
        )
    )
    queue_failure_warn_pct: int = Field(
        default=int(
            os.getenv(
                "OBSERVABILITY_QUEUE_FAILURE_WARN_PCT",
                _yaml_config.get("observability", {}).get("queue_failure_warn_pct", 20),
            )
        )
    )
    alert_email_recipients: list[str] = Field(
        default_factory=lambda: _parse_csv_list(
            os.getenv("OBSERVABILITY_ALERT_EMAILS")
            or _yaml_config.get("observability", {}).get("alert_email_recipients", [])
        )
    )
    alert_sms_recipients: list[str] = Field(
        default_factory=lambda: _parse_csv_list(
            os.getenv("OBSERVABILITY_ALERT_SMS")
            or _yaml_config.get("observability", {}).get("alert_sms_recipients", [])
        )
    )
    tracing_enabled: bool = Field(
        default=os.getenv("OBSERVABILITY_TRACING_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    otlp_endpoint: str = Field(
        default=os.getenv(
            "OBSERVABILITY_OTLP_ENDPOINT",
            _yaml_config.get("observability", {}).get("otlp_endpoint", ""),
        )
    )
    otlp_insecure: bool = Field(
        default=os.getenv("OBSERVABILITY_OTLP_INSECURE", "true").lower() in ("true", "1", "yes")
    )
    trace_sample_ratio: float = Field(
        default=float(
            os.getenv(
                "OBSERVABILITY_TRACE_SAMPLE_RATIO",
                _yaml_config.get("observability", {}).get("trace_sample_ratio", 1.0),
            )
        )
    )


class SentrySettings(BaseSettings):
    enabled: bool = Field(
        default=os.getenv(
            "SENTRY_ENABLED",
            str(_yaml_config.get("sentry", {}).get("enabled", False)),
        ).lower() in ("true", "1", "yes")
    )
    dsn: str = Field(
        default=os.getenv(
            "SENTRY_DSN",
            _yaml_config.get("sentry", {}).get("dsn", ""),
        )
    )
    environment: str = Field(
        default=os.getenv(
            "SENTRY_ENVIRONMENT",
            _yaml_config.get("sentry", {}).get("environment", ""),
        )
    )
    traces_sample_rate: float = Field(
        default=float(
            os.getenv(
                "SENTRY_TRACES_SAMPLE_RATE",
                _yaml_config.get("sentry", {}).get("traces_sample_rate", 0.05),
            )
        )
    )
    profiles_sample_rate: float = Field(
        default=float(
            os.getenv(
                "SENTRY_PROFILES_SAMPLE_RATE",
                _yaml_config.get("sentry", {}).get("profiles_sample_rate", 0.0),
            )
        )
    )
    send_default_pii: bool = Field(
        default=os.getenv(
            "SENTRY_SEND_PII",
            str(_yaml_config.get("sentry", {}).get("send_default_pii", False)),
        ).lower() in ("true", "1", "yes")
    )


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", extra="ignore")

    name: str = "VidyaOS"
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
        self.ai_queue = AIQueueSettings()
        self.startup_checks = StartupCheckSettings()
        self.worker_health = WorkerHealthSettings()
        self.llm = LLMSettings()
        self.embedding = EmbeddingSettings()
        self.storage = StorageSettings()
        self.vector_backend = VectorBackendSettings()
        self.compliance = ComplianceSettings()
        self.email = EmailSettings()
        self.digest_email = DigestEmailSettings()
        self.sms = SmsSettings()
        self.doc_watch = DocWatchSettings()
        self.incidents = IncidentSettings()
        self.observability = ObservabilitySettings()
        self.sentry = SentrySettings()
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
