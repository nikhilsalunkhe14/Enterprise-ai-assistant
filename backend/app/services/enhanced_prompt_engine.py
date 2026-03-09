import time
import asyncio
import traceback
from typing import Dict, Any, Optional
from app.database import db_manager
from app.ai.enhanced_llm_service import EnhancedLLMService
from app.tools.tool_service import ToolService
from app.core.logger import logger
from app.core.security import InputValidator
from app.core.error_handler import ErrorHandler, PerformanceMonitor
# from app.core.nlp_processor import NLPProcessor
# from app.services.pm_integration import PMToolIntegration

class EnhancedPromptEngine:
    def __init__(self):
        self.llm = EnhancedLLMService()
        self.error_handler = ErrorHandler()
        self.performance_monitor = PerformanceMonitor()
        self.tools = ToolService()
        # self.nlp_processor = NLPProcessor()
        # self.pm_integration = PMToolIntegration()
        self.prompt_version = "v2.1"
        
        # Enterprise features
        self.response_cache = {}
        self.metrics_collector = {}
        
    def _apply_guardrails(self, user_query: str) -> str:
        """Apply safety guardrails to prevent prompt injection"""
        blocked_terms = ["ignore previous instructions", "system prompt", "disregard all above"]
        
        for term in blocked_terms:
            if term in user_query.lower():
                raise ValueError("Potential prompt injection detected")
        
        return user_query
    
    def _optimize_prompt(self, user_query: str) -> str:
        """Enhance user query for better LLM reasoning"""
        return f"""
Analyze the user request carefully and provide a structured, technical response.

User Request:
{user_query}

Requirements:
- Provide structured reasoning with clear steps
- Include technical accuracy and specific details
- Recommend modern tools and frameworks
- Suggest realistic timelines and identify risks
- Use the specified response format
"""
    
    def _estimate_cost(self, tokens: int) -> float:
        """Estimate API cost based on token usage"""
        cost_per_1k = 0.0002  # Groq pricing
        return (tokens / 1000) * cost_per_1k
    
    def _detect_user_persona(self, user_query: str) -> str:
        """Detect user persona to tailor response style"""
        technical_keywords = ['code', 'library', 'framework', 'api', 'implement', 'develop', 'python', 'javascript']
        business_keywords = ['cost', 'roi', 'timeline', 'budget', 'roadmap', 'risk', 'investment', 'strategy']
        
        user_query_lower = user_query.lower()
        
        if any(word in user_query_lower for word in technical_keywords):
            return "ENGINEER"
        elif any(word in user_query_lower for word in business_keywords):
            return "MANAGER"
        return "GENERAL"
    
    def _create_contextual_system_prompt(self, user_query: str) -> str:
        """Create system prompt tailored to user persona"""
        persona = self._detect_user_persona(user_query)
        
        base_prompt = """
You are a senior AI architect and machine learning consultant specializing in Software Development Lifecycle (SDLC) guidance.

Your job is to help teams navigate the entire Software Development Lifecycle with AI-powered insights, ensuring efficiency, compliance, and quality.

SDLC PHASES YOU COVER:
1. **Planning & Requirements**: User stories, technical specifications, risk assessment
2. **Design**: Architecture, system design, database design, API design
3. **Development**: Coding standards, best practices, version control
4. **Testing**: Unit testing, integration testing, quality assurance
5. **Deployment**: CI/CD, infrastructure, monitoring
6. **Maintenance**: Bug fixes, updates, performance optimization

When answering:
1. Understand the SDLC phase and context
2. Provide structured guidance for that specific phase
3. Recommend modern tools and frameworks
4. Suggest realistic timelines and identify risks
5. Ensure compliance and quality standards
6. Use NLP analysis for better understanding

OUTPUT FORMAT:
Always return answers using this structure:

Overview
Technical Approach
Implementation Steps
Recommended Tools
Timeline
Risks
Best Practices

ML PROJECT REQUIREMENTS:
- Include modern ML tools and frameworks (TensorFlow, PyTorch, Hugging Face, AutoML)
- For ML projects: include data pipeline, model selection, iteration loops
- Use realistic timelines (4-12 weeks for MVP, not 26 weeks)
- Mention ML-specific risks (overfitting, data leakage, concept drift)
- Include infrastructure needs (GPU, cloud services, MLOps)
- Provide specific, actionable technical details
- Ensure compliance with industry standards
- Focus on quality assurance and testing strategies
"""
        
        if persona == "ENGINEER":
            return base_prompt + """

ENGINEER FOCUS:
- Focus on technical implementation details
- Recommend specific libraries and frameworks
- Provide code examples in markdown code blocks with syntax highlighting
- Discuss architecture patterns and best practices
- Emphasize performance optimization
- Include testing strategies and debugging tips
- Use technical terminology and precise specifications
"""
        elif persona == "MANAGER":
            return base_prompt + """

MANAGER FOCUS:
- Focus on business outcomes and ROI
- Provide cost breakdowns in table format
- Emphasize risk management and mitigation strategies
- Include team coordination and timeline management
- Discuss resource allocation and vendor selection
- Highlight competitive advantages and market positioning
- Use clear, business-friendly language with financial metrics
"""
        else:
            return base_prompt + """

GENERAL FOCUS:
- Balance technical and business perspectives
- Provide comprehensive overview with practical insights
- Include both implementation and strategic considerations
- Offer scalable and maintainable solutions
- Address both immediate needs and long-term goals
- Use simple analogies and clear bullet points for complex concepts
"""
    
    def _create_user_prompt(self, user_query: str, context_text: str, conversation_history: str = "") -> str:
        """Create natural user prompt with context and conversation history"""
        history_section = f"\n\nPrevious Conversation:\n{conversation_history}" if conversation_history else ""
        context_section = f"\n\nRelevant Information:\n{context_text}" if context_text else ""
        
        return f"""
User Question: {user_query}{history_section}{context_section}

Please provide a helpful, specific answer based on the user's question, previous conversation context, and available information.

IMPORTANT: If the user asks about something mentioned in the previous conversation, reference those specific details directly."""
    
    def _execute_tool_logic(self, user_query: str) -> Optional[Dict]:
        """Execute tool logic with error handling"""
        try:
            user_query_lower = user_query.lower()
            
            if "risk score" in user_query_lower:
                return self.tools.calculate_risk_score(4, 5)
            elif "timeline" in user_query_lower:
                return self.tools.estimate_timeline("medium", 5)
            elif "document" in user_query_lower:
                return self.tools.generate_project_document(user_query)
            
            return None
        except Exception as e:
            logger.error(f"Tool execution error: {str(e)}")
            return None
    
    def _calculate_confidence(self, llm_response: str, retrieved_context: list) -> float:
        """Calculate confidence score based on response quality"""
        if not llm_response:
            return 0
        
        base_confidence = 75
        
        # Boost for retrieved context
        if retrieved_context:
            base_confidence += min(len(retrieved_context) * 5, 20)
        
        # Boost for response length
        if llm_response and len(llm_response) > 200:
            base_confidence += 10
        
        # Boost for structured content
        if llm_response and any(section in llm_response for section in ["Overview", "Technical", "Implementation"]):
            base_confidence += 10
        
        return min(base_confidence, 95)
    
    async def generate_prompt(self, user_query: str, session_id: str, conversation_id: str = None) -> Dict:
        """Enterprise-grade prompt generation with comprehensive features"""
        print(f"🔍 DEBUG: EnhancedPromptEngine.generate_prompt() called with query: {user_query}")
        start_time = time.time()
        
        try:
            # Apply guardrails
            user_query = self._apply_guardrails(user_query)
            
            # Detect and log persona
            persona = self._detect_user_persona(user_query)
            print(f"🔍 DEBUG: Detected persona: {persona}")
            logger.info(f"Detected user persona: {persona}")
            
            # Apply NLP analysis
            # nlp_analysis = self.nlp_processor.analyze_sdlc_phase(user_query)
            # print(f"🔍 DEBUG: NLP Analysis: {nlp_analysis}")
            # logger.info(f"NLP Analysis: {nlp_analysis}")
            nlp_analysis = {"sdlc_phase": "general", "technical_terms": [], "sentiment": "neutral", "complexity_score": 0.5}
            
            # Check cache first
            cache_key = f"{user_query}:{session_id}"
            if cache_key in self.response_cache:
                print("🔍 DEBUG: Cache hit!")
                return self.response_cache[cache_key]
            
            # Input validation
            validated_data = InputValidator.validate_query_params({
                'user_query': user_query,
                'session_id': session_id
            })
            
            user_query = validated_data['user_query']
            
            # Fetch conversation history for context
            conversation_history = ""
            if conversation_id:
                try:
                    # Get last 3 messages for context
                    messages = await db_manager.get_conversation_messages(conversation_id, limit=3)
                    if messages:
                        conversation_history = "\n".join([
                            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                            for msg in messages[-2:]  # Last 2 messages for context
                        ])
                        print(f"🔍 DEBUG: Retrieved conversation history: {len(conversation_history)} chars")
                except Exception as e:
                    logger.warning(f"Failed to fetch conversation history: {str(e)}")
            
            # Context retrieval with ranking
            context_start = time.time()
            try:
                from app.ai import vector_store
                retrieved_chunks = vector_store.search_similar(user_query, top_k=3)
                
                # Rank by score
                retrieved_chunks = sorted(
                    retrieved_chunks,
                    key=lambda x: x.get("score", 0),
                    reverse=True
                )
                
                context_retrieval_time = time.time() - context_start

                print(f"🔍 DEBUG: FAISS search completed. Retrieved {len(retrieved_chunks)} chunks")

                if retrieved_chunks:
                    retrieved_context = [
                        chunk['metadata']['content'] if 'content' in chunk['metadata']
                        else chunk['document']
                        for chunk in retrieved_chunks
                    ]
                    logger.info(f"Retrieved {len(retrieved_context)} context chunks in {context_retrieval_time:.2f}s")
                    print("🔍 DEBUG: Retrieved documents:")
                    for i, doc in enumerate(retrieved_context[:3]):
                        print(f"  Doc {i+1}: {doc[:100]}...")
                else:
                    retrieved_context = []
                    logger.warning("No context retrieved from FAISS")
                    print("🔍 DEBUG: No context retrieved from FAISS")
            except Exception as e:
                error_info = self.error_handler.handle_faiss_error(e)
                logger.error(f"FAISS retrieval failed: {error_info['message']}")
                retrieved_context = []
                context_retrieval_time = time.time() - context_start

            # Optimize prompt
            optimized_query = self._optimize_prompt(user_query)
            
            # Create prompts
            system_prompt = self._create_contextual_system_prompt(user_query)
            user_prompt = self._create_user_prompt(optimized_query, "\n".join(retrieved_context), conversation_history)
            
            # Debug logging
            logger.debug(f"System Prompt: {system_prompt}")
            logger.debug(f"User Prompt: {user_prompt}")
            
            # LLM call
            llm_start = time.time()
            try:
                llm_response, token_usage = await self.llm.generate_response_with_retry(
                    system_prompt, user_prompt
                )
                llm_time = time.time() - llm_start
                
                logger.info(f"LLM response generated in {llm_time:.2f}s")
                logger.info(f"Token usage: {token_usage}")
                print(f"🔍 DEBUG: Token usage: {token_usage}")
                
            except Exception as e:
                error_info = self.error_handler.handle_llm_error(e)
                logger.error(f"LLM generation failed: {error_info['message']}")
                llm_response = error_info['fallback_response']
                token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                llm_time = time.time() - llm_start

            # Calculate confidence
            confidence_score = self._calculate_confidence(llm_response, retrieved_context)
            
            # Calculate metrics
            total_time = time.time() - start_time
            metrics = {
                "context_chunks": len(retrieved_context),
                "token_usage": token_usage["total_tokens"],
                "latency": total_time,
                "context_retrieval_time": context_retrieval_time,
                "llm_generation_time": llm_time
            }
            
            # Create enterprise response
            result = {
                "success": True,
                "query": user_query,
                "llm_response": llm_response,
                "retrieved_context": retrieved_context,
                "confidence_score": confidence_score,
                "model_used": "Groq LLaMA3 + FAISS RAG + NLP",
                "token_usage": token_usage,
                "performance": {
                    "total_time": total_time,
                    "context_retrieval_time": context_retrieval_time,
                    "llm_generation_time": llm_time
                },
                "prompt_version": self.prompt_version,
                "cost_estimate": self._estimate_cost(token_usage["total_tokens"]),
                "metrics": metrics,
                "persona": persona,
                "nlp_analysis": nlp_analysis,
                "conversation_context": {
                    "history_length": len(conversation_history),
                    "context_chunks": len(retrieved_context)
                }
            }
            
            # Cache result
            self.response_cache[cache_key] = result
            
            self.performance_monitor.record_request_time(total_time)
            logger.info(f"Generated result with confidence: {confidence_score}")
            print(f"🔍 DEBUG: Generated result with confidence: {confidence_score}")
            
            return result
            
        except ValueError as e:
            # Handle validation errors
            logger.error(f"Validation error: {str(e)}")
            return {
                "success": False,
                "error": {
                    "error_type": "validation_error",
                    "message": str(e),
                    "user_message": str(e)
                }
            }
            
        except Exception as e:
            # Unexpected errors
            logger.error(f"Unexpected error in prompt generation: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            self.performance_monitor.record_error("unexpected_error")
            
            return {
                "success": False,
                "error": {
                    "error_type": "system_error",
                    "message": "System error occurred",
                    "user_message": "An unexpected error occurred. Please try again."
                },
                "fallback_response": self.error_handler._get_generic_fallback()
            }
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        return self.performance_monitor.get_performance_stats()
