from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import get_db
from models.schemas import UserCreate, UserResponse, UserLogin, Token
from models.user import User
from services.auth_service import UserService
from services.jwt_service import AuthService, get_current_user
from datetime import timedelta

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    user_service = UserService(db)
    
    # Check if user already exists
    existing_user = user_service.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    db_user = user_service.create_user(user)
    
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        name=db_user.name,
        created_at=db_user.created_at,
        last_login=db_user.last_login,
        is_active=db_user.is_active
    )

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    user_service = UserService(db)
    
    # Authenticate user
    db_user = user_service.authenticate_user(user.email, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = AuthService.create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=30 * 60  # 30 minutes in seconds
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        is_active=current_user.is_active
    )

@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Successfully logged out"}
