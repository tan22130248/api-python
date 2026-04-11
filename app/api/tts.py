from fastapi import APIRouter, HTTPException, File, UploadFile
from app.schemas.tts_schema import TTSRequest, TTSResponse
from pydantic import BaseModel
import os

router = APIRouter()

class TTSConvertResponse(BaseModel):
    success: bool
    message: str
    filename: str = None
    error: str = None

@router.get("/health")
async def tts_health():
    """TTS Service health check"""
    return {
        "status": "healthy",
        "service": "TTS API"
    }

@router.get("")
async def tts_endpoint():
    """TTS service info endpoint"""
    return {
        "service": "Text-to-Speech Service",
        "endpoints": {
            "convert": "POST /api/tts/convert",
            "health": "GET /api/tts/health"
        }
    }

@router.post("/convert", response_model=TTSConvertResponse)
async def tts_convert(request: TTSRequest):
    """
    Convert Vietnamese text to speech (MP3 file)
    
    Args:
        request: TTSRequest with text field (Vietnamese text)
        
    Returns:
        TTSConvertResponse with filename of generated audio
    """
    try:
        if not request.text or request.text.strip() == "":
            raise HTTPException(status_code=400, detail="Text không được để trống")
        
        if len(request.text) > 5000:
            raise HTTPException(status_code=400, detail="Text không được vượt quá 5000 ký tự")
        
        from app.services.tts_service import convert_text_to_speech
        
        filename = convert_text_to_speech(request.text)
        
        if not filename:
            raise HTTPException(status_code=400, detail="Lỗi chuyển đổi text thành giọng nói")
        
        return TTSConvertResponse(
            success=True,
            message="Chuyển đổi thành công",
            filename=filename
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi: {str(e)}")

