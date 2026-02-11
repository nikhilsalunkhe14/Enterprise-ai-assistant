import time
import asyncio
from typing import Dict, Optional
from app.database import db_manager
from app.ai.enhanced_llm_service import EnhancedLLMService
from app.tools.tool_service import ToolService
from app.core.logger import logger
from app.core.security import InputValidator
from app.core.error_handler import ErrorHandler, PerformanceMonitor

class EnhancedPromptEngine:
    def __init__(self):
        self.llm = EnhancedLLMService()
        self.tools = ToolService()
        self.performance_monitor = PerformanceMonitor()
        self.error_handler = ErrorHandler()
        
    async def generate_prompt(self, user_query: str, session_id: str) -> Dict:
        """Enhanced prompt generation with comprehensive error handling"""
        start_time = time.time()
        
        try:
            # Input validation
            validated_data = InputValidator.validate_query_params({
                'user_query': user_query,
                'session_id': session_id
            })
            
            user_query = validated_data['user_query']
            session_id = validated_data['session_id']
            
            logger.info(f"Processing query for session: {session_id}")
            
            # Step 1: Retrieve relevant context from FAISS with error handling
            retrieved_context = []
            context_retrieval_time = 0
            
            try:
                from app.ai import vector_store
                context_start = time.time()
                retrieved_chunks = vector_store.search_similar(user_query, top_k=3)
                context_retrieval_time = time.time() - context_start
                
                if retrieved_chunks:
                    retrieved_context = [
                        chunk['metadata']['content'] if 'content' in chunk['metadata']
                        else chunk['document']
                        for chunk in retrieved_chunks
                    ]
                    logger.info(f"Retrieved {len(retrieved_context)} context chunks in {context_retrieval_time:.2f}s")
                else:
                    logger.warning("No context retrieved from FAISS")
                    
            except Exception as e:
                error_info = self.error_handler.handle_faiss_error(e)
                logger.error(f"FAISS retrieval failed: {error_info['message']}")
                # Continue without context
            
            context_text = "\n\n".join(retrieved_context) if retrieved_context else ""
            
            # Step 2: Define system prompt
            system_prompt = self._create_system_prompt()
            
            # Step 3: Create user prompt
            user_prompt = self._create_user_prompt(user_query, context_text)
            
            # Step 4: Call Groq LLM with enhanced error handling
            llm_response = ""
            llm_generation_time = 0
            
            try:
                llm_start = time.time()
                llm_response = await self.llm.generate_response(system_prompt, user_prompt)
                llm_generation_time = time.time() - llm_start
                logger.info(f"LLM response generated in {llm_generation_time:.2f}s")
                
            except Exception as e:
                error_info = self.error_handler.handle_groq_error(e)
                logger.error(f"LLM generation failed: {error_info['message']}")
                llm_response = error_info.get('fallback_response', self.error_handler._get_generic_fallback())
            
            # Step 5: Tool execution with error handling
            tool_output = None
            tool_execution_time = 0
            
            try:
                tool_start = time.time()
                tool_output = self._execute_tool_logic(user_query)
                tool_execution_time = time.time() - tool_start
                
                if tool_output:
                    logger.info(f"Tool executed in {tool_execution_time:.2f}s")
                    
            except Exception as e:
                error_info = self.error_handler.handle_tool_error(e, "unknown")
                logger.error(f"Tool execution failed: {error_info['message']}")
                tool_output = None
            
            # Step 6: Confidence calculation
            confidence_score = self._calculate_confidence(retrieved_context, llm_response)
            
            # Step 7: Save to DB with error handling
            try:
                db_manager.save_conversation(
                    session_id=session_id,
                    user_query=user_query,
                    detected_domain="RAG + LLM",
                    detected_stage="context-aware",
                    confidence_score=confidence_score
                )
            except Exception as e:
                error_info = self.error_handler.handle_database_error(e)
                logger.error(f"Database save failed: {error_info['message']}")
                # Continue without saving
            
            # Step 8: Performance monitoring
            total_time = time.time() - start_time
            self.performance_monitor.record_request_time(total_time)
            
            logger.info(f"Total request time: {total_time:.2f}s (Context: {context_retrieval_time:.2f}s, LLM: {llm_generation_time:.2f}s, Tools: {tool_execution_time:.2f}s)")
            
            return {
                "success": True,
                "user_query": user_query,
                "retrieved_context": retrieved_context,
                "llm_response": llm_response,
                "tool_output": tool_output,
                "confidence_score": confidence_score,
                "model_used": "Groq LLaMA3 + FAISS RAG + Tool Agent",
                "performance": {
                    "total_time": total_time,
                    "context_time": context_retrieval_time,
                    "llm_time": llm_generation_time,
                    "tool_time": tool_execution_time
                }
            }
            
        except ValueError as e:
            # Input validation errors
            logger.error(f"Input validation error: {str(e)}")
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
    
    def _create_system_prompt(self) -> str:
        """Create system prompt"""
        return """
You are an AI IT Project Delivery Assistant.
Use the provided IT standards context to generate structured, professional guidance.

Always respond in this structured format:
- Overview
- Planning
- Execution
- Risk Management
- Deliverables
- Success Metrics
"""
    
    def _create_user_prompt(self, user_query: str, context_text: str) -> str:
        """Create user prompt with context"""
        context_section = f"""
Relevant IT Standards Context:
{context_text}

""" if context_text else "No specific context available.\n\n"
        
        return f"""
User Query:
{user_query}

{context_section}Generate a professional structured response.
"""
    
    def _execute_tool_logic(self, user_query: str) -> Optional[Dict]:
        """Execute tool logic with error handling"""
        try:
            user_query_lower = user_query.lower()
            
            if "risk score" in user_query_lower:
                return self.tools.calculate_risk_score(4, 5)
            elif "timeline" in user_query_lower:
                return self.tools.estimate_timeline("medium", 5)
            elif "generate project document" in user_query_lower:
                return self.tools.generate_project_document("AI Project")
            
            return None
            
        except Exception as e:
            logger.error(f"Tool logic error: {str(e)}")
            raise e
    
    def _calculate_confidence(self, retrieved_context: list, llm_response: str) -> int:
        """Calculate confidence score"""
        base_confidence = 60
        
        # Boost for retrieved context
        if retrieved_context:
            base_confidence += min(len(retrieved_context) * 5, 20)
        
        # Boost for response length
        if llm_response and len(llm_response) > 200:
            base_confidence += 10
        
        # Boost for structured content
        if llm_response and any(section in llm_response for section in ["Overview", "Planning", "Execution"]):
            base_confidence += 10
        
        return min(base_confidence, 95)
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        return self.performance_monitor.get_performance_stats()
