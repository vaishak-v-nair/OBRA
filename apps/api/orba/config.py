from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://orba:orba_local@127.0.0.1:54329/orba"
    web_origin: str = "http://localhost:3000"
    session_cookie: str = "orba_session"
    cookie_secure: bool = False
    session_lifetime_seconds: int = Field(default=604800, ge=60, le=2592000)
    invitation_lifetime_seconds: int = Field(default=172800, ge=60, le=604800)
    login_max_attempts: int = Field(default=5, ge=1, le=100)
    login_window_seconds: int = Field(default=900, ge=60, le=86400)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def secure_origin(self):
        if self.web_origin.startswith("https://") and not self.cookie_secure:
            raise ValueError("HTTPS origins require COOKIE_SECURE=true")
        if not self.web_origin.startswith(("http://", "https://")) or self.web_origin.endswith("/"):
            raise ValueError("WEB_ORIGIN must be an exact HTTP(S) origin without trailing slash")
        return self
