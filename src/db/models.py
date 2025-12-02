"""
Database models for Symbiote session management.

Relationships:
- A Chat can have multiple Messages
- A Message belongs to one Chat
- A Message can be from user, system, or an agent (assistant)
"""
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Text, 
    DateTime, 
    ForeignKey, 
    Enum as SQLEnum,
    Integer
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


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


class Chat(Base):
    """
    Represents a chat session.
    Multiple agents can participate in a single chat session.
    """
    __tablename__ = "chats"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    step_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    messages: Mapped[List["Message"]] = relationship(
        "Message", 
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )
    
    def __repr__(self) -> str:
        return f"<Chat(id={self.id}, steps={self.step_count})>"


class Message(Base):
    """
    Represents a single message in a chat session.
    Each message is associated with an agent (for assistant messages) or with a user.
    """
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    role: Mapped[MessageRole] = mapped_column(SQLEnum(MessageRole), nullable=False)
    agent_type: Mapped[Optional[AgentType]] = mapped_column(SQLEnum(AgentType), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
    
    def __repr__(self) -> str:
        content_preview = self.content[:50] if self.content else ""
        return f"<Message(id={self.id}, role={self.role.value}, content='{content_preview}...')>"
