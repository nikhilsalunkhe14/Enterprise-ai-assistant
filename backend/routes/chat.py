from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import json
from datetime import datetime
from services.jwt_service import get_current_user
from models.user import User
from database.connection import get_db
from services.conversation_service import ConversationService
# Import enhanced AI service instead of MockGrokService
from app.services.enhanced_prompt_engine import EnhancedPromptEngine

# AI Models Configuration - Using Enhanced AI
AI_MODELS = ["grok-1", "llama3-70b", "mixtral-8x7b"]

class ChatRequest(BaseModel):
    message: str
    conversation_id: str
    model: str = "grok-1"

class ChatResponse(BaseModel):
    response: str
    model_used: str
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None

class ModelInfo(BaseModel):
    id: str
    name: str
    description: str
    max_tokens: int
    provider: str

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.get("/models", response_model=List[ModelInfo])
async def get_available_models():
    """Get available AI models"""
    return [
        ModelInfo(
            id=model_id,
            **model_config
        )
        for model_id, model_config in AI_MODELS.items()
    ]

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with AI model using Grok"""
    print(f"🤖 Chat request: {request}")
    print(f"👤 User: {current_user.id} - {current_user.email}")
    start_time = datetime.now()
    
    try:
        # Verify conversation belongs to user
        conversation_service = ConversationService(db)
        conversation = conversation_service.get_conversation_by_id(
            conversation_id=request.conversation_id,
            user_id=current_user.id
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get Enhanced AI response
        enhanced_engine = EnhancedPromptEngine()
        ai_response = await get_enhanced_response(
            enhanced_engine=enhanced_engine,
            message=request.message,
            model=request.model,
            conversation_history=get_conversation_history(db, request.conversation_id)
        )
        
        print(f"🤖 AI response received")
        
        # Save user message
        user_message = await create_message_in_db(
            db=db,
            conversation_id=request.conversation_id,
            role="user",
            content=request.message
        )
        
        # Save AI response
        ai_message = await create_message_in_db(
            db=db,
            conversation_id=request.conversation_id,
            role="assistant",
            content=ai_response
        )
        
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        # Estimate tokens used (simple approximation)
        tokens_used = int(len(ai_response.split()) * 1.3)  # Rough token estimate
        
        return ChatResponse(
            response=ai_response,
            model_used=request.model,
            tokens_used=tokens_used,
            response_time=response_time
        )
        
    except Exception as e:
        print(f"❌ Chat error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI chat error: {str(e)}"
        )

async def get_enhanced_response(enhanced_engine: EnhancedPromptEngine, message: str, model: str, conversation_history: List) -> str:
    """Get AI response from EnhancedPromptEngine"""
    
    try:
        # Use enhanced prompt engine
        result = await enhanced_engine.generate_prompt(message, "session_id")
        return result.get("llm_response", "I apologize, but I'm unable to process your request at this time.")
    except Exception as e:
        print(f"Error in enhanced response: {e}")
        return "I apologize, but I'm unable to process your request at this time."

def get_conversation_history(db: Session, conversation_id: str, limit: int = 5) -> List:
    """Get recent conversation history for context (No longer uses Session)"""
    # This is a synchronous wrap for an async function, ideally refactored to fully async flow
    return []

async def create_message_in_db(db: Session, conversation_id: str, role: str, content: str):
    """Create message in database using MongoDB directly"""
    try:
        from database.mongodb import insert_message
        
        message_data = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "created_at": datetime.utcnow()
        }
        
        return await insert_message(message_data)
    except Exception as e:
        print(f"Error creating message: {e}")
        return None
