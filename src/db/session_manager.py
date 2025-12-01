"""
Session Manager for Agent Clients.

Provides a high-level interface for managing chat sessions with database persistence.
This can be used as a drop-in replacement for the in-memory session management
in agent clients.
"""
import uuid
from typing import Optional, List, Dict, Any

from src.db.connection import get_session
from src.db.models import MessageRole, AgentType, TaskStatus
from src.db.repository import (
    TaskRepository,
    ChatRepository,
    MessageRepository,
    AgentRepository
)


class SessionManager:
    """
    Manages chat sessions with database persistence.
    
    Replaces in-memory session storage with database-backed storage.
    Supports multiple agents working on a single task.
    
    Usage:
        manager = SessionManager()
        
        # Create a task
        task_id = manager.create_task("Test GitHub search", "https://github.com")
        
        # Create a session for the task
        session_id = manager.create_session(task_id)
        
        # Add messages
        manager.add_system_message(session_id, "You are a helpful assistant...")
        manager.add_user_message(session_id, "Search for Python repos")
        manager.add_assistant_message(session_id, "Click on search...", agent_type=AgentType.DEEPSEEK_R1)
        
        # Get context for LLM
        context = manager.get_context(session_id)
    """
    
    def __init__(self):
        """Initialize SessionManager"""
        pass
    
    def create_task(
        self,
        title: str,
        website_url: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Create a new testing task.
        
        Returns:
            Task external_id (UUID string)
        """
        with get_session() as session:
            task = TaskRepository.create(
                session=session,
                title=title,
                description=description,
                website_url=website_url,
                metadata=metadata
            )
            return task.external_id
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by external ID"""
        with get_session() as session:
            task = TaskRepository.get_by_external_id(session, task_id)
            if not task:
                return None
            
            return {
                "id": task.external_id,
                "title": task.title,
                "description": task.description,
                "website_url": task.website_url,
                "status": task.status.value,
                "created_at": task.created_at,
                "updated_at": task.updated_at
            }
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Update task status"""
        with get_session() as session:
            task = TaskRepository.get_by_external_id(session, task_id)
            if task:
                TaskRepository.update_status(session, task.id, status)
                return True
            return False
    
    def create_session(
        self,
        task_id: str,
        session_id: Optional[str] = None,
        context: Optional[dict] = None
    ) -> str:
        """
        Create a new chat session for a task.
        
        Args:
            task_id: Task external_id
            session_id: Optional custom session ID
            context: Optional initial context data
            
        Returns:
            Session ID (UUID string)
        """
        with get_session() as session:
            task = TaskRepository.get_by_external_id(session, task_id)
            if not task:
                raise ValueError(f"Task not found: {task_id}")
            
            chat = ChatRepository.create(
                session=session,
                task_id=task.id,
                session_id=session_id or str(uuid.uuid4()),
                context=context
            )
            return chat.session_id
    
    def get_or_create_session(
        self,
        session_id: str,
        task_id: str
    ) -> str:
        """
        Get existing session or create new one.
        
        This mirrors the behavior of the old in-memory session management.
        """
        with get_session() as session:
            chat = ChatRepository.get_by_session_id(session, session_id)
            if chat:
                return chat.session_id
            
            task = TaskRepository.get_by_external_id(session, task_id)
            if not task:
                # Create task on the fly if it doesn't exist
                task = TaskRepository.create(
                    session=session,
                    title=f"Task {task_id}",
                    description="Auto-created task"
                )
            
            chat = ChatRepository.create(
                session=session,
                task_id=task.id,
                session_id=session_id
            )
            return chat.session_id
    
    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists"""
        with get_session() as session:
            chat = ChatRepository.get_by_session_id(session, session_id)
            return chat is not None
    
    def add_system_message(
        self,
        session_id: str,
        content: str
    ) -> int:
        """Add a system message to the session"""
        with get_session() as session:
            chat = ChatRepository.get_by_session_id(session, session_id)
            if not chat:
                raise ValueError(f"Session not found: {session_id}")
            
            message = MessageRepository.create(
                session=session,
                chat_id=chat.id,
                role=MessageRole.SYSTEM,
                content=content
            )
            return message.id
    
    def add_user_message(
        self,
        session_id: str,
        content: str,
        image_refs: Optional[List[str]] = None
    ) -> int:
        """Add a user message to the session"""
        with get_session() as session:
            chat = ChatRepository.get_by_session_id(session, session_id)
            if not chat:
                raise ValueError(f"Session not found: {session_id}")
            
            message = MessageRepository.create(
                session=session,
                chat_id=chat.id,
                role=MessageRole.USER,
                content=content,
                image_refs=image_refs
            )
            return message.id
    
    def add_assistant_message(
        self,
        session_id: str,
        content: str,
        agent_type: AgentType,
        model_name: str,
        action_data: Optional[dict] = None,
        confidence: Optional[float] = None
    ) -> int:
        """
        Add an assistant message to the session.
        
        Associates the message with the specified agent.
        """
        with get_session() as session:
            chat = ChatRepository.get_by_session_id(session, session_id)
            if not chat:
                raise ValueError(f"Session not found: {session_id}")
            
            # Get or create the agent
            agent = AgentRepository.get_or_create(
                session=session,
                agent_type=agent_type,
                model_name=model_name
            )
            
            message = MessageRepository.create(
                session=session,
                chat_id=chat.id,
                role=MessageRole.ASSISTANT,
                content=content,
                agent_id=agent.id,
                action_data=action_data,
                confidence=confidence
            )
            
            # Increment step count
            ChatRepository.increment_step_count(session, chat.id)
            
            return message.id
    
    def get_context(
        self,
        session_id: str,
        include_system: bool = True
    ) -> List[Dict[str, str]]:
        """
        Get conversation context for LLM.
        
        Returns messages formatted for LLM API calls.
        """
        with get_session() as session:
            chat = ChatRepository.get_by_session_id(session, session_id)
            if not chat:
                return []
            
            return MessageRepository.get_context_messages(
                session=session,
                chat_id=chat.id,
                include_system=include_system
            )
    
    def get_step_count(self, session_id: str) -> int:
        """Get current step count for a session"""
        with get_session() as session:
            chat = ChatRepository.get_by_session_id(session, session_id)
            if chat:
                return chat.step_count
            return 0
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        with get_session() as session:
            chat = ChatRepository.get_by_session_id(session, session_id)
            if not chat:
                return None
            
            return {
                "session_id": chat.session_id,
                "task_id": chat.task.external_id,
                "step_count": chat.step_count,
                "is_active": chat.is_active,
                "message_count": len(chat.messages),
                "created_at": chat.created_at,
                "updated_at": chat.updated_at
            }
    
    def list_sessions_for_task(self, task_id: str) -> List[Dict[str, Any]]:
        """List all sessions for a task"""
        with get_session() as session:
            task = TaskRepository.get_by_external_id(session, task_id)
            if not task:
                return []
            
            chats = ChatRepository.list_by_task(session, task.id)
            return [
                {
                    "session_id": chat.session_id,
                    "step_count": chat.step_count,
                    "is_active": chat.is_active,
                    "created_at": chat.created_at
                }
                for chat in chats
            ]
    
    def get_agents_for_task(self, task_id: str) -> List[Dict[str, Any]]:
        """
        Get all agents that have worked on a task.
        
        This shows the multi-agent nature of task execution.
        """
        with get_session() as session:
            task = TaskRepository.get_by_external_id(session, task_id)
            if not task:
                return []
            
            # Get unique agents from all messages in all chats
            agents_seen = set()
            agents = []
            
            for chat in task.chats:
                for message in chat.messages:
                    if message.agent and message.agent.id not in agents_seen:
                        agents_seen.add(message.agent.id)
                        agents.append({
                            "name": message.agent.name,
                            "type": message.agent.agent_type.value,
                            "model": message.agent.model_name
                        })
            
            return agents


# Global instance for convenience
session_manager = SessionManager()

