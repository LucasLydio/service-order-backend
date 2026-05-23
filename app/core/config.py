from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic import model_validator
from urllib.parse import quote_plus


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str | None = None
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "service_order"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    JWT_SECRET_KEY: str = "test-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    ENVIRONMENT: str = "development"

    @model_validator(mode="after")
    def build_database_url(self):
        if not self.DATABASE_URL:
            password = quote_plus(self.MYSQL_PASSWORD)
            self.DATABASE_URL = (
                f"mysql+pymysql://{self.MYSQL_USER}:{password}@"
                f"{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            )
        return self


@lru_cache()
def get_settings():
    return Settings()
