"""
Repository layer for database operations.

Provides high-level CRUD operations for all models.
Handles the translation between domain objects and database records.
"""
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.db.models import (
    Task, Chat, Message, Agent, ActionLog,
    TaskStatus, MessageRole, AgentType
)


class AgentRepository:
    """Repository for Agent operations"""
    
    @staticmethod
    def create(
        session: Session,
        name: str,
        agent_type: AgentType,
        model_name: str,
        description: Optional[str] = None,
        capabilities: Optional[dict] = None
    ) -> Agent:
        """Create a new agent"""
        agent = Agent(
            name=name,
            agent_type=agent_type,
            model_name=model_name,
            description=description,
            capabilities=capabilities
        )
        session.add(agent)
        session.flush()
        return agent
    
    @staticmethod
    def get_by_id(session: Session, agent_id: int) -> Optional[Agent]:
        """Get agent by ID"""
        return session.query(Agent).filter(Agent.id == agent_id).first()
    
    @staticmethod
    def get_by_type(session: Session, agent_type: AgentType) -> Optional[Agent]:
        """Get agent by type"""
        return session.query(Agent).filter(Agent.agent_type == agent_type).first()
    
    @staticmethod
    def get_or_create(
        session: Session,
        agent_type: AgentType,
        model_name: str
    ) -> Agent:
        """Get existing agent or create new one"""
        agent = AgentRepository.get_by_type(session, agent_type)
        if agent:
            return agent
        
        return AgentRepository.create(
            session=session,
            name=agent_type.value,
            agent_type=agent_type,
            model_name=model_name
        )
    
    @staticmethod
    def list_all(session: Session) -> List[Agent]:
        """List all agents"""
        return session.query(Agent).all()


class TaskRepository:
    """Repository for Task operations"""
    
    @staticmethod
    def create(
        session: Session,
        title: str,
        description: Optional[str] = None,
        website_url: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Task:
        """Create a new task"""
        task = Task(
            external_id=str(uuid.uuid4()),
            title=title,
            description=description,
            website_url=website_url,
            metadata=metadata,
            status=TaskStatus.PENDING
        )
        session.add(task)
        session.flush()
        return task
    
    @staticmethod
    def get_by_id(session: Session, task_id: int) -> Optional[Task]:
        """Get task by ID"""
        return session.query(Task).filter(Task.id == task_id).first()
    
    @staticmethod
    def get_by_external_id(session: Session, external_id: str) -> Optional[Task]:
        """Get task by external UUID"""
        return session.query(Task).filter(Task.external_id == external_id).first()
    
    @staticmethod
    def update_status(
        session: Session,
        task_id: int,
        status: TaskStatus
    ) -> Optional[Task]:
        """Update task status"""
        task = TaskRepository.get_by_id(session, task_id)
        if task:
            task.status = status
            if status == TaskStatus.COMPLETED:
                task.completed_at = datetime.utcnow()
            session.flush()
        return task
    
    @staticmethod
    def list_by_status(
        session: Session,
        status: Optional[TaskStatus] = None,
        limit: int = 100
    ) -> List[Task]:
        """List tasks, optionally filtered by status"""
        query = session.query(Task)
        if status:
            query = query.filter(Task.status == status)
        return query.order_by(desc(Task.created_at)).limit(limit).all()
    
    @staticmethod
    def delete(session: Session, task_id: int) -> bool:
        """Delete a task and all related data"""
        task = TaskRepository.get_by_id(session, task_id)
        if task:
            session.delete(task)
            return True
        return False


class ChatRepository:
    """Repository for Chat (Session) operations"""
    
    @staticmethod
    def create(
        session: Session,
        task_id: int,
        session_id: Optional[str] = None,
        context: Optional[dict] = None
    ) -> Chat:
        """Create a new chat session for a task"""
        chat = Chat(
            session_id=session_id or str(uuid.uuid4()),
            task_id=task_id,
            context=context,
            step_count=0
        )
        session.add(chat)
        session.flush()
        return chat
    
    @staticmethod
    def get_by_id(session: Session, chat_id: int) -> Optional[Chat]:
        """Get chat by ID"""
        return session.query(Chat).filter(Chat.id == chat_id).first()
    
    @staticmethod
    def get_by_session_id(session: Session, session_id: str) -> Optional[Chat]:
        """Get chat by session UUID"""
        return session.query(Chat).filter(Chat.session_id == session_id).first()
    
    @staticmethod
    def get_or_create(
        session: Session,
        session_id: str,
        task_id: int
    ) -> Chat:
        """Get existing chat or create new one"""
        chat = ChatRepository.get_by_session_id(session, session_id)
        if chat:
            return chat
        return ChatRepository.create(session, task_id, session_id)
    
    @staticmethod
    def increment_step_count(session: Session, chat_id: int) -> Optional[Chat]:
        """Increment the step count for a chat"""
        chat = ChatRepository.get_by_id(session, chat_id)
        if chat:
            chat.step_count += 1
            session.flush()
        return chat
    
    @staticmethod
    def list_by_task(
        session: Session,
        task_id: int,
        active_only: bool = False
    ) -> List[Chat]:
        """List all chats for a task"""
        query = session.query(Chat).filter(Chat.task_id == task_id)
        if active_only:
            query = query.filter(Chat.is_active == True)
        return query.order_by(desc(Chat.created_at)).all()
    
    @staticmethod
    def deactivate(session: Session, chat_id: int) -> Optional[Chat]:
        """Mark a chat as inactive"""
        chat = ChatRepository.get_by_id(session, chat_id)
        if chat:
            chat.is_active = False
            session.flush()
        return chat


class MessageRepository:
    """Repository for Message operations"""
    
    @staticmethod
    def create(
        session: Session,
        chat_id: int,
        role: MessageRole,
        content: str,
        agent_id: Optional[int] = None,
        image_refs: Optional[List[str]] = None,
        action_data: Optional[dict] = None,
        confidence: Optional[float] = None
    ) -> Message:
        """Create a new message"""
        message = Message(
            chat_id=chat_id,
            agent_id=agent_id,
            role=role,
            content=content,
            image_refs=image_refs,
            action_data=action_data,
            confidence=confidence
        )
        session.add(message)
        session.flush()
        return message
    
    @staticmethod
    def get_by_id(session: Session, message_id: int) -> Optional[Message]:
        """Get message by ID"""
        return session.query(Message).filter(Message.id == message_id).first()
    
    @staticmethod
    def list_by_chat(
        session: Session,
        chat_id: int,
        limit: Optional[int] = None
    ) -> List[Message]:
        """Get all messages for a chat, ordered by creation time"""
        query = session.query(Message).filter(
            Message.chat_id == chat_id
        ).order_by(Message.created_at)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_context_messages(
        session: Session,
        chat_id: int,
        include_system: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get messages formatted for LLM context.
        
        Returns list of dicts with 'role' and 'content' keys.
        """
        messages = MessageRepository.list_by_chat(session, chat_id)
        
        context = []
        for msg in messages:
            if not include_system and msg.role == MessageRole.SYSTEM:
                continue
            
            context.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        return context
    
    @staticmethod
    def count_by_chat(session: Session, chat_id: int) -> int:
        """Count messages in a chat"""
        return session.query(Message).filter(Message.chat_id == chat_id).count()


class ActionLogRepository:
    """Repository for ActionLog operations"""
    
    @staticmethod
    def create(
        session: Session,
        message_id: int,
        action_type: str,
        element_description: Optional[str] = None,
        coordinates: Optional[dict] = None,
        text_input: Optional[str] = None,
        confidence: float = 1.0
    ) -> ActionLog:
        """Create a new action log entry"""
        action_log = ActionLog(
            message_id=message_id,
            action_type=action_type,
            element_description=element_description,
            coordinates=coordinates,
            text_input=text_input,
            confidence=confidence
        )
        session.add(action_log)
        session.flush()
        return action_log
    
    @staticmethod
    def update_result(
        session: Session,
        action_log_id: int,
        success: bool,
        error_message: Optional[str] = None
    ) -> Optional[ActionLog]:
        """Update action log with execution result"""
        action_log = session.query(ActionLog).filter(
            ActionLog.id == action_log_id
        ).first()
        
        if action_log:
            action_log.success = success
            action_log.error_message = error_message
            session.flush()
        
        return action_log
    
    @staticmethod
    def list_by_message(session: Session, message_id: int) -> List[ActionLog]:
        """Get all action logs for a message"""
        return session.query(ActionLog).filter(
            ActionLog.message_id == message_id
        ).order_by(ActionLog.created_at).all()

