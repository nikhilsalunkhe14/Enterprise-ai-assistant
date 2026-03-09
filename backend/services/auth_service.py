from sqlalchemy.orm import Session
from models.user import User
from models.schemas import UserCreate
from passlib.context import CryptContext
from datetime import datetime

# Password hashing - using simpler approach
import hashlib
import secrets

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

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> User:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> User:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user: UserCreate) -> User:
        """Create new user"""
        # Hash password using simple method
        hashed_password = hash_password(user.password)
        
        # Create user object
        db_user = User(
            email=user.email,
            name=user.name,
            password_hash=hashed_password
        )
        
        # Add to database
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user

    def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate user with email and password"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return verify_password(plain_password, hashed_password)
