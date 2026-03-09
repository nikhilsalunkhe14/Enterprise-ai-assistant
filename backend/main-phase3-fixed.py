from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import create_tables
from routes.auth import router as auth_router
from routes.conversation import router as conversation_router
from routes.chat import router as chat_router
from routes.websocket import router as websocket_router
import os

# Create FastAPI app
app = FastAPI(
    title="ChatGPT Clone API",
    description="Production-ready ChatGPT clone with Grok AI integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"  # For development, restrict in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, tags=["authentication"])  # No prefix - already in auth.py
app.include_router(conversation_router, prefix="/api/conversations", tags=["conversations"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(websocket_router, tags=["websocket"])  # No prefix for WebSocket

# Create database tables
@app.on_event("startup")
async def startup_event():
    create_tables()

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "ChatGPT Clone API",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "authentication", 
            "conversation_persistence", 
            "ai_chat",
            "streaming_responses",
            "grok_ai_integration"
        ]
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Models endpoint
@app.get("/api/models")
async def get_available_models():
    """Get available AI models"""
    from services.mock_grok_service import MOCK_GROK_MODELS
    return {
        "models": [
            {
                "id": model_id,
                "name": model_config["name"],
                "description": model_config["description"],
                "max_tokens": model_config["max_tokens"],
                "provider": model_config["provider"]
            }
            for model_id, model_config in MOCK_GROK_MODELS.items()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main-phase3-fixed:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
