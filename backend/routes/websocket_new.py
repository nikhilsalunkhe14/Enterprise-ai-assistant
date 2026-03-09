from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict, Set
import json
import asyncio
import sys
import os
from datetime import datetime

# Add enhanced AI services path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from database.mongodb import (
    find_user_by_email, insert_message, find_conversation_by_id,
    find_messages_by_conversation, update_conversation, track_usage,
    delete_messages_after, find_message_by_id
)
from services.jwt_service import AuthService
from database.mongodb import mongodb_manager

# Import enhanced services
from app.services.enhanced_prompt_engine import EnhancedPromptEngine
from app.ai.enhanced_llm_service import EnhancedLLMService

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_conversations: Dict[str, str] = {}  # user_id -> current_conversation_id
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_conversations:
            del self.user_conversations[user_id]
    
    async def send_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_text(json.dumps(message))
            except:
                # Connection might be closed, remove it
                self.disconnect(user_id)
    
    def set_user_conversation(self, user_id: str, conversation_id: str):
        """Set the current conversation for a user"""
        self.user_conversations[user_id] = conversation_id
    
    def get_user_conversation(self, user_id: str) -> str:
        """Get the current conversation for a user"""
        return self.user_conversations.get(user_id)

manager = ConnectionManager()

async def get_websocket_user(websocket: WebSocket) -> dict:
    """Authenticate WebSocket connection"""
    try:
        # Get token from query params or headers
        token = websocket.query_params.get("token")
        if not token:
            token = websocket.headers.get("authorization", "").replace("Bearer ", "")
        
        if not token:
            await websocket.close(code=4001, reason="Authentication required")
            return None
        
        print(f"🔑 WebSocket token received: {token[:10]}...")
        
        # Verify token
        token_data = AuthService.verify_token(token)
        if not token_data:
            print(f"❌ WebSocket token verification failed")
            await websocket.close(code=4001, reason="Invalid token")
            return None
        
        print(f"✅ WebSocket token verified for: {token_data.email}")
        
        # Get user from MongoDB
        user = await find_user_by_email(token_data.email)
        if not user:
            print(f"❌ User not found: {token_data.email}")
            await websocket.close(code=4001, reason="User not found")
            return None
        
        print(f"✅ WebSocket user authenticated: {user['email']}")
        return user
        
    except Exception as e:
        print(f"❌ WebSocket authentication error: {str(e)}")
        await websocket.close(code=4001, reason="Authentication failed")
        return None

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """Enhanced WebSocket endpoint for streaming chat responses"""
    
    # Authenticate user
    user = await get_websocket_user(websocket)
    if not user:
        return
    
    # Connect to WebSocket
    await manager.connect(websocket, str(user["_id"]))
    
    try:
        # Use enhanced AI for all messages - remove MockGrokService fallback
        print("🚀 Using Enhanced AI Engine for all WebSocket connections")
        enhanced_engine = EnhancedPromptEngine()
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type")
            
            if message_type == "chat":
                try:
                    await handle_enhanced_chat_message(message_data, user, enhanced_engine)
                except Exception as e:
                    await manager.send_message(str(user["_id"]), {
                        "type": "error",
                        "message": str(e)
                    })
            
            elif message_type == "set_conversation":
                # Set current conversation for user
                conversation_id = message_data.get("conversation_id")
                if conversation_id:
                    manager.set_user_conversation(str(user["_id"]), conversation_id)
                    await manager.send_message(str(user["_id"]), {
                        "type": "conversation_set",
                        "conversation_id": conversation_id
                    })
            
            elif message_type == "edit_message":
                try:
                    await handle_message_edit(message_data, user, grok_service)
                except Exception as e:
                    await manager.send_message(str(user["_id"]), {
                        "type": "error",
                        "message": str(e)
                    })
            
            elif message_type == "regenerate_response":
                try:
                    await handle_response_regeneration(message_data, user, grok_service)
                except Exception as e:
                    await manager.send_message(str(user["_id"]), {
                        "type": "error",
                        "message": str(e)
                    })
            
            elif message_type == "ping":
                await manager.send_message(str(user["_id"]), {"type": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(str(user["_id"]))
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(str(user["_id"]))

async def handle_enhanced_chat_message(message_data, user, enhanced_engine):
    """Handle chat message using enhanced AI engine"""
    import time
    
    conversation_id = message_data.get("conversation_id")
    message_content = message_data.get("message")
    
    if not conversation_id or not message_content:
        raise Exception("Missing conversation_id or message")
    
    # Verify conversation belongs to user
    conversation = await find_conversation_by_id(conversation_id)
    if not conversation:
        print(f"❌ Conversation {conversation_id} not found")
        raise Exception("Conversation not found")
    
    # Convert both to string for comparison
    conversation_user_id = str(conversation["user_id"])
    current_user_id = str(user["_id"])
    
    if conversation_user_id != current_user_id:
        print(f"❌ User ID mismatch: conv={conversation_user_id} vs user={current_user_id}")
        raise Exception("Conversation not found")
    
    # Start enhanced response
    await manager.send_message(str(user["_id"]), {
        "type": "stream_start",
        "model": "Enhanced LLM + FAISS RAG",
        "conversation_id": conversation_id
    })
    
    try:
        # Use enhanced prompt engine
        start_time = time.time()
        
        # Generate enhanced response with context
        result = await enhanced_engine.generate_prompt(
            message_content, 
            str(user["_id"]),
            conversation_id
        )
        
        response_time = time.time() - start_time
        
        # Send structured response like corporate dashboard
        if result.get("llm_response"):
            # Send metadata first
            metadata = f"📊 **Analysis Results:**\n" \
                      f"• **Model:** {result.get('model_used', 'Enhanced LLM + FAISS RAG')}\n" \
                      f"• **Confidence:** {result.get('confidence_score', 0)}%\n" \
                      f"• **Context Chunks:** {len(result.get('retrieved_context', []))}\n" \
                      f"• **Response Time:** {response_time:.2f}s\n\n"
            
            await manager.send_message(str(user["_id"]), {
                "type": "stream_chunk",
                "content": metadata,
                "conversation_id": conversation_id
            })
            
            # Send main response
            await manager.send_message(str(user["_id"]), {
                "type": "stream_chunk", 
                "content": result["llm_response"],
                "conversation_id": conversation_id
            })
            
            # Send completion with standardized format
            await manager.send_message(str(user["_id"]), {
                "type": "stream_end",
                "message": {
                    "id": result.get("id", str(time.time())),
                    "role": "assistant",
                    "content": result["llm_response"],
                    "model": result.get('model_used', 'Enhanced LLM + FAISS RAG'),
                    "confidence": result.get('confidence_score', 0),
                    "context_chunks": len(result.get('retrieved_context', [])),
                    "tokens": result.get('token_usage', {}).get('total_tokens', 0),
                    "response_time": result.get('performance', {}).get('total_time', 0),
                    "created_at": datetime.utcnow().isoformat()
                },
                "conversation_id": conversation_id
            })
            
            # Save to database
            user_message_data = {
                "conversation_id": conversation_id,
                "role": "user", 
                "content": message_content,
                "created_at": datetime.utcnow()
            }
            await insert_message(user_message_data)
            
            assistant_message_data = {
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": result["llm_response"],
                "created_at": datetime.utcnow(),
                "tokens": result.get("token_count", 0)
            }
            await insert_message(assistant_message_data)
            
        else:
            raise Exception("Failed to generate enhanced response")
            
    except Exception as e:
        await manager.send_message(str(user["_id"]), {
            "type": "error",
            "message": f"Enhanced AI error: {str(e)}"
        })
