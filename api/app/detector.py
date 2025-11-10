from ultralytics import YOLO
from .config import settings
import tempfile
import base64
import cv2
import numpy as np
import os
from datetime import datetime
from pathlib import Path

# Lazy-loaded model
_model = None
_model_load_error = None

def get_model():
    """Get YOLO model from database active model."""
    global _model, _model_load_error
    
    if _model is None and _model_load_error is None:
        try:
            # Import here to avoid circular dependency
            from .database import SessionLocal
            from .crud.models import get_active_model
            
            # Get active model from database
            db = SessionLocal()
            try:
                active_model = get_active_model(db)
                if not active_model:
                    _model_load_error = "No active model found. Please upload and activate a model via the admin dashboard."
                    print(f"⚠ WARNING: {_model_load_error}")
                    return None
                
                model_path = active_model.file_path
                print(f"📦 Using active model from database: {model_path}")
            finally:
                db.close()
            
            # Check if model file exists
            if not os.path.exists(model_path):
                _model_load_error = f"Model file not found at {model_path}. Please re-upload the model."
                print(f"⚠ WARNING: {_model_load_error}")
                return None
            
            # Check if path is directory
            if os.path.isdir(model_path):
                _model_load_error = f"Model path is a directory: {model_path}."
                print(f"⚠ WARNING: {_model_load_error}")
                return None
            
            # Load model
            _model = YOLO(model_path)
            print(f"✓ Model loaded successfully: {model_path}")
            
        except Exception as e:
            _model_load_error = str(e)
            print(f"✗ ERROR loading model: {_model_load_error}")
            return None
    
    return _model

def _encode_visualization(vis_ndarray: np.ndarray) -> str:
    """Encode numpy image (BGR) to PNG and then base64"""
    success, png = cv2.imencode('.png', vis_ndarray)
    if not success:
        return None
    return base64.b64encode(png.tobytes()).decode('ascii')

def _save_visualization(vis_ndarray: np.ndarray, original_filename: str = None) -> str:
    """Save visualization to temp folder and return the path"""
    # Create temp results directory if not exists
    temp_dir = Path(settings.TEMP_RESULTS_DIR)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    if original_filename:
        base_name = Path(original_filename).stem
        filename = f"{base_name}_{timestamp}_detected.png"
    else:
        filename = f"detection_{timestamp}.png"
    
    # Save file
    output_path = temp_dir / filename
    cv2.imwrite(str(output_path), vis_ndarray)
    
    return str(output_path)

def detect_image_bytes(image_bytes: bytes, include_visual: bool = True, save_file: bool = False, original_filename: str = None) -> dict:
    """Run YOLO detection on image bytes and return structured result.

    Args:
        image_bytes: raw image bytes (PNG/JPEG)
        include_visual: include base64 PNG visualization in the result
        save_file: save visualization to temp folder
        original_filename: original filename for better naming

    Returns: {
        'boxes': [ { 'xyxy': [x1,y1,x2,y2], 'confidence': float, 'class': int }, ... ],
        'visualization': base64_png_or_none (only present if include_visual=True),
        'saved_path': file_path_or_none (only present if save_file=True)
    }
    """
    # Check if model is available
    model = get_model()
    if model is None:
        raise RuntimeError(f"Model not available. {_model_load_error or 'Please upload a model first.'}")
    
    # write to temp file because ultralytics model expects a path or array; path is simplest
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        results = model(tmp_path)

        if len(results) == 0:
            return {'boxes': [], 'visualization': None}

        r = results[0]

        boxes = []
        if hasattr(r, 'boxes') and len(r.boxes):
            coords = r.boxes.xyxy.cpu().numpy()
            confs = r.boxes.conf.cpu().numpy()
            classes = r.boxes.cls.cpu().numpy()
            for c, conf, cl in zip(coords, confs, classes):
                boxes.append({'xyxy': [float(v) for v in c], 'confidence': float(conf), 'class': int(cl)})

        # visualization (optional)
        vis_b64 = None
        saved_path = None
        
        if include_visual or save_file:
            try:
                vis = r.plot()  # returns numpy BGR image
                
                if include_visual:
                    vis_b64 = _encode_visualization(vis)
                
                if save_file:
                    saved_path = _save_visualization(vis, original_filename)
            except Exception:
                vis_b64 = None
                saved_path = None

        result = {'boxes': boxes}
        if include_visual:
            result['visualization'] = vis_b64
        if save_file:
            result['saved_path'] = saved_path

        return result
    finally:
        try:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
