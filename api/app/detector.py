from ultralytics import YOLO
from .config import settings
import tempfile
import base64
import cv2
import numpy as np
import os

# Lazy-loaded model
_model = None

def get_model():
    global _model
    if _model is None:
        _model = YOLO(settings.MODEL_PATH)
    return _model

def _encode_visualization(vis_ndarray: np.ndarray) -> str:
    # Encode numpy image (BGR) to PNG and then base64
    success, png = cv2.imencode('.png', vis_ndarray)
    if not success:
        return None
    return base64.b64encode(png.tobytes()).decode('ascii')

def detect_image_bytes(image_bytes: bytes) -> dict:
    """Run YOLO detection on image bytes and return structured result.

    Returns: {
      'boxes': [ { 'xyxy': [x1,y1,x2,y2], 'confidence': float, 'class': int }, ... ],
      'visualization': base64_png_or_none
    }
    """
    # write to temp file because ultralytics model expects a path or array; path is simplest
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        model = get_model()
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

        # visualization
        try:
            vis = r.plot()  # returns numpy BGR image
            vis_b64 = _encode_visualization(vis)
        except Exception:
            vis_b64 = None

        return {'boxes': boxes, 'visualization': vis_b64}
    finally:
        try:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
