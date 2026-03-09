from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from services.jwt_service import get_current_user
from database.mongodb import (
    find_message_by_id, find_conversation_by_id, update_message, delete_message,
    delete_messages_after, find_messages_by_conversation, insert_message,
    track_usage
)
from app.services.enhanced_prompt_engine import EnhancedPromptEngine

router = APIRouter(prefix="/api/messages", tags=["messages"])

# Pydantic models
class MessageUpdate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    tokens: Optional[int] = None
    created_at: datetime

class RegenerateResponse(BaseModel):
    message: MessageResponse
    tokens_used: Optional[int] = None

@router.put("/{message_id}", response_model=MessageResponse)
async def update_message_endpoint(
    message_id: str,
    message_update: MessageUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Edit a message"""
    message = await find_message_by_id(message_id)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check if user owns the conversation
    conversation = await find_conversation_by_id(message["conversation_id"])
    if not conversation or conversation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Only allow editing user messages
    if message["role"] != "user":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only user messages can be edited"
        )
    
    # Update the message
    await update_message(message_id, {
        "content": message_update.content,
        "updated_at": datetime.utcnow()
    })
    
    # Delete all messages after this message (assistant responses)
    await delete_messages_after(message["conversation_id"], message_id)
    
    # Get the updated message
    updated_message = await find_message_by_id(message_id)
    
    return MessageResponse(
        id=str(updated_message["_id"]),
        conversation_id=updated_message["conversation_id"],
        role=updated_message["role"],
        content=updated_message["content"],
        tokens=updated_message.get("tokens"),
        created_at=updated_message["created_at"]
    )

@router.post("/{message_id}/regenerate", response_model=RegenerateResponse)
async def regenerate_message(
    message_id: str,
    model: str = "grok-1",
    current_user: dict = Depends(get_current_user)
):
    """Regenerate assistant response for a user message"""
    message = await find_message_by_id(message_id)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check if user owns the conversation
    conversation = await find_conversation_by_id(message["conversation_id"])
    if not conversation or conversation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Only allow regeneration for user messages
    if message["role"] != "user":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only regenerate response for user messages"
        )
    
    # Delete existing assistant messages after this user message
    await delete_messages_after(message["conversation_id"], message_id)
    
    # Get conversation history for context
    conversation_history = await find_messages_by_conversation(
        message["conversation_id"], 
        limit=10
    )
    
    # Generate new response
    enhanced_engine = EnhancedPromptEngine()
    
    # Build messages for AI
    ai_messages = []
    
    # Add system prompt
    system_prompt = """You are an expert AI assistant providing comprehensive, professional responses. 
    Format your responses with clear headings, detailed bullet points, and actionable insights. 
    Always provide thorough, well-organized answers that demonstrate deep expertise."""
    
    ai_messages.append({"role": "system", "content": system_prompt})
    
    # Add conversation history (excluding the current message which will be added separately)
    for msg in conversation_history:
        if msg["id"] != message_id:  # Skip the current message as we'll add it fresh
            ai_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    # Add the current user message
    ai_messages.append({
        "role": message["role"],
        "content": message["content"]
    })
    
    try:
        # Get AI response
        result = await enhanced_engine.generate_prompt(message["content"], "message_regeneration")
        ai_response = result.get("llm_response", "I apologize, but I'm unable to process your request at this time.")
        
        # Save new assistant message
        assistant_message_data = {
            "conversation_id": message["conversation_id"],
            "role": "assistant",
            "content": ai_response,
            "created_at": datetime.utcnow()
        }
        
        assistant_message_id = await insert_message(assistant_message_data)
        assistant_message = await find_message_by_id(assistant_message_id)
        
        # Track usage
        tokens_used = await grok_service.estimate_tokens(ai_response)
        await track_usage(current_user["id"], tokens_used)
        
        return RegenerateResponse(
            message=MessageResponse(
                id=str(assistant_message["_id"]),
                conversation_id=assistant_message["conversation_id"],
                role=assistant_message["role"],
                content=assistant_message["content"],
                tokens=assistant_message.get("tokens"),
                created_at=assistant_message["created_at"]
            ),
            tokens_used=tokens_used
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate response: {str(e)}"
        )

@router.delete("/{message_id}")
async def delete_message_endpoint(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a message and all subsequent messages"""
    message = await find_message_by_id(message_id)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check if user owns the conversation
    conversation = await find_conversation_by_id(message["conversation_id"])
    if not conversation or conversation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Delete this message and all subsequent messages
    await delete_messages_after(message["conversation_id"], message_id)
    
    return {"message": "Message deleted successfully"}

@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific message"""
    message = await find_message_by_id(message_id)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check if user owns the conversation
    conversation = await find_conversation_by_id(message["conversation_id"])
    if not conversation or conversation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return MessageResponse(
        id=str(message["_id"]),
        conversation_id=message["conversation_id"],
        role=message["role"],
        content=message["content"],
        tokens=message.get("tokens"),
        created_at=message["created_at"]
    )
