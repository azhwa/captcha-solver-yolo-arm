from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.db_models import ModelFile

def create_model_file(
    db: Session,
    filename: str,
    file_path: str,
    file_size_mb: float,
    uploaded_by: str = "admin",
    description: str = None
) -> ModelFile:
    model_file = ModelFile(
        filename=filename,
        file_path=file_path,
        file_size_mb=file_size_mb,
        uploaded_by=uploaded_by,
        description=description
    )
    db.add(model_file)
    db.commit()
    db.refresh(model_file)
    return model_file

def get_model_files(db: Session) -> List[ModelFile]:
    return db.query(ModelFile).order_by(ModelFile.uploaded_at.desc()).all()

def get_active_model(db: Session) -> Optional[ModelFile]:
    return db.query(ModelFile).filter(ModelFile.is_active == True).first()

def activate_model(db: Session, model_id: int) -> Optional[ModelFile]:
    try:
        # Deactivate all models
        db.query(ModelFile).update({ModelFile.is_active: False}, synchronize_session='fetch')
        
        # Activate the selected model
        model = db.query(ModelFile).filter(ModelFile.id == model_id).first()
        if model:
            model.is_active = True
            db.commit()
            db.refresh(model)
        return model
    except Exception as e:
        db.rollback()
        print(f"Error in activate_model: {e}")
        raise

def delete_model_file(db: Session, model_id: int) -> bool:
    model = db.query(ModelFile).filter(ModelFile.id == model_id).first()
    if not model or model.is_active:  # Don't delete active model
        return False
    db.delete(model)
    db.commit()
    return True
