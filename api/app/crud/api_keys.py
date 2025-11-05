from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import List, Optional
import secrets
from ..models.db_models import ApiKey, ExpirationType
from ..models.schemas import ApiKeyCreate, ApiKeyUpdate, ApiKeyRenew

def generate_api_key() -> str:
    """Generate a secure random API key"""
    return f"sk_{secrets.token_urlsafe(32)}"

def create_api_key(db: Session, key_data: ApiKeyCreate, created_by: str = "admin") -> ApiKey:
    """Create a new API key"""
    key_value = key_data.key_value or generate_api_key()
    
    expires_at = None
    if key_data.expiration_type == ExpirationType.DATE:
        expires_at = key_data.expires_at
    elif key_data.expiration_type == ExpirationType.DURATION:
        if key_data.duration_days:
            expires_at = datetime.utcnow() + timedelta(days=key_data.duration_days)
    
    db_key = ApiKey(
        name=key_data.name,
        key_value=key_value,
        expiration_type=key_data.expiration_type,
        expires_at=expires_at,
        daily_limit=key_data.daily_limit,
        notes=key_data.notes,
        created_by=created_by
    )
    
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key

def get_api_key(db: Session, key_id: int) -> Optional[ApiKey]:
    return db.query(ApiKey).filter(ApiKey.id == key_id).first()

def get_api_key_by_value(db: Session, key_value: str) -> Optional[ApiKey]:
    return db.query(ApiKey).filter(ApiKey.key_value == key_value).first()

def get_api_keys(db: Session, skip: int = 0, limit: int = 100, filter_status: Optional[str] = None) -> List[ApiKey]:
    query = db.query(ApiKey)
    
    if filter_status == "active":
        query = query.filter(ApiKey.is_active == True)
    elif filter_status == "expired":
        query = query.filter(and_(ApiKey.expires_at != None, ApiKey.expires_at < datetime.utcnow()))
    elif filter_status == "expiring":
        now = datetime.utcnow()
        future = now + timedelta(days=7)
        query = query.filter(and_(ApiKey.expires_at != None, ApiKey.expires_at.between(now, future)))
    
    return query.order_by(ApiKey.created_at.desc()).offset(skip).limit(limit).all()

def update_api_key(db: Session, key_id: int, key_data: ApiKeyUpdate) -> Optional[ApiKey]:
    db_key = get_api_key(db, key_id)
    if not db_key:
        return None
    
    update_data = key_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_key, field, value)
    
    db.commit()
    db.refresh(db_key)
    return db_key

def delete_api_key(db: Session, key_id: int) -> bool:
    db_key = get_api_key(db, key_id)
    if not db_key:
        return False
    db.delete(db_key)
    db.commit()
    return True

def renew_api_key(db: Session, key_id: int, renew_data: ApiKeyRenew) -> Optional[ApiKey]:
    db_key = get_api_key(db, key_id)
    if not db_key:
        return None
    
    if renew_data.expiration_type == ExpirationType.NEVER:
        db_key.expires_at = None
        db_key.expiration_type = ExpirationType.NEVER
    elif renew_data.expiration_type == ExpirationType.DATE:
        db_key.expires_at = renew_data.expires_at
        db_key.expiration_type = ExpirationType.DATE
    elif renew_data.expiration_type == ExpirationType.DURATION:
        if renew_data.duration_days:
            db_key.expires_at = datetime.utcnow() + timedelta(days=renew_data.duration_days)
            db_key.expiration_type = ExpirationType.DURATION
    
    if not db_key.is_active:
        db_key.is_active = True
    
    db_key.expiration_notified = False
    db.commit()
    db.refresh(db_key)
    return db_key

def get_expiring_keys(db: Session, days: int = 7) -> List[ApiKey]:
    now = datetime.utcnow()
    future = now + timedelta(days=days)
    return db.query(ApiKey).filter(
        and_(ApiKey.is_active == True, ApiKey.expires_at != None, ApiKey.expires_at.between(now, future))
    ).all()
