from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from ..database import get_db
from ..models.schemas import (
    ApiKeyCreate, ApiKeyUpdate, ApiKeyRenew, 
    ApiKeyResponse, ApiKeyListResponse
)
from ..models.db_models import AdminUser
from ..auth import get_current_admin
from ..crud import api_keys as crud
from ..models.db_models import ApiKey

router = APIRouter(prefix="/admin/keys", tags=["Admin - API Keys"])

def format_key_list_response(key) -> ApiKeyListResponse:
    """Format API key for list view"""
    # Preview: first 8 + last 4 characters
    key_preview = f"{key.key_value[:8]}...{key.key_value[-4:]}"
    
    # Determine expiration status
    expiration_status = "never"
    days_until_expiry = None
    
    if key.expires_at:
        now = datetime.utcnow()
        if key.expires_at < now:
            expiration_status = "expired"
            days_until_expiry = 0
        else:
            days_until_expiry = (key.expires_at - now).days
            if days_until_expiry < 7:
                expiration_status = "expiring"
            else:
                expiration_status = "active"
    
    return ApiKeyListResponse(
        id=key.id,
        name=key.name,
        key_value_preview=key_preview,
        created_at=key.created_at,
        last_used_at=key.last_used_at,
        is_active=key.is_active,
        request_count=key.request_count,
        expires_at=key.expires_at,
        expiration_status=expiration_status,
        days_until_expiry=days_until_expiry
    )

@router.get("", response_model=List[ApiKeyListResponse])
async def list_api_keys(
    filter_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """List all API keys"""
    keys = crud.get_api_keys(db, filter_status=filter_status)
    return [format_key_list_response(key) for key in keys]

@router.post("", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Create a new API key"""
    # Check if name already exists
    existing = db.query(ApiKey).filter(ApiKey.name == key_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="API key name already exists")
    
    key = crud.create_api_key(db, key_data, created_by=current_admin.username)
    return key

@router.get("/{key_id}", response_model=ApiKeyResponse)
async def get_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Get API key details"""
    key = crud.get_api_key(db, key_id)
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    return key

@router.put("/{key_id}", response_model=ApiKeyResponse)
async def update_api_key(
    key_id: int,
    key_data: ApiKeyUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Update API key"""
    key = crud.update_api_key(db, key_id, key_data)
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    return key

@router.patch("/{key_id}/renew", response_model=ApiKeyResponse)
async def renew_api_key(
    key_id: int,
    renew_data: ApiKeyRenew,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Renew/extend API key expiration"""
    key = crud.renew_api_key(db, key_id, renew_data)
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    return key

@router.patch("/{key_id}/toggle", response_model=ApiKeyResponse)
async def toggle_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Toggle API key active status"""
    key = crud.get_api_key(db, key_id)
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    key.is_active = not key.is_active
    db.commit()
    db.refresh(key)
    return key

@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Delete API key"""
    success = crud.delete_api_key(db, key_id)
    if not success:
        raise HTTPException(status_code=404, detail="API key not found")
    return None

@router.get("/expiring/soon", response_model=List[ApiKeyListResponse])
async def get_expiring_keys(
    days: int = 7,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Get API keys expiring in N days"""
    keys = crud.get_expiring_keys(db, days=days)
    return [format_key_list_response(key) for key in keys]
