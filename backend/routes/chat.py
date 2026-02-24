from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import json
from datetime import datetime
from services.jwt_service import get_current_user
from models.user import User
from database.connection import get_db

# AI Models Configuration
AI_MODELS = {
    "llama-3-8b": {
        "name": "LLaMA 3 8B",
        "description": "Meta's LLaMA 3 model",
        "max_tokens": 8192,
        "provider": "huggingface"
    },
    "mistral-7b": {
        "name": "Mistral 7B",
        "description": "Mistral AI's 7B model",
        "max_tokens": 32768,
        "provider": "huggingface"
    },
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "description": "OpenAI's GPT-3.5 Turbo model",
        "max_tokens": 4096,
        "provider": "openai"
    }
}

class ChatRequest(BaseModel):
    message: str
    conversation_id: int
    model: str = "llama-3-8b"

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
    """Chat with AI model"""
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
        
        # Get model configuration
        model_config = AI_MODELS.get(request.model, AI_MODELS["llama-3-8b"])
        
        # Simulate AI response (in production, integrate with real AI)
        ai_response = await simulate_ai_response(
            message=request.message,
            model=request.model,
            conversation_history=get_conversation_history(db, request.conversation_id)
        )
        
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
        
        return ChatResponse(
            response=ai_response,
            model_used=request.model,
            tokens_used=len(ai_response.split()),  # Rough estimate
            response_time=response_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI chat error: {str(e)}"
        )

async def simulate_ai_response(message: str, model: str, conversation_history: List) -> str:
    """Simulate AI response (replace with real AI integration)"""
    
    # Simple response generation based on message content
    if "hello" in message.lower() or "hi" in message.lower():
        return f"Hello! I'm {AI_MODELS[model]['name']}. How can I help you today?"
    
    elif "how are you" in message.lower():
        return f"I'm doing well! I'm {AI_MODELS[model]['name']}, ready to assist you with any questions or tasks you have."
    
    elif "what can you do" in message.lower():
        return f"As {AI_MODELS[model]['name']}, I can help you with:\n\n• Answer questions and provide information\n• Help with coding and technical problems\n• Assist with writing and editing\n• Analyze data and documents\n• Provide recommendations and advice\n\nWhat would you like help with?"
    
    elif "code" in message.lower() or "programming" in message.lower():
        return f"I'd be happy to help you with coding! As {AI_MODELS[model]['name']}, I can assist with:\n\n• Writing and debugging code\n• Explaining programming concepts\n• Code optimization\n• Multiple programming languages\n• Best practices and patterns\n\nWhat programming task can I help you with?"
    
    else:
        # Contextual response
        if conversation_history:
            last_user_msg = conversation_history[-2]["content"] if len(conversation_history) >= 2 else message
            return f"I understand you're asking about: '{last_user_msg}'. Let me provide a helpful response using {AI_MODELS[model]['name']}.\n\nThis is a simulated response. In production, this would be connected to the actual {model} model via Sentence Transformers or OpenAI API to provide intelligent, context-aware responses."
        else:
            return f"Thank you for your message: '{message}'. I'm {AI_MODELS[model]['name']}, and I'm here to help! This is a simulated response that would be replaced with actual AI model integration in production."

def get_conversation_history(db: Session, conversation_id: int, limit: int = 5) -> List:
    """Get recent conversation history for context"""
    try:
        from services.conversation_service import ConversationService
        conversation_service = ConversationService(db)
        conversation = conversation_service.get_conversation_with_messages(conversation_id, 0)  # user_id=0 for this function
        
        if conversation and conversation.messages:
            return [{"role": msg.role, "content": msg.content} for msg in conversation.messages[-limit:]]
        return []
    except:
        return []

async def create_message_in_db(db: Session, conversation_id: int, role: str, content: str):
    """Create message in database"""
    try:
        from services.conversation_service import ConversationService
        from models.conversation_schemas import MessageCreate
        conversation_service = ConversationService(db)
        
        message_data = MessageCreate(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        
        return conversation_service.create_message(message_data)
    except Exception as e:
        print(f"Error creating message: {e}")
        return None
