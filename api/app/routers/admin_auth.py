from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..database import get_db
from ..models.schemas import AdminLogin, TokenResponse, AdminCreate
from ..models.db_models import AdminUser
from ..auth import (
    authenticate_admin,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/admin/auth", tags=["Admin Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(login_data: AdminLogin, db: Session = Depends(get_db)):
    """Admin login endpoint"""
    user = authenticate_admin(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.now()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/register", response_model=dict, include_in_schema=False)
async def register_admin(admin_data: AdminCreate, db: Session = Depends(get_db)):
    """Register first admin user (disable in production)"""
    # Check if admin already exists
    existing = db.query(AdminUser).first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin already exists")
    
    hashed_password = get_password_hash(admin_data.password)
    admin = AdminUser(
        username=admin_data.username,
        hashed_password=hashed_password,
        email=admin_data.email
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    return {"message": "Admin created successfully", "username": admin.username}
