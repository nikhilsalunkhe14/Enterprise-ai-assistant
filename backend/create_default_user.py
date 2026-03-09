import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from database.mongodb import insert_user, find_user_by_email
from datetime import datetime
import hashlib
import secrets

def hash_password(password: str) -> str:
    """Simple password hashing"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${password_hash}"

async def create_default_user():
    """Create a default user for testing"""
    # Connect to database first
    from database.mongodb import mongodb_manager
    await mongodb_manager.connect()
    
    email = "test@example.com"
    password = "test123"
    name = "Test User"
    
    # Check if user already exists
    existing_user = await find_user_by_email(email)
    if existing_user:
        print(f"✅ User {email} already exists!")
        return
    
    # Hash password
    password_hash = hash_password(password)
    
    # Create user data
    user_data = {
        "email": email,
        "password_hash": password_hash,
        "name": name,
        "created_at": datetime.utcnow(),
        "last_login": None,
        "is_active": True
    }
    
    # Insert user
    user_id = await insert_user(user_data)
    print(f"✅ Default user created successfully!")
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
    print(f"🆔 User ID: {user_id}")
    
    # Close connection
    await mongodb_manager.close()

if __name__ == "__main__":
    asyncio.run(create_default_user())
