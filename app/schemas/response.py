"""Response schemas for the API."""
from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class FilteredContent(BaseModel):
    """Schema for filtered content information."""

    original_text: str = Field(..., description="Orijinal metin")
    filtered_text: str = Field(..., description="Filtrelenmiş metin")
    has_sensitive_content: bool = Field(..., description="Hassas içerik tespit edildi mi?")
    masked_elements: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Maskelenen içerik öğeleri"
    )


class PromptResponse(BaseModel):
    """Schema for prompt response."""

    request_id: str = Field(..., description="İstek ID'si")
    response_content: str = Field(..., description="Model yanıtı")
    request_filtered: FilteredContent = Field(..., description="Filtrelenmiş istek içeriği")
    response_filtered: FilteredContent = Field(..., description="Filtrelenmiş yanıt içeriği")
    model_used: str = Field(..., description="Kullanılan model adı")
    provider: str = Field(..., description="Kullanılan sağlayıcı")
    processing_time_ms: float = Field(..., description="İşleme süresi (ms)")
    timestamp: datetime = Field(default_factory=datetime.now, description="Yanıt zamanı")
    tokens_used: Optional[Dict[str, int]] = Field(None, description="Kullanılan token sayısı")


class HealthResponse(BaseModel):
    """Schema for health check response."""

    status: str = Field(..., description="Servis durumu")
    version: str = Field(..., description="API versiyonu")
    environment: str = Field(..., description="Çalışma ortamı")
    providers: Dict[str, bool] = Field(..., description="API sağlayıcıları durumu") 