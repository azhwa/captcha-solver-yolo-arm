from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

class ExpirationTypeEnum(str, Enum):
    NEVER = "never"
    DATE = "date"
    DURATION = "duration"

# API Key Schemas
class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    key_value: Optional[str] = None  # Auto-generate if None
    expiration_type: ExpirationTypeEnum = ExpirationTypeEnum.NEVER
    expires_at: Optional[datetime] = None  # For type=date
    duration_days: Optional[int] = None  # For type=duration
    daily_limit: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None

class ApiKeyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    daily_limit: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class ApiKeyRenew(BaseModel):
    expiration_type: ExpirationTypeEnum
    expires_at: Optional[datetime] = None
    duration_days: Optional[int] = None

class ApiKeyResponse(BaseModel):
    id: int
    name: str
    key_value: str
    created_at: datetime
    last_used_at: Optional[datetime]
    is_active: bool
    request_count: int
    daily_limit: Optional[int]
    expires_at: Optional[datetime]
    expiration_type: str
    notes: Optional[str]
    created_by: str
    
    class Config:
        from_attributes = True

class ApiKeyListResponse(BaseModel):
    id: int
    name: str
    key_value_preview: str  # First 8 + last 4 chars
    created_at: datetime
    last_used_at: Optional[datetime]
    is_active: bool
    request_count: int
    expires_at: Optional[datetime]
    expiration_status: str  # "never", "active", "expiring", "expired"
    days_until_expiry: Optional[int]
    
    class Config:
        from_attributes = True

# Model File Schemas
class ModelFileUpload(BaseModel):
    description: Optional[str] = None

class ModelFileResponse(BaseModel):
    id: int
    filename: str
    file_size_mb: float
    uploaded_at: datetime
    is_active: bool
    uploaded_by: str
    description: Optional[str]
    
    class Config:
        from_attributes = True

# Admin Auth Schemas
class AdminLogin(BaseModel):
    username: str
    password: str

class AdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8)
    email: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

# Statistics Schemas
class DashboardStats(BaseModel):
    total_requests_today: int
    total_requests_week: int
    total_requests_month: int
    success_rate: float
    avg_response_time_ms: float
    active_keys_count: int
    total_keys_count: int
    expiring_keys_count: int
    current_model: Optional[ModelFileResponse]

class RequestLogResponse(BaseModel):
    id: int
    api_key_name: str
    endpoint: str
    status_code: int
    response_time_ms: float
    timestamp: datetime
    ip_address: Optional[str]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True

# Test Interface Schema
class DetectionTestRequest(BaseModel):
    api_key_id: int
    include_visual: bool = True
    save_file: bool = False
