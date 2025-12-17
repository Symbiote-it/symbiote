"""
Session Manager for managing chat sessions and messages.

Provides simple functions for:
- Creating chats (empty or with initial message)
- Adding messages to chats
- Removing messages
- Getting chat context for LLM
"""
from typing import Optional, List, Dict, Any

from src.db.connection import get_session
from src.db.models import MessageRole, AgentType
from src.db.repository import ChatRepository, MessageRepository


class SessionManager:
    """
    Manages chat sessions with database persistence.
    
    Usage:
        manager = SessionManager()
        
        # Create empty chat
        chat_id = manager.create_chat()
        
        # Or create chat with first message
        chat_id = manager.create_chat(first_message="Hello!")
        
        # Add messages
        manager.add_message(chat_id, "user", "Search for repos")
        manager.add_message(chat_id, "assistant", "Clicking search...", agent_type="deepseek-r1")
        
        # Get context for LLM
        context = manager.get_context(chat_id)
        
        # Remove a message
        manager.remove_message(message_id)
    """
    
    def create_chat(
        self,
        first_message: Optional[str] = None,
        first_message_role: str = "user"
    ) -> int:
        """
        Create a new chat, optionally with a first message.
        
        Args:
            first_message: Optional initial message content
            first_message_role: Role for first message ("user", "system", "assistant")
            
        Returns:
            Chat ID
        """
        with get_session() as session:
            chat = ChatRepository.create(session)
            
            if first_message:
                role = MessageRole(first_message_role)
                MessageRepository.create(
                    session=session,
                    chat_id=chat.id,
                    role=role,
                    content=first_message
                )
            
            return chat.id
    
    def add_message(
        self,
        chat_id: int,
        role: MessageRole,
        content: str,
        agent_type: Optional[str] = None
    ) -> int:
        """
        Add a message to a chat.
        
        Args:
            chat_id: ID of the chat
            role: Message role ("user", "system", "assistant")
            content: Message content
            agent_type: For assistant messages, the agent type ("deepseek-r1", "llava", "phi3")
            
        Returns:
            Message ID
        """
        with get_session() as session:
            chat = ChatRepository.get_by_id(session, chat_id)
            if not chat:
                raise ValueError(f"Chat not found: {chat_id}")
            
            msg_role = MessageRole(role)
            msg_agent_type = AgentType(agent_type) if agent_type else None
            
            message = MessageRepository.create(
                session=session,
                chat_id=chat_id,
                role=msg_role,
                content=content,
                agent_type=msg_agent_type
            )
            
            # Increment step count for assistant messages
            if msg_role == MessageRole.ASSISTANT:
                ChatRepository.increment_step_count(session, chat_id)
            
            return message.id
    
    def remove_message(self, message_id: int) -> bool:
        """
        Remove a message.
        
        Args:
            message_id: ID of the message to remove
            
        Returns:
            True if removed, False if not found
        """
        with get_session() as session:
            return MessageRepository.delete(session, message_id)
    
    def get_context(self, chat_id: int) -> List[Dict[str, Any]]:
        """
        Get chat context for LLM (all messages formatted as role/content dicts).
        
        Args:
            chat_id: ID of the chat
            
        Returns:
            List of message dicts with 'role' and 'content' keys
        """
        with get_session() as session:
            return MessageRepository.get_context(session, chat_id)
    
    def delete_chat(self, chat_id: int) -> bool:
        """
        Delete a chat and all its messages.
        
        Args:
            chat_id: ID of the chat to delete
            
        Returns:
            True if deleted, False if not found
        """
        with get_session() as session:
            return ChatRepository.delete(session, chat_id)
    
    def get_chat_info(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """
        Get basic chat info.
        
        Returns:
            Dict with chat info or None if not found
        """
        with get_session() as session:
            chat = ChatRepository.get_by_id(session, chat_id)
            if not chat:
                return None
            
            return {
                "id": chat.id,
                "step_count": chat.step_count,
                "is_active": chat.is_active,
                "message_count": len(chat.messages),
                "created_at": chat.created_at
            }


# Global instance for convenience
session_manager = SessionManager()
