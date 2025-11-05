from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import shutil
import os
from ..database import get_db
from ..models.schemas import ModelFileResponse, ModelFileUpload
from ..models.db_models import AdminUser, ModelFile
from ..auth import get_current_admin
from ..crud import models as crud
from ..detector import get_model, _model

router = APIRouter(prefix="/admin/models", tags=["Admin - Models"])

# Models directory
MODELS_DIR = Path("/app/models") if os.path.exists("/app") else Path("./models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

@router.get("", response_model=List[ModelFileResponse])
async def list_models(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """List all model files"""
    return crud.get_model_files(db)

@router.post("/upload", response_model=ModelFileResponse, status_code=status.HTTP_201_CREATED)
async def upload_model(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Upload a new YOLO model file"""
    # Validate file extension
    if not file.filename.endswith('.pt'):
        raise HTTPException(status_code=400, detail="Only .pt model files are allowed")
    
    # Save file
    file_path = MODELS_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get file size
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    # Create database record
    model_file = crud.create_model_file(
        db,
        filename=file.filename,
        file_path=str(file_path),
        file_size_mb=round(file_size_mb, 2),
        uploaded_by=current_admin.username,
        description=description
    )
    
    return model_file

@router.patch("/{model_id}/activate", response_model=ModelFileResponse)
async def activate_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Set a model as active"""
    model = crud.activate_model(db, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Reload model in detector
    global _model
    _model = None  # Reset cached model
    
    # Update MODEL_PATH in config
    from ..config import settings
    settings.MODEL_PATH = model.file_path
    
    return model

@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Delete a model file"""
    model = db.query(ModelFile).filter(ModelFile.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if model.is_active:
        raise HTTPException(status_code=400, detail="Cannot delete active model")
    
    # Delete file from disk
    if os.path.exists(model.file_path):
        os.remove(model.file_path)
    
    # Delete from database
    success = crud.delete_model_file(db, model_id)
    if not success:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return None

@router.get("/{model_id}/download")
async def download_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Download a model file"""
    model = db.query(ModelFile).filter(ModelFile.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if not os.path.exists(model.file_path):
        raise HTTPException(status_code=404, detail="Model file not found on disk")
    
    return FileResponse(
        path=model.file_path,
        filename=model.filename,
        media_type="application/octet-stream"
    )
