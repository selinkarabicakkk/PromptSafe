"""API endpoint routes for the PromptSafe application."""
from fastapi import APIRouter, Depends, HTTPException, status

from app import __version__
from app.core.config import settings
from app.core.prompt_service import prompt_service
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