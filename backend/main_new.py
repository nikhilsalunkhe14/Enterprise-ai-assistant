from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import routes
from routes.auth import router as auth_router
from routes.chat import router as chat_router
from routes.conversations import router as conversations_router
from routes.messages import router as messages_router
from routes.usage import router as usage_router
from routes.websocket_new import router as websocket_router
from routes.tool_integration import router as tool_integration_router

# Import app routes for enhanced AI
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
from app.routes.prompt_routes import router as prompt_router
from app.routes.pm_tools import router as pm_tools_router

# Import MongoDB connection
from database.mongodb import mongodb_manager

# Get port from environment (HuggingFace Spaces uses 7860)
port = int(os.environ.get("PORT", 7860))

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="ChatGPT Clone - Advanced AI Assistant",
    description="Advanced ChatGPT clone with MongoDB Atlas, conversation management, and AI optimization",
    version="2.0.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:5500/frontend", "http://127.0.0.1:5500/frontend", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include all routes
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(messages_router)
app.include_router(usage_router)
app.include_router(websocket_router)
app.include_router(tool_integration_router)
app.include_router(prompt_router)
app.include_router(pm_tools_router)

# Mount static files for frontend directory
import os
frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
app.mount("/static", StaticFiles(directory=frontend_path), name="frontend")

@app.get("/debug/test-token")
async def get_test_token():
    """Generate test token for WebSocket testing"""
    from services.jwt_service import AuthService
    test_data = {"sub": "test_user"}
    token = AuthService.create_access_token(test_data)
    return {"token": token}

@app.get("/debug")
async def debug_endpoint():
    """Initialize MongoDB connection and services"""
    try:
        print("Starting ChatGPT Clone Backend...")
        
        # Connect to MongoDB Atlas
        await mongodb_manager.connect()
        print("MongoDB Atlas connected successfully")
        
        print("ChatGPT Clone Backend is ready!")
        
    except Exception as e:
        print(f"Startup error: {str(e)}")
        raise

@app.on_event("startup")
async def startup_event():
    """Initialize MongoDB connection and services"""
    try:
        print("Starting ChatGPT Clone Backend...")
        
        # Connect to MongoDB Atlas
        await mongodb_manager.connect()
        print("MongoDB Atlas connected successfully")
        
        print("ChatGPT Clone Backend is ready!")
        
    except Exception as e:
        print(f"Startup error: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources"""
    try:
        await mongodb_manager.disconnect()
        print("MongoDB connection closed")
    except Exception as e:
        print(f"Shutdown error: {str(e)}")

@app.get("/", response_class=RedirectResponse)
async def root():
    """Redirect to frontend"""
    return RedirectResponse(url="/static/index.html")

@app.get("/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    """Enhanced health check endpoint"""
    try:
        # Check MongoDB connection
        await mongodb_manager.client.admin.command('ping')
        mongodb_status = "healthy"
    except:
        mongodb_status = "unhealthy"
    
    return {
        "status": "healthy" if mongodb_status == "healthy" else "degraded",
        "version": "2.0.0",
        "services": {
            "mongodb": mongodb_status,
            "api": "healthy"
        },
        "message": "ChatGPT Clone Advanced AI Assistant"
    }

@app.get("/info")
@limiter.limit("30/minute")
async def get_app_info(request: Request):
    """Get application information"""
    return {
        "name": "ChatGPT Clone",
        "version": "2.0.0",
        "description": "Advanced ChatGPT clone with MongoDB Atlas",
        "features": [
            "MongoDB Atlas storage",
            "Conversation management",
            "Message editing & regeneration",
            "Chat search",
            "Export conversations",
            "Usage tracking",
            "Rate limiting",
            "AI context optimization",
            "WebSocket streaming",
            "Auto title generation"
        ],
        "endpoints": {
            "auth": "/api/auth",
            "chat": "/api/chat",
            "conversations": "/api/conversations",
            "messages": "/api/messages",
            "usage": "/api/usage",
            "websocket": "/ws/chat"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
