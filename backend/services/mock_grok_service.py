import os
import asyncio
import json
from typing import List, Dict, AsyncGenerator, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MockGrokService:
    """
    Mock Grok AI Service for Testing
    Simulates AI responses without requiring real API key
    """
    
    def __init__(self):
        self.api_key = os.getenv("GROK_API_KEY", "mock_key")
        self.base_url = "https://mock-api.x.ai/v1"
        
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
        Get mock chat response
        """
        # Simulate API delay
        await asyncio.sleep(1)
        
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                user_message = msg["content"]
                break
        
        # Generate contextual response
        response = self.generate_mock_response(user_message, model)
        
        logger.info(f"Mock response generated for model {model}")
        return response
    
    async def stream_chat_response(
        self,
        messages: List[Dict],
        model: str = "grok-1",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """
        Stream mock chat response
        """
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                user_message = msg["content"]
                break
        
        # Generate full response
        full_response = self.generate_mock_response(user_message, model)
        
        # Stream it word by word
        words = full_response.split()
        for i, word in enumerate(words):
            chunk = word + " "
            yield chunk
            
            # Simulate typing delay
            await asyncio.sleep(0.05)
            
            # Add occasional longer pauses
            if i % 10 == 0:
                await asyncio.sleep(0.2)
    
    def generate_mock_response(self, user_message: str, model: str) -> str:
        """
        Generate contextual mock responses
        """
        user_message_lower = user_message.lower()
        
        # Greeting responses
        if any(greeting in user_message_lower for greeting in ["hello", "hi", "hey", "good morning", "good evening"]):
            return f"""Hello! I'm Grok-{model.split('-')[1]}, your AI assistant. I'm here to help you with any questions or tasks you might have. How can I assist you today?"""
        
        # How are you responses
        if any(phrase in user_message_lower for phrase in ["how are you", "how do you do", "what's up"]):
            return f"""I'm functioning optimally as Grok-{model.split('-')[1]}! Thanks for asking. I'm ready to help you with any questions, coding tasks, analysis, or creative work. What would you like to explore today?"""
        
        # Code-related responses
        if any(keyword in user_message_lower for keyword in ["code", "programming", "python", "javascript", "function", "algorithm"]):
            return f"""As Grok-{model.split('-')[1]}, I'd be happy to help with your coding question! 

Here's a general approach to coding problems:

1. **Understand the Requirements**: Break down the problem into smaller, manageable parts
2. **Plan Your Solution**: Think about the logic before writing code
3. **Write Clean Code**: Use meaningful variable names and comments
4. **Test Thoroughly**: Check edge cases and validate inputs
5. **Refactor**: Improve efficiency and readability

Could you provide more specific details about what you're trying to accomplish? I can then give you more targeted assistance with actual code examples."""
        
        # Learning/education responses
        if any(keyword in user_message_lower for keyword in ["learn", "study", "explain", "teach me", "help me understand"]):
            return f"""I'd be delighted to help you learn! As Grok-{model.split('-')[1]}, I can explain complex topics in simple terms.

**Effective Learning Strategies:**
- Start with the fundamentals
- Use analogies and real-world examples
- Practice with hands-on exercises
- Ask questions when confused
- Connect new concepts to what you already know

What specific topic would you like to explore? Whether it's science, technology, mathematics, or any other subject, I'm here to make learning engaging and understandable."""
        
        # Creative responses
        if any(keyword in user_message_lower for keyword in ["create", "write", "story", "poem", "creative", "imagine"]):
            return f"""Creative request! I love helping with creative projects as Grok-{model.split('-')[1]}.

**Creative Process Tips:**
1. **Brainstorm freely** - Don't judge initial ideas
2. **Find your inspiration** - Look at what moves you emotionally
3. **Create consistently** - Make creativity a daily habit
4. **Experiment** - Try new styles and approaches
5. **Get feedback** - Share your work with others

What kind of creative project are you working on? I can help with writing prompts, story ideas, character development, or any other creative endeavor."""
        
        # Problem-solving responses
        if any(keyword in user_message_lower for keyword in ["problem", "solve", "solution", "help me with", "issue", "challenge"]):
            return f"""I'm here to help you solve problems! As Grok-{model.split('-')[1]}, I can assist with systematic problem-solving.

**Problem-Solving Framework:**
1. **Define the Problem**: Clearly articulate what you're trying to solve
2. **Gather Information**: Collect relevant data and context
3. **Identify Root Causes**: Look beyond surface symptoms
4. **Brainstorm Solutions**: Generate multiple approaches
5. **Evaluate Options**: Consider pros and cons
6. **Implement and Monitor**: Execute the best solution and track results

What specific problem are you facing? The more details you provide, the better I can assist you."""
        
        # Default response
        return f"""Thank you for your message! As Grok-{model.split('-')[1]}, I'm here to assist you with a wide range of topics and tasks.

**I can help you with:**
- Answering questions and providing explanations
- Creative writing and brainstorming
- Problem-solving and critical thinking
- Learning new concepts and skills
- Technical assistance and coding
- Analysis and research
- And much more!

Your message was: "{user_message}"

Could you please provide more details about what you'd like help with? I'm ready to assist with whatever you need!"""
    
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
        return len(text) // 4

# Available Grok models for frontend
MOCK_GROK_MODELS = {
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
