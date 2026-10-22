from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://knhdb2:knhdb2@db.knh.cloud:443/knhdb2"
    db_ssl_enabled: bool = True


settings = Settings()
