from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from database.mongodb import (
    insert_user, find_user_by_email, find_user_by_id, update_user_last_login,
    mongodb_manager
)
from services.jwt_service import AuthService, get_current_user
from datetime import datetime, timedelta
import hashlib
import secrets

# Pydantic models
class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None

# Password hashing functions
def hash_password(password: str) -> str:
    """Simple password hashing"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${password_hash}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    try:
        salt, password_hash = hashed_password.split('$')
        expected_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
        return secrets.compare_digest(password_hash, expected_hash)
    except:
        return False

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Register new user"""
    
    # Check if user already exists
    existing_user = await find_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = hash_password(user.password)
    
    # Create user data for MongoDB
    user_data = {
        "email": user.email,
        "password_hash": password_hash,
        "name": user.name,
        "created_at": datetime.utcnow(),
        "last_login": None,
        "is_active": True
    }
    
    # Insert user into MongoDB
    user_id = await insert_user(user_data)
    
    # Get the created user
    db_user = await find_user_by_id(user_id)
    
    return UserResponse(
        id=str(db_user["_id"]),
        email=db_user["email"],
        name=db_user["name"],
        created_at=db_user["created_at"],
        last_login=db_user.get("last_login"),
        is_active=db_user.get("is_active", True)
    )

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    """Login user and return JWT token"""
    
    # Find user by email
    db_user = await find_user_by_email(user.email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    await update_user_last_login(str(db_user["_id"]))
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = AuthService.create_access_token(
        data={"sub": db_user["email"]}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=30 * 60  # 30 minutes in seconds
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    
    # Get user from database
    db_user = await find_user_by_email(current_user["email"])
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(db_user["_id"]),
        email=db_user["email"],
        name=db_user["name"],
        created_at=db_user["created_at"],
        last_login=db_user.get("last_login"),
        is_active=db_user.get("is_active", True)
    )

@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Successfully logged out"}
