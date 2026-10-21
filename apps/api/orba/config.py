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
    model_config = SettingsConfigDict(
        env_file=(
            Path(__file__).resolve().parents[3] / ".env",
            Path(__file__).resolve().parents[1] / ".env",
        ),
        extra="ignore",
        populate_by_name=True,
        hide_input_in_errors=True,
    )

    @field_validator("pm_model", mode="before")
    @classmethod
    def explicit_model(cls, value):
        value = value.strip() or None if isinstance(value, str) else value
        if value and not re.fullmatch(r"(?:models/)?gemini-[A-Za-z0-9._-]{1,140}", value):
            raise ValueError("ORBA_PM_MODEL must be an explicit Gemini model identifier")
        return value

    @field_validator("pm_thinking_level", mode="before")
    @classmethod
    def explicit_thinking(cls, value):
        return value.strip().lower() if isinstance(value, str) else value

    @model_validator(mode="after")
    def reviewed_pm_configuration(self):
        validate_model_configuration(self.pm_model, self.pm_thinking_level)
        return self

    @property
    def pm_configured(self) -> bool:
        return bool(self.pm_api_key and self.pm_api_key.get_secret_value() and self.pm_model)

    @model_validator(mode="after")
    def secure_origin(self):
        if self.web_origin.startswith("https://") and not self.cookie_secure:
            raise ValueError("HTTPS origins require COOKIE_SECURE=true")
        if not self.web_origin.startswith(("http://", "https://")) or self.web_origin.endswith("/"):
            raise ValueError("WEB_ORIGIN must be an exact HTTP(S) origin without trailing slash")
        return self
