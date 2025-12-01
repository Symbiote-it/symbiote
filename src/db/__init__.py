"""
Database module for Symbiote session management.

Provides database models, connection management, and session manager
for storing chat history and messages.
"""
from src.db.models import (
    Base,
    Chat, 
    Message,
    MessageRole,
    AgentType
)
from src.db.connection import (
    engine,
    SessionLocal,
    get_session,
    get_db,
    init_db,
    drop_db,
    check_connection,
    get_database_url
)
from src.db.repository import (
    ChatRepository,
    MessageRepository
)
from src.db.session_manager import SessionManager, session_manager


__all__ = [
    # Models
    "Base",
    "Chat", 
    "Message",
    
    # Enums
    "MessageRole",
    "AgentType",
    
    # Connection
    "engine",
    "SessionLocal",
    "get_session",
    "get_db",
    "init_db",
    "drop_db",
    "check_connection",
    "get_database_url",
    
    # Repositories
    "ChatRepository",
    "MessageRepository",
    
    # Session Manager
    "SessionManager",
    "session_manager",
]
