from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import tiktoken
from app.services.enhanced_prompt_engine import EnhancedPromptEngine
from database.mongodb import find_messages_by_conversation, find_message_by_id

class ContextOptimizer:
    """Optimize AI context window to reduce costs and improve performance"""
    
    def __init__(self):
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.max_context_tokens = 4000  # Leave room for response
        self.system_prompt_tokens = 200  # Approximate tokens for system prompt
        self.max_messages = 10  # Maximum number of messages to include
    
    async def optimize_context(
        self, 
        conversation_id: str, 
        current_message: str,
        include_system_prompt: bool = True
    ) -> List[Dict[str, str]]:
        """
        Optimize context for AI request
        
        Args:
            conversation_id: ID of the conversation
            current_message: Current user message
            include_system_prompt: Whether to include system prompt
            
        Returns:
            Optimized list of messages for AI context
        """
        messages = []
        
        # Add system prompt if requested
        if include_system_prompt:
            system_prompt = """You are an expert AI assistant providing comprehensive, professional responses. 
            Format your responses with clear headings, detailed bullet points, and actionable insights. 
            Always provide thorough, well-organized answers that demonstrate deep expertise."""
            
            messages.append({"role": "system", "content": system_prompt})
        
        # Get conversation history
        history_messages = await find_messages_by_conversation(conversation_id, limit=50)
        
        # Calculate available tokens for conversation history
        available_tokens = self.max_context_tokens - self.system_prompt_tokens
        current_message_tokens = len(self.encoding.encode(current_message))
        available_tokens -= current_message_tokens
        
        # Optimize message selection
        optimized_history = self._select_optimal_messages(
            history_messages, 
            available_tokens
        )
        
        # Add optimized history to messages
        messages.extend(optimized_history)
        
        # Add current message
        messages.append({"role": "user", "content": current_message})
        
        return messages
    
    def _select_optimal_messages(
        self, 
        messages: List[Dict[str, Any]], 
        max_tokens: int
    ) -> List[Dict[str, str]]:
        """
        Select optimal messages to fit within token limit
        
        Strategy:
        1. Always include the most recent messages
        2. Prioritize user messages for context
        3. Summarize very old messages if needed
        """
        if not messages:
            return []
        
        selected_messages = []
        used_tokens = 0
        
        # Process messages in reverse order (most recent first)
        for message in reversed(messages):
            message_tokens = len(self.encoding.encode(message["content"]))
            
            # Check if we can add this message
            if used_tokens + message_tokens <= max_tokens:
                # Insert at beginning to maintain chronological order
                selected_messages.insert(0, {
                    "role": message["role"],
                    "content": message["content"]
                })
                used_tokens += message_tokens
            else:
                # If we can't fit more messages, break
                break
        
        # If we have too many messages, keep only the most recent ones
        if len(selected_messages) > self.max_messages:
            selected_messages = selected_messages[-self.max_messages:]
        
        return selected_messages
    
    async def summarize_old_messages(
        self, 
        conversation_id: str, 
        cutoff_date: datetime
    ) -> Optional[str]:
        """
        Summarize messages older than cutoff date
        
        This can be used to create conversation summaries for very long chats
        """
        old_messages = await self._get_messages_before_date(conversation_id, cutoff_date)
        
        if not old_messages:
            return None
        
        # Create summary prompt
        summary_prompt = "Summarize the following conversation in 2-3 sentences:\n\n"
        for msg in old_messages:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            summary_prompt += f"{role_label}: {msg['content']}\n"
        
        try:
            enhanced_engine = EnhancedPromptEngine()
            result = await enhanced_engine.generate_prompt(summary_prompt, "context_optimization")
            summary = result.get("llm_response", "Conversation summary unavailable")
            return summary.strip()
        except:
            return None
    
    async def _get_messages_before_date(
        self, 
        conversation_id: str, 
        cutoff_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get messages before a specific date"""
        all_messages = await find_messages_by_conversation(conversation_id, limit=100)
        
        old_messages = []
        for msg in all_messages:
            if msg["created_at"] < cutoff_date:
                old_messages.append(msg)
            else:
                break
        
        return old_messages
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for a text"""
        return len(self.encoding.encode(text))
    
    def truncate_message(self, message: str, max_tokens: int) -> str:
        """Truncate message to fit within token limit"""
        tokens = self.encoding.encode(message)
        
        if len(tokens) <= max_tokens:
            return message
        
        # Truncate and decode back to text
        truncated_tokens = tokens[:max_tokens]
        return self.encoding.decode(truncated_tokens)

class SmartContextManager:
    """Smart context management with memory of conversation patterns"""
    
    def __init__(self):
        self.optimizer = ContextOptimizer()
        self.conversation_cache = {}  # Simple in-memory cache
    
    async def get_context_for_request(
        self, 
        conversation_id: str, 
        current_message: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """
        Get optimized context with user preferences
        """
        # Check cache first
        cache_key = f"{conversation_id}:{hash(current_message)}"
        if cache_key in self.conversation_cache:
            cached_context = self.conversation_cache[cache_key]
            # Check if cache is still valid (5 minutes)
            if datetime.now() - cached_context["timestamp"] < timedelta(minutes=5):
                return cached_context["messages"]
        
        # Get optimized context
        context = await self.optimizer.optimize_context(conversation_id, current_message)
        
        # Apply user preferences if available
        if user_preferences:
            context = self._apply_user_preferences(context, user_preferences)
        
        # Cache the result
        self.conversation_cache[cache_key] = {
            "messages": context,
            "timestamp": datetime.now()
        }
        
        # Clean old cache entries (keep only last 50)
        if len(self.conversation_cache) > 50:
            oldest_keys = sorted(
                self.conversation_cache.keys(),
                key=lambda k: self.conversation_cache[k]["timestamp"]
            )[:-50]
            for key in oldest_keys:
                del self.conversation_cache[key]
        
        return context
    
    def _apply_user_preferences(
        self, 
        context: List[Dict[str, str]], 
        preferences: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Apply user preferences to context"""
        # Example: user prefers shorter context
        if preferences.get("short_context", False):
            # Keep only last 3 messages
            return context[-3:] if len(context) > 3 else context
        
        # Example: user prefers no system prompt
        if preferences.get("no_system_prompt", False):
            return [msg for msg in context if msg["role"] != "system"]
        
        return context

# Global context manager instance
context_manager = SmartContextManager()
