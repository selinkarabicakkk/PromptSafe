"""MCP (Model-Context-Protocol) için yardımcı fonksiyonlar."""
from typing import Dict, Any, Tuple, Optional, List


def extract_mcp_data(request_data: Dict[str, Any]) -> Tuple[str, str, str, Dict[str, Any]]:
    """
    MCP formatındaki istekten gerekli verileri ayıklar.
    
    Args:
        request_data: MCP formatındaki istek verisi
        
    Returns:
        Tuple[str, str, str, Dict[str, Any]]: 
            - İçerik metni
            - Provider adı
            - Model adı
            - Ek parametreler
    """
    # İstek içeriğini al
    messages = request_data.get("messages", [])
    content = ""
    
    # Son kullanıcı mesajını bul
    for message in reversed(messages):
        if message.get("role") == "user":
            content = message.get("content", "")
            break
    
    # Provider ve model bilgilerini al
    provider = request_data.get("provider", "openai")
    model = request_data.get("model", "gpt-3.5-turbo")
    
    # Diğer parametreleri topla
    params = {
        "temperature": request_data.get("temperature", 0.7),
        "max_tokens": request_data.get("max_tokens", 1024),
    }
    
    # Sistem mesajını kontrol et
    for message in messages:
        if message.get("role") == "system":
            params["system_prompt"] = message.get("content", "")
            break
    
    return content, provider, model, params


def create_mcp_response(
    response_text: str, 
    original_request: Dict[str, Any], 
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    MCP formatında yanıt oluşturur.
    
    Args:
        response_text: LLM'den dönen filtrelenmiş yanıt metni
        original_request: Orijinal MCP isteği
        metadata: Yanıta eklenecek metadata
        
    Returns:
        Dict[str, Any]: MCP formatında yanıt
    """
    # Orijinal isteğin bir kopyasını oluştur
    response = original_request.copy()
    
    # Mesajları güncelle
    messages = response.get("messages", [])
    
    # Asistan yanıtını ekle
    messages.append({
        "role": "assistant",
        "content": response_text
    })
    
    response["messages"] = messages
    
    # PromptSafe metadata'sını ekle
    response["promptsafe_metadata"] = metadata
    
    return response


def is_mcp_request(request_data: Dict[str, Any]) -> bool:
    """
    Bir isteğin MCP formatında olup olmadığını kontrol eder.
    
    Args:
        request_data: Kontrol edilecek istek verisi
        
    Returns:
        bool: İstek MCP formatında ise True
    """
    # MCP formatında olması için gereken minimum alanlar
    required_fields = ["messages"]
    
    # Tüm gerekli alanların var olup olmadığını kontrol et
    for field in required_fields:
        if field not in request_data:
            return False
    
    # messages alanının bir liste olup olmadığını ve en az bir mesaj içerip içermediğini kontrol et
    messages = request_data.get("messages", [])
    if not isinstance(messages, list) or len(messages) == 0:
        return False
    
    # En az bir mesajın role ve content alanlarına sahip olup olmadığını kontrol et
    for message in messages:
        if not isinstance(message, dict):
            return False
        if "role" not in message or "content" not in message:
            return False
    
    return True 