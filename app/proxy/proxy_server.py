"""LLM istekleri için proxy sunucu."""
import json
import logging
import httpx
from typing import Dict, Any, Optional, Union, Callable
from fastapi import Request, Response, HTTPException
from starlette.responses import StreamingResponse

from app.core.config import settings
from app.proxy.mcp_handler import mcp_handler
from app.utils.mcp_utils import is_mcp_request

logger = logging.getLogger(__name__)

# LLM sağlayıcılarının API endpoint'leri
PROVIDER_ENDPOINTS = {
    "openai": "https://api.openai.com/v1/chat/completions",
    "anthropic": "https://api.anthropic.com/v1/messages",
    "google": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
}


class ProxyServer:
    """LLM isteklerini yakalayıp işleyen proxy sunucu."""
    
    def __init__(self):
        """Initialize proxy server."""
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def handle_request(self, request: Request) -> Union[Response, Dict[str, Any]]:
        """
        Gelen isteği işle ve uygun şekilde yönlendir.
        
        Args:
            request: Gelen HTTP isteği
            
        Returns:
            Union[Response, Dict[str, Any]]: İşlenmiş yanıt
        """
        try:
            # İstek gövdesini oku
            body = await request.json()
            
            # MCP formatında mı kontrol et
            if is_mcp_request(body):
                logger.info("MCP formatında istek alındı")
                return await self._handle_mcp_request(body)
            else:
                logger.info("Standart API isteği alındı")
                return await self._handle_api_request(request, body)
                
        except json.JSONDecodeError:
            logger.error("İstek gövdesi JSON formatında değil")
            raise HTTPException(status_code=400, detail="Geçersiz JSON formatı")
        except Exception as e:
            logger.error(f"İstek işlenirken hata: {str(e)}")
            raise HTTPException(status_code=500, detail=f"İstek işlenirken hata: {str(e)}")
    
    async def _handle_mcp_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP formatındaki isteği işle.
        
        Args:
            request_data: MCP formatındaki istek verisi
            
        Returns:
            Dict[str, Any]: İşlenmiş MCP yanıtı
        """
        return await mcp_handler.process_request(request_data)
    
    async def _handle_api_request(self, request: Request, body: Dict[str, Any]) -> Response:
        """
        Standart API isteğini işle ve ilgili sağlayıcıya yönlendir.
        
        Args:
            request: Orijinal HTTP isteği
            body: İstek gövdesi
            
        Returns:
            Response: Sağlayıcıdan gelen yanıt
        """
        # İstek URL'inden sağlayıcıyı belirle
        provider = self._determine_provider(request.url.path)
        
        if not provider:
            raise HTTPException(status_code=400, detail="Desteklenmeyen API endpoint")
        
        # Sağlayıcı endpoint'ini al
        target_url = PROVIDER_ENDPOINTS.get(provider)
        
        if not target_url:
            raise HTTPException(status_code=400, detail=f"Desteklenmeyen sağlayıcı: {provider}")
        
        # İsteği ilgili sağlayıcıya yönlendir
        headers = dict(request.headers)
        headers.pop("host", None)
        
        # API anahtarını ekle
        api_key = self._get_api_key(provider)
        if provider == "openai":
            headers["Authorization"] = f"Bearer {api_key}"
        elif provider == "anthropic":
            headers["x-api-key"] = api_key
        elif provider == "google":
            target_url = f"{target_url}?key={api_key}"
        
        # İsteği gönder
        response = await self.client.post(
            target_url,
            json=body,
            headers=headers
        )
        
        # Yanıtı döndür
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    
    def _determine_provider(self, path: str) -> Optional[str]:
        """
        İstek yolundan sağlayıcıyı belirle.
        
        Args:
            path: İstek URL yolu
            
        Returns:
            Optional[str]: Sağlayıcı adı veya None
        """
        if "openai" in path or "chat/completions" in path:
            return "openai"
        elif "anthropic" in path or "messages" in path:
            return "anthropic"
        elif "google" in path or "gemini" in path:
            return "google"
        return None
    
    def _get_api_key(self, provider: str) -> str:
        """
        Sağlayıcı için API anahtarını al.
        
        Args:
            provider: Sağlayıcı adı
            
        Returns:
            str: API anahtarı
        """
        if provider == "openai":
            return settings.OPENAI_API_KEY or ""
        elif provider == "anthropic":
            return settings.ANTHROPIC_API_KEY or ""
        elif provider == "google":
            return settings.GOOGLE_API_KEY or ""
        return ""


# Singleton instance
proxy_server = ProxyServer() 