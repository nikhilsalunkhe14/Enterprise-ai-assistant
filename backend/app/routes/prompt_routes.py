from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.models.request_models import PromptRequest
from app.services.enhanced_prompt_engine import EnhancedPromptEngine  # Use Enhanced version
from app.core.logger import logger

router = APIRouter()
prompt_engine = EnhancedPromptEngine()  # Use Enhanced version
limiter = Limiter(key_func=get_remote_address)

@router.post("/generate-prompt")
@limiter.limit("60/minute")
async def generate_prompt(request: Request, prompt_request: PromptRequest):
    """Generate structured prompt based on user query with session context"""
    try:
        logger.info(f"Received request: session_id={prompt_request.session_id}, user_query='{prompt_request.user_query[:50]}...'")
        
        # Use async version for better concurrency
        result = await prompt_engine.generate_prompt(prompt_request.user_query, prompt_request.session_id, prompt_request.session_id)
        
        # Transform response to match frontend expectations
        response = {
            "content": result.get("llm_response", ""),
            "model": result.get('model_used', 'Enhanced LLM + FAISS RAG'),
            "confidence": result.get('confidence_score', 0),
            "context_chunks": len(result.get('retrieved_context', [])),
            "tokens": result.get('token_usage', {}).get('total_tokens', 0),
            "response_time": result.get('performance', {}).get('total_time', 0),
            "success": result.get('success', False)
        }
        
        logger.info(f"Generated result with confidence: {response['confidence']}")
        return response
    
    except Exception as e:
        logger.error(f"Error in generate_prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/debug")
async def debug_endpoint():
    """Debug endpoint to check system status"""
    return {
        "status": "debug",
        "message": "System is running",
        "available_domains": list(prompt_engine.domain_keywords.keys()),
        "available_stages": list(prompt_engine.stage_keywords.keys()),
        "vector_store": vector_store.get_stats()
    }

@router.post("/search-rag")
async def search_rag(query: str = "project management", top_k: int = 3):
    """Test RAG search functionality"""
    try:
        results = vector_store.search_similar(query, top_k)
        return {
            "query": query,
            "results": results,
            "total_found": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG search error: {str(e)}")
