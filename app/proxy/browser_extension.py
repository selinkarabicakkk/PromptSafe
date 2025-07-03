"""Tarayıcı eklentisi için yardımcı sınıf ve fonksiyonlar."""
import json
import logging
from typing import Dict, Any, Optional

from fastapi import WebSocket, WebSocketDisconnect
from app.proxy.mcp_handler import mcp_handler

logger = logging.getLogger(__name__)


class BrowserExtensionManager:
    """Tarayıcı eklentisi bağlantılarını yöneten sınıf."""
    
    def __init__(self):
        """Initialize browser extension manager."""
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """
        Yeni bir WebSocket bağlantısı kabul et.
        
        Args:
            websocket: WebSocket bağlantısı
            client_id: İstemci tanımlayıcısı
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Yeni WebSocket bağlantısı: {client_id}")
    
    def disconnect(self, client_id: str):
        """
        WebSocket bağlantısını kapat.
        
        Args:
            client_id: İstemci tanımlayıcısı
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket bağlantısı kapatıldı: {client_id}")
    
    async def handle_message(self, websocket: WebSocket, client_id: str):
        """
        WebSocket üzerinden gelen mesajları işle.
        
        Args:
            websocket: WebSocket bağlantısı
            client_id: İstemci tanımlayıcısı
        """
        try:
            while True:
                # Mesajı al
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Mesaj tipini kontrol et
                message_type = message.get("type")
                
                if message_type == "prompt":
                    # Prompt işleme
                    await self._handle_prompt_message(websocket, message)
                elif message_type == "ping":
                    # Ping mesajına yanıt ver
                    await websocket.send_json({"type": "pong"})
                else:
                    # Bilinmeyen mesaj tipi
                    logger.warning(f"Bilinmeyen mesaj tipi: {message_type}")
                    await websocket.send_json({
                        "type": "error",
                        "error": f"Bilinmeyen mesaj tipi: {message_type}"
                    })
                    
        except WebSocketDisconnect:
            self.disconnect(client_id)
        except Exception as e:
            logger.error(f"WebSocket mesajı işlenirken hata: {str(e)}")
            try:
                await websocket.send_json({
                    "type": "error",
                    "error": f"Mesaj işlenirken hata: {str(e)}"
                })
            except:
                pass
    
    async def _handle_prompt_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        Prompt mesajını işle.
        
        Args:
            websocket: WebSocket bağlantısı
            message: Gelen mesaj
        """
        try:
            # Prompt verilerini al
            prompt_data = message.get("data", {})
            
            # MCP handler ile işle
            result = await mcp_handler.process_request(prompt_data)
            
            # Sonucu gönder
            await websocket.send_json({
                "type": "response",
                "data": result
            })
            
        except Exception as e:
            logger.error(f"Prompt işlenirken hata: {str(e)}")
            await websocket.send_json({
                "type": "error",
                "error": f"Prompt işlenirken hata: {str(e)}"
            })


# Singleton instance
browser_extension_manager = BrowserExtensionManager() 