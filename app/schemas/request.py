"""Request schemas for the API."""
from typing import Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field


class ModelProvider(str, Enum):
    """Supported model providers."""

    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    
    
class PromptRequest(BaseModel):
    """Schema for prompt request."""

    content: str = Field(..., description="Kullanıcıdan gelen istek içeriği")
    provider: ModelProvider = Field(ModelProvider.OPENAI, description="Kullanılacak AI model sağlayıcısı")
    model: Optional[str] = Field("gpt-3.5-turbo", description="Kullanılacak model adı")
    temperature: Optional[float] = Field(0.7, description="Yaratıcılık seviyesi (0.0-1.0)")
    max_tokens: Optional[int] = Field(1024, description="Maksimum yanıt token sayısı")
    user_id: Optional[str] = Field(None, description="İsteği gönderen kullanıcının ID'si")
    system_prompt: Optional[str] = Field(None, description="Sistem prompt (varsa)")
    additional_params: Optional[Dict] = Field(None, description="Model sağlayıcısına özel parametreler") 