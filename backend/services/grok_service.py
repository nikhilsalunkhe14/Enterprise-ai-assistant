import os
import httpx
import json
import asyncio
from typing import List, Dict, AsyncGenerator, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GrokService:
    """
    Grok AI Service for ChatGPT Clone
    Handles all interactions with Grok API including streaming responses
    """
    
    def __init__(self):
        self.api_key = os.getenv("GROK_API_KEY")
        self.base_url = "https://api.x.ai/v1"  # Updated Grok API endpoint
        
        if not self.api_key:
            raise ValueError("GROK_API_KEY environment variable is not set")
        
        # Available Grok models
        self.models = {
            "grok-1": {
                "name": "Grok-1",
                "description": "Fast and efficient model for most tasks",
                "max_tokens": 8192,
                "provider": "xai"
            },
            "grok-1.5": {
                "name": "Grok-1.5",
                "description": "Most capable model for complex tasks",
                "max_tokens": 16384,
                "provider": "xai"
            }
        }
    
    async def get_chat_response(
        self, 
        messages: List[Dict], 
        model: str = "grok-1",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> str:
        """
        Get chat response from Grok API
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    error_detail = response.json().get("error", {}).get("message", "Unknown error")
                    logger.error(f"Grok API error: {error_detail}")
                    raise Exception(f"Grok API error: {error_detail}")
                    
        except httpx.TimeoutException:
            logger.error("Request to Grok API timed out")
            raise Exception("Request to Grok API timed out")
        except Exception as e:
            logger.error(f"Error calling Grok API: {str(e)}")
            raise Exception(f"Error calling Grok API: {str(e)}")
    
    async def stream_chat_response(
        self,
        messages: List[Dict],
        model: str = "grok-1",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat response from Grok API
        Returns tokens as they are generated
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status_code != 200:
                        error_detail = (await response.aread()).decode()
                        logger.error(f"Grok API streaming error: {error_detail}")
                        raise Exception(f"Grok API error: {error_detail}")
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix
                            
                            if data == "[DONE]":
                                break
                            
                            try:
                                json_data = json.loads(data)
                                if "choices" in json_data and len(json_data["choices"]) > 0:
                                    delta = json_data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
                                
        except httpx.TimeoutException:
            logger.error("Request to Grok API timed out during streaming")
            raise Exception("Request to Grok API timed out during streaming")
        except Exception as e:
            logger.error(f"Error streaming from Grok API: {str(e)}")
            raise Exception(f"Error streaming from Grok API: {str(e)}")
    
    async def get_available_models(self) -> List[Dict]:
        """
        Get list of available Grok models
        """
        return [
            {
                "id": model_id,
                **model_config
            }
            for model_id, model_config in self.models.items()
        ]
    
    async def validate_model(self, model: str) -> bool:
        """
        Validate if model is available
        """
        return model in self.models
    
    def get_model_info(self, model: str) -> Optional[Dict]:
        """
        Get model information
        """
        return self.models.get(model)
    
    async def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text (rough approximation)
        """
        # Rough estimation: ~4 characters per token
        return len(text) // 4

# Available Grok models for frontend
GROK_MODELS = {
    "grok-1": {
        "name": "Grok-1",
        "description": "Fast and efficient model for most tasks",
        "max_tokens": 8192,
        "provider": "xai"
    },
    "grok-1.5": {
        "name": "Grok-1.5",
        "description": "Most capable model for complex tasks",
        "max_tokens": 16384,
        "provider": "xai"
    }
}
