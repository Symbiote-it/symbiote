"""
Database module for Symbiote session management.

Provides database models, connection management, and repositories
for storing chat history, tasks, and agent interactions.
"""
from src.db.models import (
    Base,
    Task, 
    Chat, 
    Message, 
    Agent, 
    ActionLog,
    TaskStatus,
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
    TaskRepository,
    ChatRepository,
    MessageRepository,
    AgentRepository,
    ActionLogRepository
)
from src.db.session_manager import SessionManager, session_manager


__all__ = [
    # Models
    "Base",
    "Task",
    "Chat", 
    "Message",
    "Agent",
    "ActionLog",
    
    # Enums
    "TaskStatus",
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
    "TaskRepository",
    "ChatRepository",
    "MessageRepository",
    "AgentRepository",
    "ActionLogRepository",
    
    # Session Manager
    "SessionManager",
    "session_manager",
]

