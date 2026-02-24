from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import create_tables
from routes.auth import router as auth_router
import os

# Create FastAPI app
app = FastAPI(
    title="Enterprise AI Assistant API",
    description="Production-ready authentication system",
    version="1.0.0"
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

# Create database tables
@app.on_event("startup")
async def startup_event():
    create_tables()

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Enterprise AI Assistant API",
        "version": "1.0.0",
        "status": "running"
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
