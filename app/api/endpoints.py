"""API endpoint routes for the PromptSafe application."""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse

from app import __version__
from app.core.config import settings
from app.core.prompt_service import prompt_service
from app.proxy.proxy_server import proxy_server
from app.proxy.system_proxy import system_proxy
from app.schemas.request import PromptRequest
from app.schemas.response import HealthResponse, PromptResponse
from app.services.llm_service import (
    OpenAIService,
    GoogleAIService,
    AnthropicService,
)

router = APIRouter()


@router.post("/prompt", response_model=PromptResponse)
async def process_prompt(request: PromptRequest):
    """
    Process user prompt through security filters and LLM.
    
    - Filters sensitive information from input
    - Sends cleaned prompt to selected LLM
    - Filters sensitive information from LLM response
    - Returns processed output with metadata
    """
    try:
        response = await prompt_service.process_prompt(request)
        return response
    except Exception as e:
        # Log error properly in production
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"İşleme hatası: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Service health check endpoint.
    
    Checks API connectivity status to all LLM providers.
    """
    # Check provider availability
    openai_service = OpenAIService()
    google_service = GoogleAIService()
    anthropic_service = AnthropicService()
    
    provider_status = {
        "openai": openai_service.is_available(),
        "google": google_service.is_available(),
        "anthropic": anthropic_service.is_available(),
    }
    
    return HealthResponse(
        status="active",
        version=__version__,
        environment=settings.ENVIRONMENT,
        providers=provider_status
    )


# Yeni proxy endpoint'leri
@router.post("/proxy/mcp")
async def proxy_mcp_request(request: Request):
    """
    MCP formatındaki istekleri işleyen proxy endpoint.
    
    Bu endpoint, Model-Context-Protocol formatındaki istekleri alır,
    hassas verileri filtreler ve sonucu döndürür.
    """
    result = await proxy_server.handle_request(request)
    if isinstance(result, Response):
        return result
    return JSONResponse(content=result)


@router.post("/proxy/{provider}/{path:path}")
async def proxy_api_request(request: Request, provider: str, path: str):
    """
    LLM API isteklerini proxy'leyen genel endpoint.
    
    Bu endpoint, standart LLM API isteklerini yakalayıp ilgili sağlayıcıya yönlendirir,
    ancak önce hassas verileri filtreler.
    
    Args:
        provider: LLM sağlayıcısı (openai, anthropic, google)
        path: API yolu
    """
    return await proxy_server.handle_request(request)


# Sistem proxy endpoint'leri
@router.post("/system-proxy/enable")
async def enable_system_proxy():
    """
    Sistem seviyesinde proxy ayarlarını etkinleştirir.
    
    Bu endpoint, işletim sisteminin proxy ayarlarını PromptSafe'e yönlendirecek şekilde yapılandırır.
    """
    success = system_proxy.enable()
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sistem proxy ayarları etkinleştirilemedi"
        )
    
    return {"status": "success", "message": "Sistem proxy ayarları etkinleştirildi"}


@router.post("/system-proxy/disable")
async def disable_system_proxy():
    """
    Sistem seviyesinde proxy ayarlarını devre dışı bırakır.
    
    Bu endpoint, işletim sisteminin proxy ayarlarını normal haline döndürür.
    """
    success = system_proxy.disable()
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sistem proxy ayarları devre dışı bırakılamadı"
        )
    
    return {"status": "success", "message": "Sistem proxy ayarları devre dışı bırakıldı"} 