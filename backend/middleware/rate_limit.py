from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis
import os
import json
from typing import Dict, Any
import time

# Redis connection for distributed rate limiting
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

class RateLimitMiddleware:
    """Custom rate limiting middleware with Redis backend"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Get client IP
            client_ip = get_remote_address(request)
            
            # Check rate limits
            await self.check_rate_limits(client_ip, request)
        
        await self.app(scope, receive, send)
    
    async def check_rate_limits(self, client_ip: str, request: Request):
        """Check various rate limits"""
        current_time = int(time.time())
        
        # Different limits for different endpoints
        if request.url.path.startswith("/api/chat"):
            # Chat endpoints: stricter limits
            await self.check_sliding_window_limit(
                f"chat:{client_ip}", 
                limit=20,  # 20 requests per minute
                window=60,
                current_time
            )
        elif request.url.path.startswith("/api/auth"):
            # Auth endpoints: very strict limits
            await self.check_sliding_window_limit(
                f"auth:{client_ip}",
                limit=5,  # 5 requests per minute
                window=60,
                current_time
            )
        else:
            # General API limits
            await self.check_sliding_window_limit(
                f"general:{client_ip}",
                limit=100,  # 100 requests per minute
                window=60,
                current_time
            )
    
    async def check_sliding_window_limit(self, key: str, limit: int, window: int, current_time: int):
        """Check sliding window rate limit using Redis"""
        pipe = redis_client.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, current_time - window)
        
        # Count current requests
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(current_time): current_time})
        
        # Set expiration
        pipe.expire(key, window)
        
        results = await pipe.execute()
        current_requests = results[1]
        
        if current_requests >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(window)}
            )

# Rate limit configurations for different user tiers
class UserRateLimits:
    """Rate limits based on user subscription tier"""
    
    FREE_TIER = {
        "requests_per_hour": 50,
        "requests_per_day": 200,
        "tokens_per_day": 10000
    }
    
    PRO_TIER = {
        "requests_per_hour": 200,
        "requests_per_day": 1000,
        "tokens_per_day": 50000
    }
    
    ENTERPRISE_TIER = {
        "requests_per_hour": 1000,
        "requests_per_day": 10000,
        "tokens_per_day": 500000
    }

async def check_user_rate_limit(user_id: str, tier: str = "free"):
    """Check user-specific rate limits"""
    current_time = int(time.time())
    hour_start = current_time - 3600  # 1 hour ago
    day_start = current_time - 86400  # 24 hours ago
    
    # Get limits for user tier
    limits = getattr(UserRateLimits, f"{tier.upper()}_TIER")
    
    # Check hourly limit
    hourly_key = f"hourly:{user_id}"
    pipe = redis_client.pipeline()
    pipe.zremrangebyscore(hourly_key, 0, hour_start)
    pipe.zcard(hourly_key)
    hourly_count = (await pipe.execute())[1]
    
    if hourly_count >= limits["requests_per_hour"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Hourly rate limit exceeded"
        )
    
    # Check daily limit
    daily_key = f"daily:{user_id}"
    pipe = redis_client.pipeline()
    pipe.zremrangebyscore(daily_key, 0, day_start)
    pipe.zcard(daily_key)
    daily_count = (await pipe.execute())[1]
    
    if daily_count >= limits["requests_per_day"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily rate limit exceeded"
        )
    
    # Add current request
    await redis_client.zadd(hourly_key, {str(current_time): current_time})
    await redis_client.zadd(daily_key, {str(current_time): current_time})
    await redis_client.expire(hourly_key, 3600)
    await redis_client.expire(daily_key, 86400)

# Rate limit exception handler
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exception handler"""
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": exc.detail
        }
    )
