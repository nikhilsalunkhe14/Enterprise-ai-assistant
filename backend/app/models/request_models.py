from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class PromptRequest(BaseModel):
    """Request model for prompt generation with strict validation"""
    model_config = ConfigDict(protected_namespaces=())
    
    user_query: str = Field(
        ..., 
        min_length=5, 
        max_length=2000,
        description="User query for AI assistant (5-2000 characters)"
    )
    session_id: str = Field(
        ...,
        description="User session identifier"
    )

class PromptResponse(BaseModel):
    """Response model for prompt generation"""
    model_config = ConfigDict(protected_namespaces=())
    
    user_query: str
    retrieved_context: list
    llm_response: str
    tool_output: Optional[dict] = None
    confidence_score: int
    model_used: str

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    message: str
    details: Optional[dict] = None

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    message: str
    timestamp: Optional[str] = None

class StandardsResponse(BaseModel):
    """Standards response model"""
    standards: list
    count: int
