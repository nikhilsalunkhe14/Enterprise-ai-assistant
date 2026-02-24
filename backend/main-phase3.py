from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import create_tables
from routes.auth import router as auth_router
from routes.conversation_fixed import router as conversation_router
from routes.chat import router as chat_router
import os

# Create FastAPI app
app = FastAPI(
    title="Enterprise AI Assistant API",
    description="Production-ready authentication, conversation, and AI chat system",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://huggingface.co",
        "*"  # For development, restrict in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(conversation_router)
app.include_router(chat_router)

# Create database tables
@app.on_event("startup")
async def startup_event():
    create_tables()

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Enterprise AI Assistant API",
        "version": "3.0.0",
        "status": "running",
        "features": ["authentication", "conversation_persistence", "ai_chat"]
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
