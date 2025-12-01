"""
Repository layer for database operations.

Provides high-level CRUD operations for Chat and Message models.
"""
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session

from src.db.models import AgentType, Chat, Message, MessageRole


class ChatRepository:
    """Repository for Chat operations"""
    
    @staticmethod
    def create(session: Session) -> Chat:
        """Create a new empty chat"""
        chat = Chat(step_count=0)
        session.add(chat)
        session.flush()
        return chat
    
    @staticmethod
    def get_by_id(session: Session, chat_id: int) -> Optional[Chat]:
        """Get chat by ID"""
        return session.query(Chat).filter(Chat.id == chat_id).first()
    
    @staticmethod
    def delete(session: Session, chat_id: int) -> bool:
        """Delete a chat and all its messages"""
        chat = ChatRepository.get_by_id(session, chat_id)
        if chat:
            session.delete(chat)
            return True
        return False
    
    @staticmethod
    def increment_step_count(session: Session, chat_id: int) -> Optional[Chat]:
        """Increment the step count for a chat"""
        chat = ChatRepository.get_by_id(session, chat_id)
        if chat:
            chat.step_count += 1
            session.flush()
        return chat
    
    @staticmethod
    def list_all(session: Session, active_only: bool = False) -> List[Chat]:
        """List all chats"""
        query = session.query(Chat)
        if active_only:
            query = query.filter(Chat.is_active == True)
        return query.order_by(Chat.created_at.desc()).all()


class MessageRepository:
    """Repository for Message operations"""
    
    @staticmethod
    def create(
        session: Session,
        chat_id: int,
        role: MessageRole,
        content: str,
        agent_type: Optional[AgentType] = None
    ) -> Message:
        """Create a new message"""
        message = Message(
            chat_id=chat_id,
            role=role,
            agent_type=agent_type,
            content=content
        )
        session.add(message)
        session.flush()
        return message
    
    @staticmethod
    def get_by_id(session: Session, message_id: int) -> Optional[Message]:
        """Get message by ID"""
        return session.query(Message).filter(Message.id == message_id).first()
    
    @staticmethod
    def delete(session: Session, message_id: int) -> bool:
        """Delete a message"""
        message = MessageRepository.get_by_id(session, message_id)
        if message:
            session.delete(message)
            return True
        return False
    
    @staticmethod
    def list_by_chat(session: Session, chat_id: int) -> List[Message]:
        """Get all messages for a chat, ordered by creation time"""
        return session.query(Message).filter(
            Message.chat_id == chat_id
        ).order_by(Message.created_at).all()
    
    @staticmethod
    def get_context(session: Session, chat_id: int) -> List[Dict[str, Any]]:
        """
        Get messages formatted for LLM context.
        Returns list of dicts with 'role' and 'content' keys.
        """
        messages = MessageRepository.list_by_chat(session, chat_id)
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]
