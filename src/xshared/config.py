from pydantic_settings import BaseSettings, SettingsConfigDict


class SharedSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- БД ---
    database_url: str = "postgresql+asyncpg://knhdb2:knhdb2@db.knh.cloud:443/knhdb2"
    db_ssl_enabled: bool = True
    db_ssl_ca_path: str | None = None

    # --- Пул соединений ---
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_echo: bool = False


settings = SharedSettings()
