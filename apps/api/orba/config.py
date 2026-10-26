import re
from pathlib import Path

from pydantic import AliasChoices, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from orba.pm_models_policy import ThinkingLevel, validate_model_configuration


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://orba:orba_local@127.0.0.1:54329/orba"
    web_origin: str = "http://localhost:3000"
    session_cookie: str = "orba_session"
    cookie_secure: bool = False
    session_lifetime_seconds: int = Field(default=604800, ge=60, le=2592000)
    invitation_lifetime_seconds: int = Field(default=172800, ge=60, le=604800)
    login_max_attempts: int = Field(default=5, ge=1, le=100)
    login_window_seconds: int = Field(default=900, ge=60, le=86400)
    scheduler_ack_seconds: int = Field(
        default=10, ge=2, le=60, validation_alias="ORBA_SCHEDULER_ACK_SECONDS"
    )
    scheduler_lease_seconds: int = Field(
        default=30, ge=5, le=120, validation_alias="ORBA_SCHEDULER_LEASE_SECONDS"
    )
    scheduler_max_lease_seconds: int = Field(
        default=120, ge=10, le=600, validation_alias="ORBA_SCHEDULER_MAX_LEASE_SECONDS"
    )
    scheduler_heartbeat_seconds: int = Field(
        default=10, ge=1, le=30, validation_alias="ORBA_SCHEDULER_HEARTBEAT_SECONDS"
    )
    scheduler_liveness_seconds: int = Field(
        default=60, ge=10, le=600, validation_alias="ORBA_SCHEDULER_LIVENESS_SECONDS"
    )
    scheduler_global_capacity: int = Field(
        default=8, ge=1, le=64, validation_alias="ORBA_SCHEDULER_GLOBAL_CAPACITY"
    )
    scheduler_run_capacity: int = Field(
        default=2, ge=1, le=16, validation_alias="ORBA_SCHEDULER_RUN_CAPACITY"
    )
    scheduler_max_attempts: int = Field(
        default=3, ge=1, le=5, validation_alias="ORBA_SCHEDULER_MAX_ATTEMPTS"
    )
    scheduler_batch_size: int = Field(
        default=8, ge=1, le=32, validation_alias="ORBA_SCHEDULER_BATCH_SIZE"
    )
    pm_api_key: SecretStr | None = Field(
        default=None, validation_alias=AliasChoices("ORBA_PM_API_KEY", "GEMINI_API_KEY")
    )
    pm_model: str | None = Field(default=None, max_length=160, validation_alias="ORBA_PM_MODEL")
    pm_timeout_seconds: int = Field(
        default=60, ge=5, le=180, validation_alias="ORBA_PM_TIMEOUT_SECONDS"
    )
    pm_max_output_tokens: int = Field(
        default=6000, ge=512, le=16000, validation_alias="ORBA_PM_MAX_OUTPUT_TOKENS"
    )
    pm_thinking_level: ThinkingLevel = Field(
        default="low", validation_alias="ORBA_PM_THINKING_LEVEL"
    )
    pm_max_input_bytes: int = Field(
        default=48000, ge=8192, le=96000, validation_alias="ORBA_PM_MAX_INPUT_BYTES"
    )
    pm_max_concurrent: int = Field(default=2, ge=1, le=4, validation_alias="ORBA_PM_MAX_CONCURRENT")
    pm_account_attempts: int = Field(
        default=5, ge=1, le=20, validation_alias="ORBA_PM_ACCOUNT_ATTEMPTS_PER_HOUR"
    )
    pm_global_attempts: int = Field(
        default=20, ge=1, le=100, validation_alias="ORBA_PM_GLOBAL_ATTEMPTS_PER_HOUR"
    )
    architect_api_key: SecretStr | None = Field(
        default=None, validation_alias="ORBA_ARCHITECT_API_KEY"
    )
    architect_model: str | None = Field(
        default=None, max_length=160, validation_alias="ORBA_ARCHITECT_MODEL"
    )
    architect_thinking_level: ThinkingLevel = Field(
        default="low", validation_alias="ORBA_ARCHITECT_THINKING_LEVEL"
    )
    architect_timeout_seconds: int = Field(
        default=90, ge=5, le=180, validation_alias="ORBA_ARCHITECT_TIMEOUT_SECONDS"
    )
    architect_max_output_tokens: int = Field(
        default=6000, ge=512, le=16000, validation_alias="ORBA_ARCHITECT_MAX_OUTPUT_TOKENS"
    )
    architect_max_input_bytes: int = Field(
        default=96000, ge=8192, le=96000, validation_alias="ORBA_ARCHITECT_MAX_INPUT_BYTES"
    )
    model_config = SettingsConfigDict(
        env_file=(
            Path(__file__).resolve().parents[3] / ".env",
            Path(__file__).resolve().parents[1] / ".env",
        ),
        extra="ignore",
        populate_by_name=True,
        hide_input_in_errors=True,
    )

    @field_validator("pm_model", "architect_model", mode="before")
    @classmethod
    def explicit_model(cls, value):
        value = value.strip() or None if isinstance(value, str) else value
        if value and not re.fullmatch(r"(?:models/)?gemini-[A-Za-z0-9._-]{1,140}", value):
            raise ValueError("ORBA_PM_MODEL must be an explicit Gemini model identifier")
        return value

    @field_validator("pm_thinking_level", "architect_thinking_level", mode="before")
    @classmethod
    def explicit_thinking(cls, value):
        return value.strip().lower() if isinstance(value, str) else value

    @model_validator(mode="after")
    def reviewed_pm_configuration(self):
        validate_model_configuration(self.pm_model, self.pm_thinking_level)
        validate_model_configuration(self.architect_model, self.architect_thinking_level)
        return self

    @property
    def pm_configured(self) -> bool:
        return bool(self.pm_api_key and self.pm_api_key.get_secret_value() and self.pm_model)

    def architect_settings(self):
        """Validated model policy, shared transport shape; never mutate PM selection."""
        key = self.architect_api_key
        if not key or not key.get_secret_value():
            key = self.pm_api_key
        return self.model_copy(
            update={
                "pm_api_key": key,
                "pm_model": self.architect_model,
                "pm_thinking_level": self.architect_thinking_level,
                "pm_timeout_seconds": self.architect_timeout_seconds,
                "pm_max_output_tokens": self.architect_max_output_tokens,
                "pm_max_input_bytes": self.architect_max_input_bytes,
            }
        )

    @model_validator(mode="after")
    def secure_origin(self):
        if self.web_origin.startswith("https://") and not self.cookie_secure:
            raise ValueError("HTTPS origins require COOKIE_SECURE=true")
        if not self.web_origin.startswith(("http://", "https://")) or self.web_origin.endswith("/"):
            raise ValueError("WEB_ORIGIN must be an exact HTTP(S) origin without trailing slash")
        return self

    def scheduler_policy(self):
        from orba.scheduler_schemas import SchedulerPolicy

        return SchedulerPolicy(
            acknowledge_seconds=self.scheduler_ack_seconds,
            lease_seconds=self.scheduler_lease_seconds,
            max_lease_seconds=self.scheduler_max_lease_seconds,
            heartbeat_seconds=self.scheduler_heartbeat_seconds,
            worker_liveness_seconds=self.scheduler_liveness_seconds,
            global_capacity=self.scheduler_global_capacity,
            run_capacity=self.scheduler_run_capacity,
            max_attempts=self.scheduler_max_attempts,
            batch_size=self.scheduler_batch_size,
        )
