from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DATABASE_URL: str | None = None

    SECRET_KEY: str
    ALGORITHM: str


    @model_validator(mode="after")
    def get_database_url(self):
        self.DATABASE_URL = (
            f"postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi-task"
        )
        return self

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    
settings = Settings()
    