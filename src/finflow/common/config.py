from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    host: str
    port: int
    database: str = Field(validation_alias="DB_NAME")
    user: str
    password: str
    database_schema: str = Field(validation_alias="DB_SCHEMA")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DB_",
        case_sensitive=False,   
    )


db_settings = DatabaseSettings()