from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASS: str = "postgres"
    DB_NAME: str = "fastapi-task"
    DATABASE_URL: str | None = None

    SECRET_KEY: str = "mysecretpassword123456789"
    ALGORITHM: str = "HS256"



    @model_validator(mode="after")
    def assemble_db_connection(self):
        if self.DATABASE_URL is None:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        return self  # ← Возвращаем self, а не строку!

settings = Settings()
    