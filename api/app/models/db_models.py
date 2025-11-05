from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base

class ExpirationType(str, enum.Enum):
    NEVER = "never"
    DATE = "date"
    DURATION = "duration"

class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    key_value = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    request_count = Column(Integer, default=0)
    daily_limit = Column(Integer, nullable=True)  # null = unlimited
    expires_at = Column(DateTime, nullable=True, index=True)  # null = never expire
    expiration_type = Column(Enum(ExpirationType), default=ExpirationType.NEVER)
    expiration_notified = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_by = Column(String(255), default="admin")
    
    # Relationship
    request_logs = relationship("RequestLog", back_populates="api_key")

class RequestLog(Base):
    __tablename__ = "request_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=False)
    endpoint = Column(String(255), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    
    # Relationship
    api_key = relationship("ApiKey", back_populates="request_logs")

class ModelFile(Base):
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), unique=True, nullable=False)
    file_size_mb = Column(Float, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=False, index=True)
    uploaded_by = Column(String(255), default="admin")
    description = Column(Text, nullable=True)

class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
