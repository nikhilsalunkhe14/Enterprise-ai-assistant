from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime
from services.jwt_service import get_current_user
from database.mongodb import get_user_usage

router = APIRouter(prefix="/api/usage", tags=["usage"])

# Pydantic models
class UsageResponse(BaseModel):
    user_id: str
    tokens_used: int
    request_count: int
    last_request: datetime

@router.get("", response_model=UsageResponse)
async def get_usage_stats(current_user: dict = Depends(get_current_user)):
    """Get current user's usage statistics"""
    usage = await get_user_usage(str(current_user["_id"]))
    
    if not usage:
        return UsageResponse(
            user_id=str(current_user["_id"]),
            tokens_used=0,
            request_count=0,
            last_request=datetime.utcnow()
        )
    
    return UsageResponse(
        user_id=usage["user_id"],
        tokens_used=usage.get("tokens_used", 0),
        request_count=usage.get("request_count", 0),
        last_request=usage.get("last_request", datetime.utcnow())
    )
