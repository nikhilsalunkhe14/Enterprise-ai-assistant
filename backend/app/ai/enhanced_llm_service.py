import asyncio
import time
from typing import Optional, Dict, Any
from groq import Groq
from app.core.config import settings
from app.core.logger import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            raise e

class EnhancedLLMService:
    def __init__(self):
        api_key = settings.GROQ_API_KEY
        print(f"🔍 DEBUG: GROQ_API_KEY loaded: {'SET' if api_key else 'NOT SET'}")
        print(f"🔍 DEBUG: API key length: {len(api_key) if api_key else 0}")
        
        if not api_key:
            print("🚨 CRITICAL: GROQ_API_KEY is not set! LLM calls will fail.")
            raise Exception("GROQ_API_KEY not configured")
            
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"
        self.circuit_breaker = CircuitBreaker()
        self.timeout = 30.0
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError))
    )
    async def generate_response_with_retry(self, system_prompt: str, user_prompt: str) -> str:
        """Generate LLM response with retry and circuit breaker"""
        logger.info(f"Generating LLM response with model: {self.model}")
        print(f"🔍 DEBUG: LLM model: {self.model}")
        print(f"🔍 DEBUG: System prompt: {system_prompt[:50]}...")
        print(f"🔍 DEBUG: User prompt: {user_prompt[:50]}...")
        
        try:
            completion = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000,
                    timeout=self.timeout
                ),
                timeout=self.timeout
            )
            
            response = completion.choices[0].message.content
            logger.info("LLM response generated successfully")
            print(f"🔍 DEBUG: Raw LLM response: {response[:100]}...")
            
            # Extract token usage
            token_usage = {
                "prompt_tokens": completion.usage.prompt_tokens if completion.usage else 0,
                "completion_tokens": completion.usage.completion_tokens if completion.usage else 0,
                "total_tokens": completion.usage.total_tokens if completion.usage else 0
            }
            print(f"🔍 DEBUG: Token usage: {token_usage}")
            
            return response, token_usage
            
        except asyncio.TimeoutError:
            logger.error("LLM request timed out")
            raise Exception("LLM request timeout")
        except Exception as e:
            logger.error(f"LLM API error: {str(e)}")
            raise e
    
    async def generate_response(self, system_prompt: str, user_prompt: str) -> tuple:
        """Main response method with fallback"""
        print(f"🔍 DEBUG: generate_response() called")
        print(f"🔍 DEBUG: System prompt: {system_prompt[:50]}...")
        print(f"🔍 DEBUG: User prompt: {user_prompt[:50]}...")
        
        try:
            return await self.generate_response_with_retry(system_prompt, user_prompt)
        except Exception as e:
            print(f"🔍 DEBUG: LLM call failed: {type(e).__name__}: {str(e)}")
            logger.error(f"LLM service failed: {str(e)}")
            fallback_response = self._get_fallback_response(system_prompt, user_prompt)
            return fallback_response, {"total_tokens": 0}
    
    def _get_fallback_response(self, system_prompt: str, user_prompt: str) -> str:
        """Fallback response when LLM is unavailable"""
        return """I apologize, but I'm currently experiencing technical difficulties with my AI service. 

Here's a basic structured response based on your query:

**Overview**
Your query has been received and will be processed as soon as the AI service is restored.

**Planning**
- Review your requirements once the service is available
- Consider standard project management practices

**Execution**
- Wait for service restoration
- Proceed with manual planning in the meantime

**Risk Management**
- Service unavailability is a temporary risk
- Have backup manual processes ready

**Deliverables**
- Project requirements document
- Implementation timeline (when service restored)

**Success Metrics**
- Service restoration time
- Project continuity maintained

Please try again in a few minutes. If the issue persists, contact your system administrator."""
