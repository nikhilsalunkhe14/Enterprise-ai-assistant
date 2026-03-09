from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class MongoDBManager:
    def __init__(self):
        self.mongodb_url = os.getenv("MONGODB_URL")
        self.database_name = os.getenv("DATABASE_NAME", "chatgpt_clone")
        self.client = None
        self.database = None
        
        if not self.mongodb_url:
            raise ValueError("MONGODB_URL environment variable is required")
        
        logger.info(f"Initializing MongoDB connection to database: {self.database_name}")
    
    async def connect(self):
        """Establish connection to MongoDB Atlas"""
        try:
            self.client = AsyncIOMotorClient(self.mongodb_url)
            self.database = self.client[self.database_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("✅ Connected to MongoDB Atlas successfully")
            
            # Create indexes for better performance
            await self.create_indexes()
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            raise
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    async def create_indexes(self):
        """Create indexes for collections"""
        try:
            # Users collection indexes
            await self.database.users.create_index("email", unique=True)
            await self.database.users.create_index("created_at")
            
            # Conversations collection indexes
            await self.database.conversations.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
            await self.database.conversations.create_index("updated_at")
            await self.database.conversations.create_index([("user_id", ASCENDING), ("title", "text")])
            await self.database.conversations.create_index([("user_id", ASCENDING), ("is_pinned", DESCENDING), ("updated_at", DESCENDING)])
            
            # Messages collection indexes
            await self.database.messages.create_index([("conversation_id", ASCENDING), ("created_at", ASCENDING)])
            await self.database.messages.create_index([("conversation_id", ASCENDING), ("role", ASCENDING), ("created_at", DESCENDING)])
            
            # Usage collection indexes
            await self.database.usage.create_index([("user_id", ASCENDING), ("last_request", DESCENDING)])
            
            logger.info("✅ Database indexes created successfully")
        except Exception as e:
            logger.error(f"❌ Error creating indexes: {str(e)}")
    
    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        if self.database is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.database[collection_name]

# Global MongoDB instance
mongodb_manager = MongoDBManager()

# Database operations helper functions
async def get_database():
    """Get database instance"""
    return mongodb_manager.database

async def insert_user(user_data: Dict[str, Any]) -> str:
    """Insert a new user into the users collection"""
    collection = mongodb_manager.get_collection("users")
    result = await collection.insert_one(user_data)
    return str(result.inserted_id)

async def find_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Find a user by email"""
    collection = mongodb_manager.get_collection("users")
    user = await collection.find_one({"email": email})
    return user

async def find_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Find a user by ID"""
    collection = mongodb_manager.get_collection("users")
    try:
        user = await collection.find_one({"_id": ObjectId(user_id)})
        return user
    except:
        return None

async def update_user_last_login(user_id: str):
    """Update user's last login timestamp"""
    collection = mongodb_manager.get_collection("users")
    try:
        await collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login": datetime.utcnow()}}
        )
    except:
        pass

async def insert_conversation(conversation_data: Dict[str, Any]) -> str:
    """Insert a new conversation"""
    collection = mongodb_manager.get_collection("conversations")
    result = await collection.insert_one(conversation_data)
    return str(result.inserted_id)

async def find_conversations_by_user(user_id: str, limit: int = 50, include_archived: bool = False) -> List[Dict[str, Any]]:
    """Get all conversations for a user"""
    collection = mongodb_manager.get_collection("conversations")
    query = {"user_id": user_id}
    if not include_archived:
        query["is_archived"] = {"$ne": True}
    
    cursor = collection.find(query).sort([
        ("is_pinned", DESCENDING),
        ("updated_at", DESCENDING)
    ]).limit(limit)
    conversations = []
    async for conversation in cursor:
        conversation["id"] = str(conversation["_id"])
        conversations.append(conversation)
    return conversations

async def search_conversations(user_id: str, search_query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search conversations by title"""
    collection = mongodb_manager.get_collection("conversations")
    query = {
        "user_id": user_id,
        "is_archived": {"$ne": True},
        "$text": {"$search": search_query}
    }
    
    cursor = collection.find(query).sort([
        ("is_pinned", DESCENDING),
        ("updated_at", DESCENDING)
    ]).limit(limit)
    conversations = []
    async for conversation in cursor:
        conversation["id"] = str(conversation["_id"])
        conversations.append(conversation)
    return conversations

async def find_conversation_by_id(conversation_id: str) -> Optional[Dict[str, Any]]:
    """Find a conversation by ID"""
    collection = mongodb_manager.get_collection("conversations")
    try:
        conversation = await collection.find_one({"_id": ObjectId(conversation_id)})
        if conversation:
            conversation["id"] = str(conversation["_id"])
        return conversation
    except:
        return None

async def update_conversation(conversation_id: str, update_data: Dict[str, Any]):
    """Update a conversation"""
    collection = mongodb_manager.get_collection("conversations")
    try:
        await collection.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": update_data}
        )
    except:
        pass

async def pin_conversation(conversation_id: str, is_pinned: bool = True):
    """Pin or unpin a conversation"""
    await update_conversation(conversation_id, {
        "is_pinned": is_pinned,
        "updated_at": datetime.utcnow()
    })

async def archive_conversation(conversation_id: str, is_archived: bool = True):
    """Archive or unarchive a conversation"""
    await update_conversation(conversation_id, {
        "is_archived": is_archived,
        "updated_at": datetime.utcnow()
    })

async def delete_conversation(conversation_id: str):
    """Delete a conversation and its messages"""
    conversations_collection = mongodb_manager.get_collection("conversations")
    messages_collection = mongodb_manager.get_collection("messages")
    
    try:
        # Delete all messages in the conversation
        await messages_collection.delete_many({"conversation_id": conversation_id})
        # Delete the conversation
        await conversations_collection.delete_one({"_id": ObjectId(conversation_id)})
    except:
        pass

async def insert_message(message_data: Dict[str, Any]) -> str:
    """Insert a new message"""
    collection = mongodb_manager.get_collection("messages")
    result = await collection.insert_one(message_data)
    return str(result.inserted_id)

async def find_messages_by_conversation(conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get all messages for a conversation"""
    collection = mongodb_manager.get_collection("messages")
    cursor = collection.find({"conversation_id": conversation_id}).sort("created_at", ASCENDING).limit(limit)
    messages = []
    async for message in cursor:
        message["id"] = str(message["_id"])
        messages.append(message)
    return messages

async def find_message_by_id(message_id: str) -> Optional[Dict[str, Any]]:
    """Find a message by ID"""
    collection = mongodb_manager.get_collection("messages")
    try:
        message = await collection.find_one({"_id": ObjectId(message_id)})
        if message:
            message["id"] = str(message["_id"])
        return message
    except:
        return None

async def update_message(message_id: str, update_data: Dict[str, Any]):
    """Update a message"""
    collection = mongodb_manager.get_collection("messages")
    try:
        await collection.update_one(
            {"_id": ObjectId(message_id)},
            {"$set": update_data}
        )
    except:
        pass

async def delete_message(message_id: str):
    """Delete a message"""
    collection = mongodb_manager.get_collection("messages")
    try:
        await collection.delete_one({"_id": ObjectId(message_id)})
    except:
        pass

async def delete_messages_after(conversation_id: str, message_id: str):
    """Delete all messages after a specific message in a conversation"""
    collection = mongodb_manager.get_collection("messages")
    try:
        target_message = await find_message_by_id(message_id)
        if target_message:
            await collection.delete_many({
                "conversation_id": conversation_id,
                "created_at": {"$gt": target_message["created_at"]}
            })
    except:
        pass

async def get_conversation_message_count(conversation_id: str) -> int:
    """Get the count of messages in a conversation"""
    collection = mongodb_manager.get_collection("messages")
    count = await collection.count_documents({"conversation_id": conversation_id})
    return count

# Usage tracking functions
async def track_usage(user_id: str, tokens_used: int):
    """Track user API usage"""
    collection = mongodb_manager.get_collection("usage")
    await collection.update_one(
        {"user_id": user_id},
        {
            "$inc": {
                "tokens_used": tokens_used,
                "request_count": 1
            },
            "$set": {
                "last_request": datetime.utcnow()
            }
        },
        upsert=True
    )

async def get_user_usage(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user usage statistics"""
    collection = mongodb_manager.get_collection("usage")
    usage = await collection.find_one({"user_id": user_id})
    return usage
