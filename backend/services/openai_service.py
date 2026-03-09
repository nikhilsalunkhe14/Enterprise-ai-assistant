import os
import httpx
import json
from typing import List, Dict, AsyncGenerator
from datetime import datetime

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    async def get_chat_response(
        self, 
        messages: List[Dict], 
        model: str = "gpt-3.5-turbo",
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Get chat response from OpenAI"""
        
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
                    raise Exception(f"OpenAI API error: {error_detail}")
                    
        except httpx.TimeoutException:
            raise Exception("Request to OpenAI API timed out")
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")
    
    async def stream_chat_response(
        self,
        messages: List[Dict],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """Stream chat response from OpenAI"""
        
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
                        raise Exception(f"OpenAI API error: {error_detail}")
                    
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
            raise Exception("Request to OpenAI API timed out")
        except Exception as e:
            raise Exception(f"Error streaming from OpenAI API: {str(e)}")

# Available OpenAI models
OPENAI_MODELS = {
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "description": "Fast and efficient model for most tasks",
        "max_tokens": 4096,
        "provider": "openai"
    },
    "gpt-4": {
        "name": "GPT-4",
        "description": "Most capable model for complex tasks",
        "max_tokens": 8192,
        "provider": "openai"
    },
    "gpt-4-turbo": {
        "name": "GPT-4 Turbo",
        "description": "Latest GPT-4 model with improved performance",
        "max_tokens": 128000,
        "provider": "openai"
    }
}
