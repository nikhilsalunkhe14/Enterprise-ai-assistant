from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import get_db
from models.conversation_schemas import (
    ConversationCreate, 
    ConversationResponse, 
    ConversationWithMessages,
    MessageCreate, 
    MessageResponse
)
from services.conversation_service import ConversationService
from services.jwt_service import get_current_user
from models.user import User
from datetime import timedelta

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new conversation"""
    conversation_service = ConversationService(db)
    db_conversation = conversation_service.create_conversation(
        user_id=current_user.id,
        conversation=conversation
    )
    
    return ConversationResponse(
        id=db_conversation.id,
        user_id=db_conversation.user_id,
        title=db_conversation.title,
        created_at=db_conversation.created_at,
        message_count=0
    )

@router.get("/", response_model=list[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for current user"""
    conversation_service = ConversationService(db)
    conversations = conversation_service.get_user_conversations(current_user.id)
    
    return [
        ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            created_at=conv.created_at,
            message_count=conv.message_count or 0
        )
        for conv in conversations
    ]

@router.get("/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation with all messages"""
    conversation_service = ConversationService(db)
    conversation = conversation_service.get_conversation_with_messages(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return ConversationWithMessages(
        id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        created_at=conversation.created_at,
        message_count=len(conversation.messages),
        messages=[
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at
            )
            for msg in conversation.messages
        ]
    )

@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: int,
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send message to conversation"""
    conversation_service = ConversationService(db)
    
    # Verify conversation belongs to user
    conversation = conversation_service.get_conversation_by_id(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Create message
    db_message = conversation_service.create_message(
        MessageCreate(
            conversation_id=conversation_id,
            role=message.role,
            content=message.content
        )
    )
    
    return MessageResponse(
        id=db_message.id,
        conversation_id=db_message.conversation_id,
        role=db_message.role,
        content=db_message.content,
        created_at=db_message.created_at
    )

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete conversation"""
    conversation_service = ConversationService(db)
    success = conversation_service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return {"message": "Conversation deleted successfully"}

@router.put("/{conversation_id}")
async def update_conversation_title(
    conversation_id: int,
    title_update: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update conversation title"""
    conversation_service = ConversationService(db)
    success = conversation_service.update_conversation_title(
        conversation_id=conversation_id,
        user_id=current_user.id,
        title=title_update.get("title", "")
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return {"message": "Conversation title updated successfully"}
