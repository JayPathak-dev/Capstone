from typing import List, Union
import json
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "paimana-secret-key-development-environment-placeholder"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PAIMANA Infrastructure Intelligence"

    # Database
    DATABASE_URL: str = "sqlite:///./paimana.db"

    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        return v

    # ML & Inference
    ML_MODEL_DIR: str = "./ml/artifacts"
    ENABLE_FALLBACK_SCORING: bool = True

    # AI Assistant
    LLM_PROVIDER: str = "mock"  # mock, gemini, openai
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_MODEL_NAME: str = "gemini-1.5-flash"

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
