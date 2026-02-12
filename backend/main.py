from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from services.standards_loader import get_all_standards
from app.routes.prompt_routes import router as prompt_router
from app.ai import initialize_ai_components
from app.core.logger import logger
import json
import os

# Get port from environment (HuggingFace Spaces uses 7860)
port = int(os.environ.get("PORT", 7860))

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="AI Prompt Engineering Agent",
    description="Backend for AI-based IT Project Delivery Guidance Agent with RAG Architecture",
    version="1.0.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include prompt routes
app.include_router(prompt_router)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize AI components at startup"""
    logger.info("Initializing AI components...")
    initialize_ai_components()
    logger.info("✅ Embedding engine ready")
    logger.info("✅ Vector store ready")
    logger.info("🚀 AI components initialized successfully!")

@app.get("/", response_class=RedirectResponse)
async def root():
    """Redirect to corporate dashboard"""
    return RedirectResponse(url="/static/corporate-dashboard.html")

@app.get("/health")
@limiter.limit("60/minute")
async def health_check(request):
    """Basic health check endpoint"""
    return {"status": "healthy", "message": "AI Prompt Engineering Agent is running"}

@app.get("/standards")
@limiter.limit("30/minute")
async def get_standards(request):
    """Get all standards as JSON response"""
    standards = get_all_standards()
    return {"standards": standards}

@app.get("/standards/{standard_name}")
async def get_specific_standard(standard_name: str):
    """Get a specific standard by name"""
    # List of available standard files
    available_standards = [
        "sdlc", "agile", "devops", "itil", "iso", "pmbok"
    ]
    
    # Check if the requested standard exists
    if standard_name not in available_standards:
        raise HTTPException(status_code=404, detail="Standard not found")
    
    # Construct file path
    standards_dir = os.path.join(os.path.dirname(__file__), "standards")
    file_path = os.path.join(standards_dir, f"{standard_name}.json")
    
    try:
        # Load and return the specific standard
        with open(file_path, 'r', encoding='utf-8') as f:
            standard_data = json.load(f)
        return standard_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Standard not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error reading standard data")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
