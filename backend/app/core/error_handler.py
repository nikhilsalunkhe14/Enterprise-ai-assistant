import traceback
from typing import Dict, Any, Optional
from app.core.logger import logger
from app.core.config import settings

class ErrorHandler:
    @staticmethod
    def handle_groq_error(error: Exception) -> Dict[str, Any]:
        """Handle Groq API specific errors"""
        error_str = str(error).lower()
        
        if "invalid api key" in error_str:
            logger.critical("Invalid Groq API key")
            return {
                "error_type": "authentication_error",
                "message": "AI service authentication failed. Please contact administrator.",
                "user_message": "AI service is temporarily unavailable. Please try again later.",
                "retry_allowed": False
            }
        
        elif "rate limit" in error_str or "too many requests" in error_str:
            logger.warning("Groq rate limit exceeded")
            return {
                "error_type": "rate_limit_error",
                "message": "AI service rate limit exceeded",
                "user_message": "Too many requests. Please wait a moment and try again.",
                "retry_allowed": True,
                "retry_after": 60
            }
        
        elif "timeout" in error_str:
            logger.error("Groq API timeout")
            return {
                "error_type": "timeout_error",
                "message": "AI service timeout",
                "user_message": "AI service is taking too long to respond. Please try again.",
                "retry_allowed": True
            }
        
        elif "model" in error_str and "not found" in error_str:
            logger.error(f"Groq model not available: {error_str}")
            return {
                "error_type": "model_error",
                "message": "AI model not available",
                "user_message": "AI service is currently using a different model. Please try again.",
                "retry_allowed": True
            }
        
        else:
            logger.error(f"Unknown Groq error: {error_str}")
            return {
                "error_type": "unknown_error",
                "message": f"Groq API error: {str(error)}",
                "user_message": "AI service encountered an error. Please try again later.",
                "retry_allowed": True
            }
    
    @staticmethod
    def handle_faiss_error(error: Exception) -> Dict[str, Any]:
        """Handle FAISS vector store errors"""
        error_str = str(error).lower()
        
        if "index" in error_str and "not found" in error_str:
            logger.error("FAISS index not found")
            return {
                "error_type": "index_error",
                "message": "Vector store not initialized",
                "user_message": "Knowledge base is loading. Please try again in a moment.",
                "retry_allowed": True
            }
        
        elif "dimension" in error_str:
            logger.error(f"FAISS dimension mismatch: {error_str}")
            return {
                "error_type": "dimension_error",
                "message": "Vector dimension mismatch",
                "user_message": "AI service is reconfiguring. Please try again.",
                "retry_allowed": True
            }
        
        else:
            logger.error(f"FAISS error: {error_str}")
            return {
                "error_type": "vector_error",
                "message": f"Vector store error: {str(error)}",
                "user_message": "Knowledge base encountered an error. Using fallback mode.",
                "retry_allowed": False
            }
    
    @staticmethod
    def handle_tool_error(error: Exception, tool_name: str) -> Dict[str, Any]:
        """Handle tool execution errors"""
        logger.error(f"Tool {tool_name} error: {str(error)}")
        
        return {
            "error_type": "tool_error",
            "tool_name": tool_name,
            "message": f"Tool execution failed: {str(error)}",
            "user_message": f"Tool '{tool_name}' encountered an error. Continuing with AI response.",
            "retry_allowed": False
        }
    
    @staticmethod
    def handle_database_error(error: Exception) -> Dict[str, Any]:
        """Handle database errors"""
        error_str = str(error).lower()
        
        if "connection" in error_str:
            logger.critical("Database connection failed")
            return {
                "error_type": "database_connection_error",
                "message": "Database connection failed",
                "user_message": "Service is experiencing database issues. Some features may be limited.",
                "retry_allowed": True
            }
        
        elif "lock" in error_str:
            logger.warning("Database lock error")
            return {
                "error_type": "database_lock_error",
                "message": "Database lock timeout",
                "user_message": "Service is busy. Please try again.",
                "retry_allowed": True
            }
        
        else:
            logger.error(f"Database error: {error_str}")
            return {
                "error_type": "database_error",
                "message": f"Database error: {str(error)}",
                "user_message": "Service encountered a database error. Some features may be limited.",
                "retry_allowed": False
            }
    
    @staticmethod
    def create_error_response(error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "success": False,
            "error": error_info,
            "timestamp": logger.handlers[0].formatter.formatTime(logger.makeRecord(
                "", 0, "", 0, "", (), None
            )) if logger.handlers else None,
            "fallback_response": ErrorHandler._get_generic_fallback()
        }
    
    @staticmethod
    def _get_generic_fallback() -> str:
        """Generic fallback response"""
        return """I apologize, but I'm currently experiencing technical difficulties. 

**Overview**
Your request has been received but cannot be processed at this time.

**Planning**
- Please review your query and try again
- Consider if your question can be rephrased

**Execution**
- Wait a moment before retrying
- Check if the issue persists

**Risk Management**
- Service unavailability is temporary
- Have backup processes ready

**Deliverables**
- Your original query will be processed when service is restored

**Success Metrics**
- Service restoration time
- Query processing completion

Please try again in a few minutes."""

class PerformanceMonitor:
    def __init__(self):
        self.request_times = []
        self.error_counts = {}
        self.memory_usage = []
    
    def record_request_time(self, duration: float):
        """Record request duration"""
        self.request_times.append(duration)
        # Keep only last 1000 requests
        if len(self.request_times) > 1000:
            self.request_times = self.request_times[-1000:]
    
    def record_error(self, error_type: str):
        """Record error occurrence"""
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.request_times:
            return {"avg_response_time": 0, "max_response_time": 0, "min_response_time": 0}
        
        return {
            "avg_response_time": sum(self.request_times) / len(self.request_times),
            "max_response_time": max(self.request_times),
            "min_response_time": min(self.request_times),
            "total_requests": len(self.request_times),
            "error_counts": self.error_counts.copy()
        }
