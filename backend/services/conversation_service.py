from sqlalchemy.orm import Session
from models.conversation import Conversation, Message
from models.conversation_schemas import ConversationCreate, MessageCreate
from sqlalchemy import desc, func
from datetime import datetime

class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    def create_conversation(self, user_id: int, conversation: ConversationCreate) -> Conversation:
        """Create new conversation"""
        db_conversation = Conversation(
            user_id=user_id,
            title=conversation.title
        )
        
        self.db.add(db_conversation)
        self.db.commit()
        self.db.refresh(db_conversation)
        
        return db_conversation

    def get_user_conversations(self, user_id: int) -> list:
        """Get all conversations for a user with message count"""
        conversations = self.db.query(
            Conversation.id,
            Conversation.user_id,
            Conversation.title,
            Conversation.created_at,
            func.count(Message.id).label('message_count')
        ).outerjoin(Message).filter(
            Conversation.user_id == user_id
        ).group_by(
            Conversation.id
        ).order_by(
            desc(Conversation.created_at)
        ).all()
        
        return conversations

    def get_conversation_by_id(self, conversation_id: int, user_id: int) -> Conversation:
        """Get conversation by ID for specific user"""
        return self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()

    def get_conversation_with_messages(self, conversation_id: int, user_id: int) -> Conversation:
        """Get conversation with all messages"""
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        
        if conversation:
            # Load messages
            messages = self.db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at).all()
            conversation.messages = messages
        
        return conversation

    def create_message(self, message: MessageCreate) -> Message:
        """Create new message"""
        db_message = Message(
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content
        )
        
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        
        return db_message

    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Delete conversation and all messages"""
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if conversation:
            self.db.delete(conversation)
            self.db.commit()
            return True
        return False

    def update_conversation_title(self, conversation_id: int, user_id: int, title: str) -> bool:
        """Update conversation title"""
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if conversation:
            conversation.title = title
            self.db.commit()
            return True
        return False
