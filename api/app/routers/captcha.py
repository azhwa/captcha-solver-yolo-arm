from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from ..detector import detect_image_bytes

router = APIRouter()

@router.post("/detect")
async def detect_captcha(
    file: UploadFile = File(...),
    include_visual: bool = True,
    save_file: bool = False
):
    """Detect objects in captcha image using YOLOv8 model
    
    Args:
        file: Image file to detect
        include_visual: Include base64 visualization in response
        save_file: Save visualization to temp folder
    """
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        image_bytes = await file.read()
        result = detect_image_bytes(
            image_bytes, 
            include_visual=include_visual,
            save_file=save_file,
            original_filename=file.filename
        )
        
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "captcha-detector"}
