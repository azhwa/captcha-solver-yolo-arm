from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
from typing import List
from ..models.db_models import RequestLog, ApiKey

def create_request_log(
    db: Session,
    api_key_id: int,
    endpoint: str,
    status_code: int,
    response_time_ms: float,
    ip_address: str = None,
    user_agent: str = None,
    error_message: str = None,
    file_size_bytes: int = None
) -> RequestLog:
    log = RequestLog(
        api_key_id=api_key_id,
        endpoint=endpoint,
        status_code=status_code,
        response_time_ms=response_time_ms,
        ip_address=ip_address,
        user_agent=user_agent,
        error_message=error_message,
        file_size_bytes=file_size_bytes
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_request_logs(db: Session, skip: int = 0, limit: int = 50, api_key_id: int = None) -> List[RequestLog]:
    query = db.query(RequestLog)
    if api_key_id:
        query = query.filter(RequestLog.api_key_id == api_key_id)
    return query.order_by(RequestLog.timestamp.desc()).offset(skip).limit(limit).all()

def get_today_request_count(db: Session, api_key_id: int) -> int:
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    return db.query(func.count(RequestLog.id)).filter(
        and_(RequestLog.api_key_id == api_key_id, RequestLog.timestamp >= today_start)
    ).scalar()
