from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import date


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
        extra="ignore",
    )


class PipelineSettings(BaseSettings):
    batch_date: date
    batch_size: int
    max_retries: int
    retry_delay: int
    source_system: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="PIPELINE_",
        case_sensitive=False,
        extra="ignore",
    )

class StorageSettings(BaseSettings):
    bucket_name: str
    raw_path: str
    staging_path: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="STORAGE_",
        case_sensitive=False,
        extra="ignore",
    )

db_settings = DatabaseSettings()
pipeline_settings = PipelineSettings()
storage_settings = StorageSettings()