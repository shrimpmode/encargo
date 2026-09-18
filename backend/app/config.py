from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./waitlist.db"
    debug: bool = False
    # The frontend's dev server origin — only consumer of this API locally.
    allowed_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
