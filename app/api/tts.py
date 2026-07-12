from fastapi import APIRouter, HTTPException
from app.schemas.tts_schema import TTSRequest
from app.services.tts_service import SUPPORTED_LANGUAGES, convert_text_to_speech
from pydantic import BaseModel

router = APIRouter()


class TTSConvertResponse(BaseModel):
    success: bool
    message: str
    filename: str = None
    error: str = None


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
    """Convert text to speech (multi-language via gTTS)."""
    try:
        if not request.text or request.text.strip() == "":
            raise HTTPException(status_code=400, detail="Text không được để trống")

        if len(request.text) > 5000:
            raise HTTPException(status_code=400, detail="Text không được vượt quá 5000 ký tự")

        filename = convert_text_to_speech(
            request.text,
            language=request.language or "vi",
            slow=bool(request.slow),
        )

        if not filename:
            raise HTTPException(status_code=400, detail="Lỗi chuyển đổi text thành giọng nói")

        return TTSConvertResponse(
            success=True,
            message="Chuyển đổi thành công",
            filename=filename,
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi: {str(e)}")
