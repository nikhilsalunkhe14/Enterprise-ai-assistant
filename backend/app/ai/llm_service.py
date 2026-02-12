import os
import httpx
import asyncio
from groq import Groq
from backend.app.core.config import settings
from backend.app.core.logger import logger

class LLMService:
    def __init__(self):
        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )
        self.model = "llama-3.1-8b-instant"  # free + powerful
        self.timeout = 45.0  # Stable timeout for production

    def generate_response(self, system_prompt: str, user_prompt: str):
        logger.info(f"Generating LLM response with model: {self.model}")
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
                timeout=self.timeout
            )

            response = completion.choices[0].message.content
            logger.info("LLM response generated successfully")
            return response

        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            return f"LLM Error: {str(e)}"
