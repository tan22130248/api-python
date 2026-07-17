from fastapi import APIRouter, HTTPException
from app.schemas.tts_schema import TTSRequest
from app.services.tts_service import SUPPORTED_LANGUAGES, convert_text_to_speech
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class TTSConvertResponse(BaseModel):
    success: bool
    message: str
    filename: Optional[str] = None
    audio_base64: Optional[str] = None
    error: Optional[str] = None


@router.get("/health")
async def tts_health():
    return {"status": "healthy", "service": "TTS API"}


@router.get("")
async def tts_endpoint():
    return {
        "service": "Text-to-Speech Service",
        "endpoints": {
            "convert": "POST /api/tts/convert",
            "languages": "GET /api/tts/languages",
            "health": "GET /api/tts/health",
        },
        "supportedLanguages": SUPPORTED_LANGUAGES,
    }


@router.get("/languages")
async def tts_languages():
    return {
        "success": True,
        "languages": [{"code": code, "label": label} for code, label in SUPPORTED_LANGUAGES.items()],
    }


@router.post("/convert", response_model=TTSConvertResponse)
async def tts_convert(request: TTSRequest):
    """Convert text to speech (multi-language via gTTS). Returns base64 for cross-container upload."""
    try:
        if not request.text or request.text.strip() == "":
            raise HTTPException(status_code=400, detail="Text không được để trống")

        if len(request.text) > 5000:
            raise HTTPException(status_code=400, detail="Text không được vượt quá 5000 ký tự")

        filepath, audio_b64 = convert_text_to_speech(
            request.text,
            language=request.language or "vi",
            slow=bool(request.slow),
        )

        if not audio_b64:
            raise HTTPException(status_code=400, detail="Lỗi chuyển đổi text thành giọng nói")

        return TTSConvertResponse(
            success=True,
            message="Chuyển đổi thành công",
            filename=filepath,
            audio_base64=audio_b64,
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi: {str(e)}")
