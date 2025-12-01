"""
Database models for Symbiote session management.

Relationships:
- A Task can have multiple Chats (sessions)
- A Chat belongs to one Task
- A Chat can have multiple Messages
- A Message is associated with one Agent
- Multiple Agents can work on a single Task through different messages
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, 
    Text, 
    DateTime, 
    ForeignKey, 
    JSON,
    Enum as SQLEnum,
    Float,
    Integer
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class TaskStatus(enum.Enum):
    """Status of a testing task"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessageRole(enum.Enum):
    """Role of message sender"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class AgentType(enum.Enum):
    """Types of agents available"""
    DEEPSEEK_R1 = "deepseek-r1"
    LLAVA = "llava"
    PHI3 = "phi3"


class Agent(Base):
    """
    Represents an AI agent that can work on tasks.
    Tracks agent metadata and capabilities.
    """
    __tablename__ = "agents"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    agent_type: Mapped[AgentType] = mapped_column(SQLEnum(AgentType), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    capabilities: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="agent")
    
    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, name='{self.name}', type={self.agent_type.value})>"


class Task(Base):
    """
    Represents a testing task that can have multiple chat sessions.
    A task defines what needs to be tested (e.g., "Test GitHub search functionality").
    """
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus), 
        default=TaskStatus.PENDING,
        nullable=False
    )
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    chats: Mapped[List["Chat"]] = relationship(
        "Chat", 
        back_populates="task",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title[:30]}...', status={self.status.value})>"


class Chat(Base):
    """
    Represents a chat session within a task.
    Multiple agents can participate in a single chat session.
    """
    __tablename__ = "chats"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    step_count: Mapped[int] = mapped_column(Integer, default=0)
    context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # Relationships
    task: Mapped["Task"] = relationship("Task", back_populates="chats")
    messages: Mapped[List["Message"]] = relationship(
        "Message", 
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )
    
    def __repr__(self) -> str:
        return f"<Chat(id={self.id}, session_id='{self.session_id}', steps={self.step_count})>"


class Message(Base):
    """
    Represents a single message in a chat session.
    Each message is associated with an agent (for assistant messages).
    """
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    agent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agents.id"), nullable=True)
    role: Mapped[MessageRole] = mapped_column(SQLEnum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # For storing image data references (not the actual base64)
    image_refs: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Action metadata for assistant responses
    action_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
    agent: Mapped[Optional["Agent"]] = relationship("Agent", back_populates="messages")
    
    def __repr__(self) -> str:
        content_preview = self.content[:50] if self.content else ""
        return f"<Message(id={self.id}, role={self.role.value}, content='{content_preview}...')>"


class ActionLog(Base):
    """
    Logs specific actions taken during testing.
    Provides detailed tracking of what actions were performed.
    """
    __tablename__ = "action_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    element_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    coordinates: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    text_input: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    success: Mapped[Optional[bool]] = mapped_column(default=None, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    message: Mapped["Message"] = relationship("Message")
    
    def __repr__(self) -> str:
        return f"<ActionLog(id={self.id}, action={self.action_type}, success={self.success})>"

