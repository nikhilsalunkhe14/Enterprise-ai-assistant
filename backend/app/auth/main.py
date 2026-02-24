from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import sqlite3
import os

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database initialization
def init_db():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Models
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

# Database functions
def get_user_by_email(email: str):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(user_data: dict):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Hash password
    hashed_password = pwd_context.hash(user_data['password'])
    
    cursor.execute('''
        INSERT INTO users (email, username, password_hash, full_name)
        VALUES (?, ?, ?, ?)
    ''', (user_data['email'], user_data['username'], hashed_password, user_data.get('full_name')))
    
    conn.commit()
    conn.close()

def create_session(user_id: int, token: str):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    cursor.execute('''
        INSERT INTO sessions (user_id, token, expires_at)
        VALUES (?, ?, ?)
    ''', (user_id, token, expires_at))
    
    conn.commit()
    conn.close()

def verify_token(token: str):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.user_id, u.email, u.username, u.full_name
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.token = ? AND s.expires_at > CURRENT_TIMESTAMP
    ''', (token,))
    
    result = cursor.fetchone()
    conn.close()
    return result

# Authentication functions
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# FastAPI app
app = FastAPI(title="Enterprise AI Assistant API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        token = credentials.credentials
    except JWTError:
        raise credentials_exception
    
    user_data = verify_token(token)
    if user_data is None:
        raise credentials_exception
    
    return user_data

# Routes
@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    # Check if user exists
    existing_user = get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_data = user.dict()
    create_user(user_data)
    
    # Get created user
    created_user = get_user_by_email(user.email)
    
    return UserResponse(
        id=created_user[0],
        email=created_user[1],
        username=created_user[2],
        full_name=created_user[4],
        is_active=created_user[5],
        created_at=created_user[6]
    )

@app.post("/api/auth/login", response_model=Token)
async def login(user: UserLogin):
    # Authenticate user
    db_user = get_user_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user[3]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": db_user[0], "email": db_user[1]},
        expires_delta=access_token_expires
    )
    
    # Create session
    create_session(db_user[0], token)
    
    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user[0],
        email=current_user[1],
        username=current_user[2],
        full_name=current_user[3],
        is_active=True,
        created_at=current_user[4] if len(current_user) > 4 else None
    )

@app.post("/api/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    # In a real implementation, you would invalidate the token
    # For now, just return success
    return {"message": "Successfully logged out"}

@app.get("/")
async def root():
    return {"message": "Enterprise AI Assistant API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
