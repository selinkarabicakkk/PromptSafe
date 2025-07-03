"""Model-Context-Protocol (MCP) entegrasyonu için handler sınıfı."""
import json
import logging
from typing import Dict, Any, Optional, Tuple

from app.core.config import settings
from app.core.prompt_service import prompt_service
from app.schemas.request import PromptRequest, ModelProvider
from app.utils.mcp_utils import extract_mcp_data, create_mcp_response

logger = logging.getLogger(__name__)

class MCPHandler:
    """MCP protokolü üzerinden gelen istekleri işleyen sınıf."""
    
    def __init__(self):
        """Initialize MCP handler."""
        self.supported_providers = {
            "openai": ModelProvider.OPENAI,
            "anthropic": ModelProvider.ANTHROPIC,
            "google": ModelProvider.GOOGLE,
        }
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP formatındaki isteği işle ve filtrelenmiş yanıtı döndür.
        
        Args:
            request_data: MCP formatındaki istek verisi
            
        Returns:
            Dict[str, Any]: MCP formatında filtrelenmiş yanıt
        """
        try:
            # MCP verilerini ayıkla
            content, provider_name, model, params = extract_mcp_data(request_data)
            
            # Provider adını PromptSafe'in desteklediği formata dönüştür
            provider = self._map_provider(provider_name)
            
            # PromptRequest oluştur
            prompt_request = PromptRequest(
                content=content,
                provider=provider,
                model=model,
                temperature=params.get("temperature", 0.7),
                max_tokens=params.get("max_tokens", 1024),
                system_prompt=params.get("system_prompt"),
                additional_params=params
            )
            
            # PromptSafe ile işle
            response = await prompt_service.process_prompt(prompt_request)
            
            # Yanıtı MCP formatına dönüştür
            mcp_response = create_mcp_response(
                response.response_content,
                request_data,
                {
                    "filtered_input": response.request_filtered.has_sensitive_content,
                    "filtered_output": response.response_filtered.has_sensitive_content,
                    "processing_time_ms": response.processing_time_ms,
                    "request_id": response.request_id
                }
            )
            
            return mcp_response
            
        except Exception as e:
            logger.error(f"MCP isteği işlenirken hata: {str(e)}")
            # Hata durumunda basit bir yanıt döndür
            return {
                "error": True,
                "message": f"İstek işlenirken hata oluştu: {str(e)}"
            }
    
    def _map_provider(self, provider_name: str) -> ModelProvider:
        """
        Provider adını PromptSafe'in desteklediği formata dönüştür.
        
        Args:
            provider_name: MCP'den gelen provider adı
            
        Returns:
            ModelProvider: PromptSafe'in desteklediği provider enum değeri
        """
        provider_name = provider_name.lower()
        
        # Provider adını kontrol et
        if provider_name in self.supported_providers:
            return self.supported_providers[provider_name]
        
        # Desteklenmeyen provider için varsayılan olarak OpenAI kullan
        logger.warning(f"Desteklenmeyen provider: {provider_name}, OpenAI kullanılıyor")
        return ModelProvider.OPENAI


# Singleton instance
mcp_handler = MCPHandler() 