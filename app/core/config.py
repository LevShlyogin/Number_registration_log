from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    app_env: str = Field(default="dev", alias="APP_ENV")
    database_url: str = Field(alias="DATABASE_URL")
    default_ttl_seconds: int = Field(default=1800, alias="DEFAULT_TTL_SECONDS")
    admin_users: list[str] = ["vgrubtsov", "yuaalekseeva", "lrshlyogin", "pyagavrilov"]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()