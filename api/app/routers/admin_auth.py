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
    pwd_context,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/admin/auth", tags=["Admin Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(login_data: AdminLogin, db: Session = Depends(get_db)):
    """Admin login endpoint"""
    try:
        user = authenticate_admin(db, login_data.username, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username atau password salah. Silakan periksa kembali credentials Anda.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update last login and auto-upgrade deprecated hash
        try:
            user.last_login = datetime.utcnow()
            
            # Auto-upgrade password hash if using deprecated scheme (bcrypt -> pbkdf2)
            if pwd_context.needs_update(user.hashed_password):
                user.hashed_password = get_password_hash(login_data.password)
                print(f"✓ Auto-upgraded password hash for user: {user.username}")
            
            db.commit()
            db.refresh(user)
        except Exception as db_error:
            print(f"⚠ Warning: Failed to update user data: {db_error}")
            db.rollback()
            # Continue anyway - login still works
        
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
    except HTTPException:
        raise  # Re-raise HTTP exceptions (401, etc.)
    except Exception as e:
        error_type = type(e).__name__
        print(f"✗ Login error: {error_type}: {e}")
        
        # Specific error messages for different error types
        if "UnknownHashError" in error_type or "hash" in str(e).lower():
            detail = "Server error: Password hash tidak kompatibel. Silakan hubungi administrator."
        elif "database" in str(e).lower() or "sqlite" in str(e).lower():
            detail = "Server error: Database error. Silakan coba lagi."
        else:
            detail = f"Server error: Terjadi kesalahan saat login. ({error_type})"
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
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
