"""Integration services for different LLM providers."""
import time
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple

from app.core.config import settings
from app.schemas.request import ModelProvider, PromptRequest
from app.schemas.response import FilteredContent, PromptResponse


class BaseLLMService(ABC):
    """Base abstract class for all LLM service integrations."""
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        Generate response from the LLM provider.
        
        Args:
            prompt: The processed prompt text
            **kwargs: Additional parameters for the model
        
        Returns:
            Tuple[str, Dict]: Response text and metadata
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the service is available (has API key, etc.)"""
        pass


class OpenAIService(BaseLLMService):
    """OpenAI API integration service."""
    
    def __init__(self):
        """Initialize the OpenAI service."""
        self.api_key = settings.OPENAI_API_KEY
        
    def is_available(self) -> bool:
        """Check if OpenAI service is available."""
        return self.api_key is not None and len(self.api_key) > 0
        
    async def generate_response(self, prompt: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """Generate response using OpenAI API."""
        try:
            import openai
            
            # Set API key
            client = openai.OpenAI(api_key=self.api_key)
            
            # Get parameters
            model = kwargs.get("model", "gpt-3.5-turbo")
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 1024)
            system_prompt = kwargs.get("system_prompt")
            
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Call API
            start_time = time.time()
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            end_time = time.time()
            
            # Extract response
            response_text = response.choices[0].message.content
            
            # Prepare metadata
            metadata = {
                "model": model,
                "processing_time_ms": (end_time - start_time) * 1000,
                "tokens": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            return response_text, metadata
            
        except ImportError:
            # Handle missing openai package
            return "OpenAI paketi yüklü değil.", {"error": "openai paketi yüklü değil."}
            
        except Exception as e:
            # Handle API errors
            error_msg = f"OpenAI API hatası: {str(e)}"
            return error_msg, {"error": error_msg}


class GoogleAIService(BaseLLMService):
    """Google (Gemini) API integration service."""
    
    def __init__(self):
        """Initialize the Google AI service."""
        self.api_key = settings.GOOGLE_API_KEY
        
    def is_available(self) -> bool:
        """Check if Google AI service is available."""
        return self.api_key is not None and len(self.api_key) > 0
        
    async def generate_response(self, prompt: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """Generate response using Google Generative AI API."""
        try:
            import google.generativeai as genai
            
            # Set API key
            genai.configure(api_key=self.api_key)
            
            # Get parameters
            model = kwargs.get("model", "gemini-pro")
            temperature = kwargs.get("temperature", 0.7)
            
            # Call API
            start_time = time.time()
            model_instance = genai.GenerativeModel(model)
            response = model_instance.generate_content(prompt, generation_config={"temperature": temperature})
            end_time = time.time()
            
            # Extract response
            response_text = response.text
            
            # Prepare metadata
            metadata = {
                "model": model,
                "processing_time_ms": (end_time - start_time) * 1000,
            }
            
            return response_text, metadata
            
        except ImportError:
            # Handle missing google-generativeai package
            return "Google GenerativeAI paketi yüklü değil.", {"error": "google-generativeai paketi yüklü değil."}
            
        except Exception as e:
            # Handle API errors
            error_msg = f"Google API hatası: {str(e)}"
            return error_msg, {"error": error_msg}


class AnthropicService(BaseLLMService):
    """Anthropic (Claude) API integration service."""
    
    def __init__(self):
        """Initialize the Anthropic service."""
        self.api_key = settings.ANTHROPIC_API_KEY
        
    def is_available(self) -> bool:
        """Check if Anthropic service is available."""
        return self.api_key is not None and len(self.api_key) > 0
        
    async def generate_response(self, prompt: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """Generate response using Anthropic API."""
        try:
            import anthropic
            
            # Set API key
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # Get parameters
            model = kwargs.get("model", "claude-3-haiku-20240307")
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 1024)
            system_prompt = kwargs.get("system_prompt")
            
            # Call API
            start_time = time.time()
            message = client.messages.create(
                model=model,
                system=system_prompt or "",
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            end_time = time.time()
            
            # Extract response
            response_text = message.content[0].text
            
            # Prepare metadata
            metadata = {
                "model": model,
                "processing_time_ms": (end_time - start_time) * 1000,
            }
            
            return response_text, metadata
            
        except ImportError:
            # Handle missing anthropic package
            return "Anthropic paketi yüklü değil.", {"error": "anthropic paketi yüklü değil."}
            
        except Exception as e:
            # Handle API errors
            error_msg = f"Anthropic API hatası: {str(e)}"
            return error_msg, {"error": error_msg}


class LLMServiceFactory:
    """Factory class for creating LLM services based on provider."""
    
    @staticmethod
    def get_service(provider: ModelProvider) -> BaseLLMService:
        """
        Get the appropriate LLM service based on provider.
        
        Args:
            provider: The model provider to use
            
        Returns:
            BaseLLMService: An instance of the LLM service
        """
        if provider == ModelProvider.OPENAI:
            return OpenAIService()
        elif provider == ModelProvider.GOOGLE:
            return GoogleAIService()
        elif provider == ModelProvider.ANTHROPIC:
            return AnthropicService()
        else:
            # Default to OpenAI
            return OpenAIService() 