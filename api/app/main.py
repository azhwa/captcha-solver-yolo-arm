from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from .config import settings
from .deps import get_api_key
from .database import Base, engine, get_db
from .models.db_models import AdminUser
from .auth import get_password_hash

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    Base.metadata.create_all(bind=engine)
    
    db = next(get_db())
    try:
        # Clean orphaned request logs (migration fix for NOT NULL constraint)
        from sqlalchemy import text
        result = db.execute(text(
            "DELETE FROM request_logs WHERE api_key_id IS NULL OR "
            "api_key_id NOT IN (SELECT id FROM api_keys)"
        ))
        deleted_count = result.rowcount
        if deleted_count > 0:
            db.commit()
            print(f"✓ Database migration: Cleaned {deleted_count} orphaned request logs")
        
        # Sync admin user with .env credentials on every startup
        # Always update FIRST admin (single admin mode)
        admin = db.query(AdminUser).order_by(AdminUser.id).first()
        
        if not admin:
            # Create first admin from .env
            admin = AdminUser(
                username=settings.ADMIN_USERNAME,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                email=settings.ADMIN_EMAIL if settings.ADMIN_EMAIL else None
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"✓ Admin created from .env: {settings.ADMIN_USERNAME}")
        else:
            # Update existing FIRST admin with .env credentials
            updated = False
            
            # Update username if changed
            if admin.username != settings.ADMIN_USERNAME:
                admin.username = settings.ADMIN_USERNAME
                updated = True
                print(f"✓ Admin username updated: {settings.ADMIN_USERNAME}")
            
            # Update password if changed
            from .auth import verify_password
            try:
                if not verify_password(settings.ADMIN_PASSWORD, admin.hashed_password):
                    admin.hashed_password = get_password_hash(settings.ADMIN_PASSWORD)
                    updated = True
                    print(f"✓ Admin password updated from .env")
            except:
                admin.hashed_password = get_password_hash(settings.ADMIN_PASSWORD)
                updated = True
                print(f"✓ Admin password force-updated from .env")
            
            # Update email if changed (optional)
            new_email = settings.ADMIN_EMAIL if settings.ADMIN_EMAIL else None
            if admin.email != new_email:
                admin.email = new_email
                updated = True
                if new_email:
                    print(f"✓ Admin email updated: {new_email}")
                else:
                    print(f"✓ Admin email cleared (not configured)")
            
            if updated:
                db.commit()
                db.refresh(admin)
            else:
                print(f"✓ Admin synced: {admin.username}")
    except Exception as e:
        print(f"⚠ Startup warning: {e}")
    finally:
        db.close()
    
    yield
    # Shutdown
    pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Log request if API key is present
    if hasattr(request.state, "api_key_id"):
        process_time = (time.time() - start_time) * 1000  # ms
        
        # Get database session
        db = next(get_db())
        from .crud.logs import create_request_log
        
        try:
            create_request_log(
                db,
                api_key_id=request.state.api_key_id,
                endpoint=request.url.path,
                status_code=response.status_code,
                response_time_ms=round(process_time, 2),
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )
        except Exception as e:
            print(f"Failed to log request: {e}")
        finally:
            db.close()
    
    return response

@app.get("/")
async def root():
    """Health check endpoint - always returns 200 OK"""
    return {"message": "Welcome to Captcha Solver API", "version": "2.0", "status": "running"}

# Import and include routers
from .routers import captcha, admin_auth, admin_keys, admin_models, admin_stats

# Public API routes (requires API key)
app.include_router(
    captcha.router,
    prefix=settings.API_V1_STR,
    dependencies=[Depends(get_api_key)]
)

# Admin routes (requires JWT)
app.include_router(admin_auth.router)
app.include_router(admin_keys.router)
app.include_router(admin_models.router)
app.include_router(admin_stats.router)