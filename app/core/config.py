"""Application configuration."""

from pydantic import BaseModel
import os


class DatabaseConfig(BaseModel):
    dsn: str = "sqlite:///data/postcodes.db"


class Config:
    # :DatabaseConfig: String to database location
    database: DatabaseConfig = DatabaseConfig()
    # :str: Secrect key
    token_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "MYAPI_"


config = Config()
