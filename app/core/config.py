import logging
import secrets
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: Literal["development", "production"] = "development"
    DATABASE_URL: str = "sqlite:///./tasks.db"
    # Required in production; generated at start-up in development
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_V1_STR: str = "/api/v1"
    # Comma-separated list of allowed origins
    CORS_ORIGINS: str = "http://localhost:5173"
    DEMO_MODE: bool = False

    @model_validator(mode="after")
    def ensure_secret_key(self) -> "Settings":
        if not self.SECRET_KEY:
            if self.ENVIRONMENT == "production":
                raise ValueError("SECRET_KEY must be set when ENVIRONMENT=production")
            self.SECRET_KEY = secrets.token_urlsafe(32)
            logger.warning(
                "SECRET_KEY is not set; using a random key. "
                "Tokens will stop working when the server restarts."
            )
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
