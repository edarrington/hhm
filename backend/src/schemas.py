"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional


# Household Schemas
class HouseholdCreate(BaseModel):
    """Create household request"""
    name: str


class HouseholdUpdate(BaseModel):
    """Update household request"""
    name: Optional[str] = None
    timezone: Optional[str] = None


class HouseholdResponse(BaseModel):
    """Household response"""
    id: UUID
    name: str
    timezone: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Household Member Schemas
class HouseholdMemberCreate(BaseModel):
    """Create household member request"""
    user_id: str
    name: str
    email: Optional[EmailStr] = None
    role: str = "member"


class HouseholdMemberUpdate(BaseModel):
    """Update household member request"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class HouseholdMemberResponse(BaseModel):
    """Household member response"""
    id: UUID
    household_id: UUID
    user_id: str
    name: str
    email: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Authentication Schemas
class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginRequest(BaseModel):
    """Login request"""
    household_id: UUID
    email: EmailStr
    user_id: str


# Memory Schemas
class MemoryCreate(BaseModel):
    """Create memory request"""
    memory_type: str  # fact, event, preference, relationship
    content: str
    metadata: Optional[dict] = None


class MemoryResponse(BaseModel):
    """Memory response"""
    id: UUID
    household_id: UUID
    memory_type: str
    content: str
    metadata: dict
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Conversation Schemas
class MessageCreate(BaseModel):
    """Create message request"""
    role: str  # user, assistant
    content: str


class MessageResponse(BaseModel):
    """Message response"""
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Conversation response"""
    id: UUID
    household_id: UUID
    user_id: UUID
    mode: str
    created_at: datetime
    updated_at: datetime
    messages: Optional[list[MessageResponse]] = None
    
    class Config:
        from_attributes = True


# Integration Schemas
class IntegrationResponse(BaseModel):
    """Integration response"""
    id: UUID
    household_id: UUID
    integration_type: str
    is_connected: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Health Check
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
