from pydantic_settings import BaseSettings, SettingsConfigDict


class SharedSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- DB ---
    database_url: str
    db_ssl_enabled: bool

    # --- Connections pool ---
    db_pool_size: int
    db_max_overflow: int
    db_echo: bool

    # --- Dadata creds ---
    dd_token: str
    dd_secret: str


settings = SharedSettings()
