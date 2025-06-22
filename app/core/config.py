"""Application configuration module."""
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# .env dosyasını yükle (varsa)
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    # API keys
    OPENAI_API_KEY: Optional[str] = Field(None, env="OPENAI_API_KEY")
    GOOGLE_API_KEY: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")

    # Service configs
    PROJECT_NAME: str = "PromptSafe"
    API_V1_STR: str = "/api/v1"
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Security
    SECRET_KEY: str = Field(
        default="dogrulama_icin_cok_gizli_anahtar_buraya_yazilmali", env="SECRET_KEY"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Features
    ENABLE_REGEX_FILTERS: bool = Field(default=True, env="ENABLE_REGEX_FILTERS")
    ENABLE_NER_FILTERS: bool = Field(default=True, env="ENABLE_NER_FILTERS")
    
    # Text configs
    MAX_TEXT_LENGTH: int = Field(default=8192, env="MAX_TEXT_LENGTH")

    class Config:
        """Pydantic configuration."""

        case_sensitive = True
        env_file = ".env"


settings = Settings() 