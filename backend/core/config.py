import os
from typing import Literal, List, Any
from pydantic import Field, model_validator, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/aarogya",
        validation_alias="DATABASE_URL"
    )
    sync_url: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/aarogya",
        validation_alias="SYNC_DATABASE_URL"
    )
    pool_size: int = Field(default=10, validation_alias="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, validation_alias="DB_MAX_OVERFLOW")
    echo: bool = Field(default=False, validation_alias="DB_ECHO_SQL")

class LoggingSettings(BaseSettings):
    level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    format_type: Literal["CONSOLE", "JSON"] = Field(default="CONSOLE", validation_alias="LOG_FORMAT")

class SecuritySettings(BaseSettings):
    allowed_hosts: List[str] = Field(default=["*"])
    allowed_origins: List[str] = Field(default=["*"])
    max_request_size: int = Field(default=10485760, validation_alias="MAX_REQUEST_SIZE")  # 10MB default

    @model_validator(mode="before")
    @classmethod
    def parse_lists(cls, data: dict[str, Any]) -> dict[str, Any]:
        if isinstance(data.get("allowed_hosts"), str):
            data["allowed_hosts"] = [host.strip() for host in data["allowed_hosts"].split(",")]
        if isinstance(data.get("allowed_origins"), str):
            data["allowed_origins"] = [origin.strip() for origin in data["allowed_origins"].split(",")]
        return data

class AIWorkflowSettings(BaseSettings):
    confidence_high: float = Field(default=0.85, validation_alias="CONFIDENCE_HIGH")
    confidence_medium: float = Field(default=0.70, validation_alias="CONFIDENCE_MEDIUM")
    confidence_low: float = Field(default=0.50, validation_alias="CONFIDENCE_LOW")
    max_followups: int = Field(default=3, validation_alias="MAX_FOLLOWUPS")

    # Weighted confidence aggregation
    weight_symptom: float = Field(default=0.30, validation_alias="WEIGHT_SYMPTOM")
    weight_risk: float = Field(default=0.20, validation_alias="WEIGHT_RISK")
    weight_retrieval: float = Field(default=0.25, validation_alias="WEIGHT_RETRIEVAL")
    weight_diagnosis: float = Field(default=0.25, validation_alias="WEIGHT_DIAGNOSIS")

    # RAG settings
    rag_top_k: int = Field(default=5, validation_alias="RAG_TOP_K")
    chroma_persist_dir: str = Field(default="./chroma_db", validation_alias="CHROMA_PERSIST_DIR")

    # Thresholds / Triggers
    diagnosis_followup_threshold: float = Field(default=0.70, validation_alias="DIAGNOSIS_FOLLOWUP_THRESHOLD")
    emergency_urgency_trigger: str = Field(default="emergency", validation_alias="EMERGENCY_URGENCY_TRIGGER")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_DEBUG: bool = True
    APP_TITLE: str = "AarogyaAgent API"
    APP_VERSION: str = "0.1.0"

    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    log: LoggingSettings = Field(default_factory=LoggingSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    ai: AIWorkflowSettings = Field(default_factory=AIWorkflowSettings)

    @model_validator(mode="after")
    def adjust_defaults_by_env(self) -> "Settings":
        if self.APP_ENV == "production":
            self.APP_DEBUG = False
            # Force secure defaults
            if "*" in self.security.allowed_hosts:
                # Issue warning in production, but let settings parse
                pass
        elif self.APP_ENV == "development":
            self.APP_DEBUG = True
            self.db.echo = True
        return self

# Global settings instance
settings = Settings()
