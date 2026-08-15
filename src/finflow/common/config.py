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
    rejected_path: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="STORAGE_",
        case_sensitive=False,
        extra="ignore",
    )

class LoggingSettings(BaseSettings):
    log_level: str = Field(validation_alias="LOG_LEVEL")
    log_format: str = Field(validation_alias="LOG_FORMAT")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

class FinFlowSettings(BaseSettings):
    database: DatabaseSettings
    pipeline: PipelineSettings
    storage: StorageSettings
    logging: LoggingSettings

settings = FinFlowSettings(
    database=DatabaseSettings(),
    pipeline=PipelineSettings(),
    storage=StorageSettings(),
    logging=LoggingSettings(),
)

from pydantic import BaseModel


class FinFlowSettings(BaseModel):
    database: DatabaseSettings
    pipeline: PipelineSettings
    storage: StorageSettings
    logging: LoggingSettings


settings = FinFlowSettings(
    database=DatabaseSettings(),
    pipeline=PipelineSettings(),
    storage=StorageSettings(),
    logging=LoggingSettings(),
)