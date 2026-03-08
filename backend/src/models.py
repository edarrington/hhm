"""Database configuration and models"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()


class Household(Base):
    """Household record"""
    __tablename__ = "households"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Household preferences
    timezone = Column(String(50), default="UTC")
    settings = Column(JSON, default={})


class HouseholdMember(Base):
    """Household member (user)"""
    __tablename__ = "household_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.id"), nullable=False)
    user_id = Column(String(255), nullable=False)  # OAuth ID or user identifier
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    role = Column(String(50), default="member")  # admin, member
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Integration(Base):
    """OAuth tokens for household integrations"""
    __tablename__ = "integrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.id"), nullable=False)
    integration_type = Column(String(50), nullable=False)  # google_calendar, gmail, drive, todoist
    access_token = Column(Text)  # Encrypted
    refresh_token = Column(Text)  # Encrypted
    expires_at = Column(DateTime)
    is_connected = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class Conversation(Base):
    """Chat/voice conversation"""
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("household_members.id"), nullable=False)
    mode = Column(String(20), default="text")  # text, voice
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConversationMessage(Base):
    """Message in a conversation"""
    __tablename__ = "conversation_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Memory(Base):
    """Household memory (facts, events, preferences)"""
    __tablename__ = "memories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.id"), nullable=False)
    memory_type = Column(String(50), nullable=False)  # fact, event, preference, relationship
    content = Column(Text, nullable=False)
    meta = Column(JSON, default={})
    embedding = Column(JSON)  # Vector embedding for semantic search
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    """Operation audit log"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("household_members.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(255))
    details = Column(JSON, default={})
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
