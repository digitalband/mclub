import logging
from pathlib import Path

from pydantic import Field, BaseModel
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


class AuthJWTSettings(BaseSettings):
    private_key_path: Path = BASE_DIR / "core" / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "core" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 3600


class EmailSettings(BaseModel):
    EMAIL_TEMPLATE_DIR: str = BASE_DIR / "api_v1" / "email" / "temaplates"


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
    db: DbSettings = Field(default_factory=DbSettings)
    auth_jwt: AuthJWTSettings = Field(default_factory=AuthJWTSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    email: EmailSettings

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8"
    )


settings = Settings()
