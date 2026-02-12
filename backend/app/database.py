import sqlite3
import os
from datetime import datetime
from backend.app.core.config import settings
from backend.app.core.logger import logger

class DatabaseManager:
    def __init__(self):
        # Extract database path from DATABASE_URL (sqlite:///./ai_agent.db)
        if settings.DATABASE_URL.startswith("sqlite:///"):
            self.db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        else:
            # Fallback to default if URL format is different
            self.db_path = "ai_agent.db"
        
        logger.info(f"Initializing database at: {self.db_path}")
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with conversations table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_query TEXT NOT NULL,
                    detected_domain TEXT,
                    detected_stage TEXT,
                    confidence_score INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def save_conversation(self, session_id: str, user_query: str, detected_domain: str, 
                         detected_stage: str, confidence_score: int):
        """Save conversation record to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversations 
                (session_id, user_query, detected_domain, detected_stage, confidence_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, user_query, detected_domain, detected_stage, confidence_score))
            
            conn.commit()
            conn.close()
            logger.info(f"Conversation saved for session: {session_id}")
        except sqlite3.Error as e:
            logger.error(f"Error saving conversation: {e}")
            raise
    
    def get_last_domain_for_session(self, session_id: str) -> str:
        """Get the last detected domain for a given session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT detected_domain FROM conversations 
                WHERE session_id = ? AND detected_domain IS NOT NULL
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (session_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Error retrieving last domain: {e}")
            return None
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> list:
        """Get conversation history for a session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_query, detected_domain, detected_stage, confidence_score, created_at
                FROM conversations 
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (session_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "user_query": row[0],
                    "detected_domain": row[1],
                    "detected_stage": row[2],
                    "confidence_score": row[3],
                    "created_at": row[4]
                }
                for row in results
            ]
        except sqlite3.Error as e:
            print(f"Error retrieving conversation history: {e}")
            return []

# Global database instance
db_manager = DatabaseManager()
