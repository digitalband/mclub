import logging
from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent
ENV_FILE_PATH = BASE_DIR / "core" / ".env"


class DbSettings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    echo: bool = False

    @property
    def DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, env_file_encoding="utf-8", extra="allow"
    )


class RedisSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_USER: Optional[str] = None
    REDIS_PASS: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, env_file_encoding="utf-8", extra="allow"
    )

class AuthJWTSettings(BaseSettings):
    private_key_path: Path = BASE_DIR / "core" / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "core" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 3600
    verification_code_length: int = 6
    verification_code_expiration_minutes: int = 5  * 60

class EmailSettings(BaseSettings):
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str
    EMAIL_TEMPLATE_DIR: Path = BASE_DIR / "api_v1" / "email" / "templates"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, env_file_encoding="utf-8", extra="allow"
    )

class LoggingSettings(BaseSettings):
    logging_level: int = logging.INFO

    def configure_logging(self):
        logging.basicConfig(
            level=self.logging_level,
            datefmt="%Y-%m-%d %H:%M:%S",
            format="[%(asctime)s.%(msecs)03d] %(module)s:%(lineno)d %(levelname)s - %(message)s",
        )


class Settings(BaseSettings):
    MODE: str
    db: DbSettings = DbSettings()
    redis: RedisSettings = RedisSettings()
    email: EmailSettings = EmailSettings()
    auth_jwt: AuthJWTSettings = AuthJWTSettings()
    logging: LoggingSettings = LoggingSettings()

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="allow"
    )


settings = Settings()
