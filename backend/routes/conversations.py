from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from services.jwt_service import get_current_user
from database.mongodb import (
    insert_conversation, find_conversations_by_user, find_conversation_by_id,
    update_conversation, delete_conversation, search_conversations,
    pin_conversation, archive_conversation, find_messages_by_conversation,
    insert_message, track_usage
)
from app.services.enhanced_prompt_engine import EnhancedPromptEngine
import json

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

# Pydantic models
class ConversationCreate(BaseModel):
    title: Optional[str] = None

class ConversationUpdate(BaseModel):
    title: Optional[str] = None

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    is_archived: bool = False
    is_pinned: bool = False
    message_count: int = 0

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    tokens: Optional[int] = None
    created_at: datetime

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new conversation"""
    conversation_data = {
        "user_id": str(current_user["_id"]),
        "title": conversation.title or "New Chat",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_archived": False,
        "is_pinned": False
    }
    
    conversation_id = await insert_conversation(conversation_data)
    db_conversation = await find_conversation_by_id(conversation_id)
    
    return ConversationResponse(
        id=str(db_conversation["_id"]),
        user_id=db_conversation["user_id"],
        title=db_conversation["title"],
        created_at=db_conversation["created_at"],
        updated_at=db_conversation["updated_at"],
        is_archived=db_conversation.get("is_archived", False),
        is_pinned=db_conversation.get("is_pinned", False),
        message_count=0
    )

@router.get("", response_model=List[ConversationResponse])
async def get_conversations(
    include_archived: bool = Query(False, description="Include archived conversations"),
    current_user: dict = Depends(get_current_user)
):
    """Get all conversations for the current user"""
    conversations = await find_conversations_by_user(
        user_id=str(current_user["_id"]),
        include_archived=include_archived
    )
    
    result = []
    for conv in conversations:
        message_count = len(await find_messages_by_conversation(conv["id"], limit=1000))
        result.append(ConversationResponse(
            id=conv["id"],
            user_id=conv["user_id"],
            title=conv["title"],
            created_at=conv["created_at"],
            updated_at=conv["updated_at"],
            is_archived=conv.get("is_archived", False),
            is_pinned=conv.get("is_pinned", False),
            message_count=message_count
        ))
    
    return result

@router.get("/search", response_model=List[ConversationResponse])
async def search_conversations_endpoint(
    q: str = Query(..., min_length=1, description="Search query"),
    current_user: dict = Depends(get_current_user)
):
    """Search conversations by title"""
    conversations = await search_conversations(
        user_id=str(current_user["_id"]),
        search_query=q
    )
    
    result = []
    for conv in conversations:
        message_count = len(await find_messages_by_conversation(conv["id"], limit=1000))
        result.append(ConversationResponse(
            id=conv["id"],
            user_id=conv["user_id"],
            title=conv["title"],
            created_at=conv["created_at"],
            updated_at=conv["updated_at"],
            is_archived=conv.get("is_archived", False),
            is_pinned=conv.get("is_pinned", False),
            message_count=message_count
        ))
    
    return result

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific conversation"""
    conversation = await find_conversation_by_id(conversation_id)
    
    if not conversation or conversation["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    message_count = len(await find_messages_by_conversation(conversation_id, limit=1000))
    
    return ConversationResponse(
        id=str(conversation["_id"]),
        user_id=conversation["user_id"],
        title=conversation["title"],
        created_at=conversation["created_at"],
        updated_at=conversation["updated_at"],
        is_archived=conversation.get("is_archived", False),
        is_pinned=conversation.get("is_pinned", False),
        message_count=message_count
    )

@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation_endpoint(
    conversation_id: str,
    conversation_update: ConversationUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update conversation title"""
    conversation = await find_conversation_by_id(conversation_id)
    
    if not conversation or conversation["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    update_data = {"updated_at": datetime.utcnow()}
    if conversation_update.title:
        update_data["title"] = conversation_update.title
    
    await update_conversation(conversation_id, update_data)
    updated_conversation = await find_conversation_by_id(conversation_id)
    
    message_count = len(await find_messages_by_conversation(conversation_id, limit=1000))
    
    return ConversationResponse(
        id=str(updated_conversation["_id"]),
        user_id=updated_conversation["user_id"],
        title=updated_conversation["title"],
        created_at=updated_conversation["created_at"],
        updated_at=updated_conversation["updated_at"],
        is_archived=updated_conversation.get("is_archived", False),
        is_pinned=updated_conversation.get("is_pinned", False),
        message_count=message_count
    )

@router.post("/{conversation_id}/pin")
async def pin_conversation_endpoint(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Pin or unpin a conversation"""
    conversation = await find_conversation_by_id(conversation_id)
    
    if not conversation or conversation["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    is_pinned = not conversation.get("is_pinned", False)
    await pin_conversation(conversation_id, is_pinned)
    
    return {"message": f"Conversation {'pinned' if is_pinned else 'unpinned'} successfully"}

@router.post("/{conversation_id}/archive")
async def archive_conversation_endpoint(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Archive or unarchive a conversation"""
    conversation = await find_conversation_by_id(conversation_id)
    
    if not conversation or conversation["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    is_archived = not conversation.get("is_archived", False)
    await archive_conversation(conversation_id, is_archived)
    
    return {"message": f"Conversation {'archived' if is_archived else 'unarchived'} successfully"}

@router.delete("/{conversation_id}")
async def delete_conversation_endpoint(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a conversation"""
    conversation = await find_conversation_by_id(conversation_id)
    
    if not conversation or conversation["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    await delete_conversation(conversation_id)
    
    return {"message": "Conversation deleted successfully"}

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all messages in a conversation"""
    conversation = await find_conversation_by_id(conversation_id)
    
    if not conversation or conversation["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = await find_messages_by_conversation(conversation_id)
    
    return [
        MessageResponse(
            id=msg["id"],
            conversation_id=msg["conversation_id"],
            role=msg["role"],
            content=msg["content"],
            tokens=msg.get("tokens"),
            created_at=msg["created_at"]
        )
        for msg in messages
    ]

@router.post("/{conversation_id}/generate-title")
async def generate_conversation_title(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Auto-generate conversation title using AI"""
    conversation = await find_conversation_by_id(conversation_id)
    
    if not conversation or conversation["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = await find_messages_by_conversation(conversation_id, limit=3)
    
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages found to generate title"
        )
    
    # Get first user message for title generation
    first_user_message = None
    for msg in messages:
        if msg["role"] == "user":
            first_user_message = msg["content"]
            break
    
    if not first_user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user message found"
        )
    
    # Generate title using AI
    enhanced_engine = EnhancedPromptEngine()
    title_prompt = f"""Generate a short, descriptive title (max 50 characters) for a conversation that starts with: "{first_user_message[:200]}..."
    
    Rules:
    - Maximum 50 characters
    - No quotes
    - Descriptive and clear
    - Use title case
    - Be concise but informative
    
    Title:"""
    
    try:
        result = await enhanced_engine.generate_prompt(title_prompt, "title_generation")
        ai_response = result.get("llm_response", "New Chat")
        
        # Clean up the title
        title = ai_response.strip().strip('"').strip("'").strip()
        if len(title) > 50:
            title = title[:47] + "..."
        
        # Update conversation title
        await update_conversation(conversation_id, {
            "title": title,
            "updated_at": datetime.utcnow()
        })
        
        return {"title": title}
        
    except Exception as e:
        # Fallback to truncated first message
        fallback_title = first_user_message[:47] + "..." if len(first_user_message) > 50 else first_user_message
        await update_conversation(conversation_id, {
            "title": fallback_title,
            "updated_at": datetime.utcnow()
        })
        
        return {"title": fallback_title}

@router.get("/export")
async def export_all_conversations(
    format: str = Query("json", regex="^(json|markdown|txt)$"),
    current_user: dict = Depends(get_current_user)
):
    """Export all conversations in different formats"""
    
    # Get all conversations for current user
    conversations = await find_conversations_by_user(str(current_user["_id"]))
    
    if format == "json":
        export_data = {
            "conversations": conversations,
            "export_date": datetime.utcnow().isoformat(),
            "total_conversations": len(conversations)
        }
        
        return JSONResponse(
            content=export_data,
            headers={"Content-Disposition": "attachment; filename=conversations.json"}
        )
    
    elif format == "markdown":
        markdown_content = "# All Conversations\n\n"
        markdown_content += f"**Export Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"
        markdown_content += f"**Total Conversations:** {len(conversations)}\n\n"
        markdown_content += "---\n\n"
        
        for conv in conversations:
            markdown_content += f"# {conv['title']}\n\n"
            markdown_content += f"**Created:** {conv['created_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            markdown_content += f"**Last Updated:** {conv['updated_at'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # Get messages for this conversation
            messages = await find_messages_by_conversation(conv["id"])
            for msg in messages:
                if msg["role"] == "user":
                    markdown_content += f"## 👤 User\n{msg['content']}\n\n"
                else:
                    markdown_content += f"## 🤖 Assistant\n{msg['content']}\n\n"
            
            markdown_content += "---\n\n"
        
        return PlainTextResponse(
            content=markdown_content,
            headers={"Content-Disposition": "attachment; filename=conversations.md"}
        )
    
    else:
        # TXT format
        txt_content = "All Conversations\n\n"
        txt_content += f"Export Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"
        txt_content += f"Total Conversations: {len(conversations)}\n\n"
        txt_content += "---\n\n"
        
        for conv in conversations:
            txt_content += f"Conversation: {conv['title']}\n"
            txt_content += f"Created: {conv['created_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            txt_content += f"Last Updated: {conv['updated_at'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # Get messages for this conversation
            messages = await find_messages_by_conversation(conv["id"])
            for msg in messages:
                role_label = "USER" if msg["role"] == "user" else "ASSISTANT"
                txt_content += f"[{role_label}] {msg['created_at'].strftime('%H:%M:%S')}\n"
                txt_content += f"{msg['content']}\n\n"
            
            txt_content += "---\n\n"
        
        return PlainTextResponse(
            content=txt_content,
            headers={"Content-Disposition": "attachment; filename=conversations.txt"}
        )

@router.get("/{conversation_id}/export")
async def export_conversation(
    conversation_id: str,
    format: str = Query("json", regex="^(json|markdown|txt)$"),
    current_user: dict = Depends(get_current_user)
):
    """Export conversation in different formats"""
    conversation = await find_conversation_by_id(conversation_id)
    
    if not conversation or conversation["user_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = await find_messages_by_conversation(conversation_id)
    
    if format == "json":
        export_data = {
            "conversation": {
                "id": conversation["id"],
                "title": conversation["title"],
                "created_at": conversation["created_at"].isoformat(),
                "updated_at": conversation["updated_at"].isoformat()
            },
            "messages": [
                {
                    "role": msg["role"],
                    "content": msg["content"],
                    "created_at": msg["created_at"].isoformat()
                }
                for msg in messages
            ]
        }
        
        return JSONResponse(
            content=export_data,
            headers={"Content-Disposition": f"attachment; filename={conversation['title']}.json"}
        )
    
    elif format == "markdown":
        markdown_content = f"# {conversation['title']}\n\n"
        markdown_content += f"**Created:** {conversation['created_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
        markdown_content += f"**Last Updated:** {conversation['updated_at'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        markdown_content += "---\n\n"
        
        for msg in messages:
            if msg["role"] == "user":
                markdown_content += f"## 👤 User\n{msg['content']}\n\n"
            else:
                markdown_content += f"## 🤖 Assistant\n{msg['content']}\n\n"
        
        return PlainTextResponse(
            content=markdown_content,
            headers={
                "Content-Disposition": f"attachment; filename={conversation['title']}.md",
                "Content-Type": "text/markdown"
            }
        )
    
    else:  # txt format
        txt_content = f"Conversation: {conversation['title']}\n"
        txt_content += f"Created: {conversation['created_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
        txt_content += f"Last Updated: {conversation['updated_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
        txt_content += "=" * 50 + "\n\n"
        
        for msg in messages:
            role_label = "USER" if msg["role"] == "user" else "ASSISTANT"
            txt_content += f"[{role_label}] {msg['created_at'].strftime('%H:%M:%S')}\n"
            txt_content += f"{msg['content']}\n\n"
        
        return PlainTextResponse(
            content=txt_content,
            headers={
                "Content-Disposition": f"attachment; filename={conversation['title']}.txt",
                "Content-Type": "text/plain"
            }
        )

@router.get("/export")
async def export_all_conversations(
    format: str = Query("json", regex="^(json|markdown|txt)$"),
    current_user: dict = Depends(get_current_user)
):
    """Export all conversations in different formats"""
    
    # Get all conversations for current user
    conversations = await find_conversations_by_user(str(current_user["_id"]))
    
    if format == "json":
        export_data = {
            "conversations": conversations,
            "export_date": datetime.utcnow().isoformat(),
            "total_conversations": len(conversations)
        }
        
        return JSONResponse(
            content=export_data,
            headers={"Content-Disposition": "attachment; filename=conversations.json"}
        )
    
    elif format == "markdown":
        markdown_content = "# All Conversations\n\n"
        markdown_content += f"**Export Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"
        markdown_content += f"**Total Conversations:** {len(conversations)}\n\n"
        markdown_content += "---\n\n"
        
        for conv in conversations:
            markdown_content += f"# {conv['title']}\n\n"
            markdown_content += f"**Created:** {conv['created_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            markdown_content += f"**Last Updated:** {conv['updated_at'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # Get messages for this conversation
            messages = await find_messages_by_conversation(conv["id"])
            for msg in messages:
                if msg["role"] == "user":
                    markdown_content += f"## 👤 User\n{msg['content']}\n\n"
                else:
                    markdown_content += f"## 🤖 Assistant\n{msg['content']}\n\n"
            
            markdown_content += "---\n\n"
        
        return PlainTextResponse(
            content=markdown_content,
            headers={"Content-Disposition": "attachment; filename=conversations.md"}
        )
    
    else:
        # TXT format
        txt_content = "All Conversations\n\n"
        txt_content += f"Export Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"
        txt_content += f"Total Conversations: {len(conversations)}\n\n"
        txt_content += "---\n\n"
        
        for conv in conversations:
            txt_content += f"Conversation: {conv['title']}\n"
            txt_content += f"Created: {conv['created_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            txt_content += f"Last Updated: {conv['updated_at'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # Get messages for this conversation
            messages = await find_messages_by_conversation(conv["id"])
            for msg in messages:
                role_label = "USER" if msg["role"] == "user" else "ASSISTANT"
                txt_content += f"[{role_label}] {msg['created_at'].strftime('%H:%M:%S')}\n"
                txt_content += f"{msg['content']}\n\n"
            
            txt_content += "---\n\n"
        
        return PlainTextResponse(
            content=txt_content,
            headers={"Content-Disposition": "attachment; filename=conversations.txt"}
        )
