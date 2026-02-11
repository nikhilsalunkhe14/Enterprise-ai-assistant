import re
import html
from typing import Dict, Any, Optional
from fastapi import HTTPException
from app.core.logger import logger

class InputValidator:
    @staticmethod
    def sanitize_input(user_input: str) -> str:
        """Sanitize user input to prevent XSS and injection attacks"""
        if not user_input:
            raise ValueError("Input cannot be empty")
        
        # Remove potential HTML tags
        sanitized = html.escape(user_input)
        
        # Remove potential script content
        script_pattern = r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>'
        sanitized = re.sub(script_pattern, '', sanitized, flags=re.IGNORECASE)
        
        # Remove SQL injection patterns
        sql_patterns = [
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',
            r'(--|#|\/\*|\*\/)',
            r'(\bor\b\s+\d+\s*=\s*\d+\b)',
            r'(\band\b\s+\d+\s*=\s*\d+\b)'
        ]
        
        for pattern in sql_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        # Length validation
        if len(sanitized) > 2000:
            raise ValueError("Input too long (max 2000 characters)")
        
        if len(sanitized.strip()) < 3:
            raise ValueError("Input too short (min 3 characters)")
        
        return sanitized.strip()
    
    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """Validate session ID format"""
        if not session_id:
            return False
        
        # Basic email_timestamp format validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}_\d{13}$'
        return bool(re.match(pattern, session_id))
    
    @staticmethod
    def validate_query_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize query parameters"""
        validated = {}
        
        if 'user_query' in params:
            try:
                validated['user_query'] = InputValidator.sanitize_input(params['user_query'])
            except ValueError as e:
                logger.error(f"Invalid user_query: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Invalid query: {str(e)}")
        
        if 'session_id' in params:
            if not InputValidator.validate_session_id(params['session_id']):
                logger.error("Invalid session_id format")
                raise HTTPException(status_code=401, detail="Invalid session")
            validated['session_id'] = params['session_id']
        
        return validated

class SecurityMiddleware:
    @staticmethod
    def add_security_headers(response):
        """Add security headers to response"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        return response
