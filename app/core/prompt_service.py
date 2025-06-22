"""Core prompt service to handle user requests and responses."""
import uuid
import time
from typing import Dict, Optional

from app.filters.filter_manager import filter_manager
from app.schemas.request import PromptRequest
from app.schemas.response import FilteredContent, PromptResponse
from app.services.llm_service import LLMServiceFactory


class PromptService:
    """Core service to handle user prompt requests."""
    
    async def process_prompt(self, request: PromptRequest) -> PromptResponse:
        """
        Process a user prompt request through the filtering and LLM pipeline.
        
        Args:
            request: The prompt request data
            
        Returns:
            PromptResponse: The processed response with filtering information
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 1. Filter the input prompt
        filtered_input, input_masked_elements, input_has_sensitive = filter_manager.filter_text(request.content)
        
        # Create request filtered content object
        request_filtered = FilteredContent(
            original_text=request.content,
            filtered_text=filtered_input,
            has_sensitive_content=input_has_sensitive,
            masked_elements=input_masked_elements
        )
        
        # 2. Get the appropriate LLM service
        llm_service = LLMServiceFactory.get_service(request.provider)
        
        # 3. Generate response from LLM
        response_text, response_metadata = await llm_service.generate_response(
            prompt=filtered_input,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=request.system_prompt,
            **(request.additional_params or {})
        )
        
        # 4. Filter the output response
        filtered_output, output_masked_elements, output_has_sensitive = filter_manager.filter_text(response_text)
        
        # Create response filtered content object
        response_filtered = FilteredContent(
            original_text=response_text,
            filtered_text=filtered_output,
            has_sensitive_content=output_has_sensitive,
            masked_elements=output_masked_elements
        )
        
        # 5. Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # 6. Create and return final response
        return PromptResponse(
            request_id=request_id,
            response_content=filtered_output,
            request_filtered=request_filtered,
            response_filtered=response_filtered,
            model_used=response_metadata.get("model", request.model),
            provider=request.provider.value,
            processing_time_ms=processing_time_ms,
            tokens_used=response_metadata.get("tokens")
        )


# Singleton instance
prompt_service = PromptService() 