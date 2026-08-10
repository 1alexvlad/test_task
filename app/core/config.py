from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    DB_HOST: str 
    DB_PORT: int 
    DB_USER: str 
    DB_PASS: str 
    DB_NAME: str 
    DATABASE_URL: str | None

    SECRET_KEY: str 
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    REFRESH_TOKEN_EXPIRE_DAYS: int 



    @model_validator(mode="after")
    def assemble_db_connection(self):
        if self.DATABASE_URL is None:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        return self  
    
settings = Settings()
    