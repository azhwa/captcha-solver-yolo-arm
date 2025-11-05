from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional
from ..database import get_db
from ..models.schemas import DashboardStats, RequestLogResponse
from ..models.db_models import AdminUser, ApiKey, RequestLog, ModelFile
from ..auth import get_current_admin
from ..crud import logs as crud_logs
from ..crud import models as crud_models

router = APIRouter(prefix="/admin/stats", tags=["Admin - Statistics"])

@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Get dashboard statistics"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)
    
    # Total requests
    total_requests_today = db.query(func.count(RequestLog.id)).filter(
        RequestLog.timestamp >= today_start
    ).scalar() or 0
    
    total_requests_week = db.query(func.count(RequestLog.id)).filter(
        RequestLog.timestamp >= week_start
    ).scalar() or 0
    
    total_requests_month = db.query(func.count(RequestLog.id)).filter(
        RequestLog.timestamp >= month_start
    ).scalar() or 0
    
    # Success rate
    total_requests = db.query(func.count(RequestLog.id)).scalar() or 0
    successful_requests = db.query(func.count(RequestLog.id)).filter(
        RequestLog.status_code == 200
    ).scalar() or 0
    success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 100.0
    
    # Average response time
    avg_response_time = db.query(func.avg(RequestLog.response_time_ms)).scalar() or 0
    
    # API keys count
    active_keys_count = db.query(func.count(ApiKey.id)).filter(
        ApiKey.is_active == True
    ).scalar() or 0
    
    total_keys_count = db.query(func.count(ApiKey.id)).scalar() or 0
    
    # Expiring keys
    future_7_days = now + timedelta(days=7)
    expiring_keys_count = db.query(func.count(ApiKey.id)).filter(
        ApiKey.is_active == True,
        ApiKey.expires_at != None,
        ApiKey.expires_at.between(now, future_7_days)
    ).scalar() or 0
    
    # Current model
    current_model = crud_models.get_active_model(db)
    
    # Check if model file exists
    from ..detector import get_model
    model_available = get_model() is not None
    
    return DashboardStats(
        total_requests_today=total_requests_today,
        total_requests_week=total_requests_week,
        total_requests_month=total_requests_month,
        success_rate=round(success_rate, 2),
        avg_response_time_ms=round(avg_response_time, 2),
        active_keys_count=active_keys_count,
        total_keys_count=total_keys_count,
        expiring_keys_count=expiring_keys_count,
        current_model=current_model
    )

@router.get("/logs", response_model=List[RequestLogResponse])
async def get_request_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    api_key_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Get request logs with pagination"""
    logs = crud_logs.get_request_logs(db, skip=skip, limit=limit, api_key_id=api_key_id)
    
    result = []
    for log in logs:
        api_key = db.query(ApiKey).filter(ApiKey.id == log.api_key_id).first()
        result.append(RequestLogResponse(
            id=log.id,
            api_key_name=api_key.name if api_key else "Unknown",
            endpoint=log.endpoint,
            status_code=log.status_code,
            response_time_ms=log.response_time_ms,
            timestamp=log.timestamp,
            ip_address=log.ip_address,
            error_message=log.error_message
        ))
    
    return result
