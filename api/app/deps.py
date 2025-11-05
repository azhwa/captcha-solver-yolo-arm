from fastapi import HTTPException, Security, Depends, Request
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_429_TOO_MANY_REQUESTS
from sqlalchemy.orm import Session
from datetime import datetime
from .config import settings
from .database import get_db
from .crud.api_keys import get_api_key_by_value
from .crud.logs import get_today_request_count

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(
    request: Request,
    api_key_header: str = Security(api_key_header),
    db: Session = Depends(get_db)
):
    """Validate API key from database with expiration and rate limit checks"""
    if not api_key_header:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, 
            detail="API key is missing. Please create an API key via the dashboard."
        )
    
    # Get key from database
    key_record = get_api_key_by_value(db, api_key_header)
    if not key_record:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, 
            detail="Invalid API key. Please check your key or create a new one via the dashboard."
        )
    
    # Check if active
    if not key_record.is_active:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, 
            detail="API key is disabled"
        )
    
    # Check if expired
    if key_record.expires_at:
        if datetime.utcnow() > key_record.expires_at:
            # Auto-disable expired key
            key_record.is_active = False
            db.commit()
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, 
                detail="API key has expired"
            )
    
    # Check daily limit
    if key_record.daily_limit and key_record.daily_limit > 0:
        today_requests = get_today_request_count(db, key_record.id)
        if today_requests >= key_record.daily_limit:
            raise HTTPException(
                status_code=HTTP_429_TOO_MANY_REQUESTS, 
                detail=f"Daily request limit ({key_record.daily_limit}) exceeded"
            )
    
    # Update last_used_at and increment counter
    key_record.last_used_at = datetime.utcnow()
    key_record.request_count += 1
    db.commit()
    
    # Store key info in request state for logging
    request.state.api_key_id = key_record.id
    
    return api_key_header