from fastapi import APIRouter, HTTPException, File, Form, UploadFile
from fastapi.concurrency import run_in_threadpool
from app.schemas.pronunciation_schema import PronunciationResponse
import os
import tempfile

router = APIRouter()

def get_audio_suffix(filename: str, content_type: str) -> str:
    normalized = filename.lower() if filename else ''
    if normalized.endswith('.wav'):
        return '.wav'
    if normalized.endswith('.mp3'):
        return '.mp3'
    if normalized.endswith('.webm'):
        return '.webm'
    if normalized.endswith('.ogg'):
        return '.ogg'
    if normalized.endswith('.m4a'):
        return '.m4a'
    if content_type:
        if 'wav' in content_type:
            return '.wav'
        if 'mpeg' in content_type or 'mp3' in content_type:
            return '.mp3'
        if 'webm' in content_type:
            return '.webm'
        if 'ogg' in content_type:
            return '.ogg'
        if 'm4a' in content_type or 'aac' in content_type:
            return '.m4a'
    return '.wav'

SUPPORTED_AUDIO_TYPES = {
    'audio/wav',
    'audio/x-wav',
    'audio/mpeg',
    'audio/mp3',
    'audio/webm',
    'audio/ogg',
    'audio/x-m4a',
    'audio/m4a',
    'audio/opus',
}

MAX_AUDIO_SIZE = 25 * 1024 * 1024


async def save_uploaded_audio(audio_file: UploadFile) -> str:
    contents = await audio_file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="File âm thanh đang trống")
    if len(contents) > MAX_AUDIO_SIZE:
        raise HTTPException(status_code=413, detail="File âm thanh không được vượt quá 25 MB")

    suffix = get_audio_suffix(audio_file.filename or "", audio_file.content_type or "")
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(contents)
        return temp_file.name

@router.get("/health")
async def pronunciation_health():
    """Pronunciation Service health check"""
    return {
        "status": "healthy",
        "service": "Pronunciation API"
    }

@router.post("/check", response_model=PronunciationResponse)
async def check_pronunciation(
    target_text: str = Form(...),
    audio_file: UploadFile = File(...)
):
    """
    Check pronunciation by comparing speech with target text
    
    Args:
        target_text: The target text to compare against
        audio_file: Uploaded audio file (WAV/MP3)
        
    Returns:
        PronunciationResponse with recognition results
    """
    try:
        if not target_text or target_text.strip() == "":
            raise HTTPException(status_code=400, detail="Target text không được để trống")
        
        if not audio_file:
            raise HTTPException(status_code=400, detail="Audio file là bắt buộc")

        if not audio_file.filename:
            raise HTTPException(status_code=400, detail="Tên file âm thanh không hợp lệ")

        content_type = audio_file.content_type or ''
        if content_type not in SUPPORTED_AUDIO_TYPES:
            if not any(audio_file.filename.lower().endswith(ext) for ext in ['.wav', '.mp3', '.webm', '.ogg', '.m4a']):
                raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file WAV, MP3, WEBM, OGG hoặc M4A")

        temp_file_path = await save_uploaded_audio(audio_file)
        
        try:
            from app.services.pronunciation_service import check_pronunciation as check_svc
            
            result = await run_in_threadpool(check_svc, temp_file_path, target_text.strip())
            
            return PronunciationResponse(
                success=True,
                message="Kiểm tra phát âm thành công",
                recognized_text=result["recognized_text"],
                accuracy_score=result["accuracy_score"],
                feedback=result["feedback"],
                model_used="faster-whisper"
            )
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi: {str(e)}")


@router.post("/check-vosk", response_model=PronunciationResponse)
async def check_pronunciation_vosk(
    target_text: str = Form(...),
    audio_file: UploadFile = File(...)
):
    """Kiểm tra phát âm bằng model Vosk cục bộ, độc lập với Faster-Whisper."""
    try:
        if not target_text or target_text.strip() == "":
            raise HTTPException(status_code=400, detail="Target text không được để trống")
        if not audio_file or not audio_file.filename:
            raise HTTPException(status_code=400, detail="File âm thanh là bắt buộc")

        content_type = audio_file.content_type or ''
        if content_type not in SUPPORTED_AUDIO_TYPES:
            supported_extensions = ['.wav', '.mp3', '.webm', '.ogg', '.m4a']
            if not any(audio_file.filename.lower().endswith(ext) for ext in supported_extensions):
                raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file WAV, MP3, WEBM, OGG hoặc M4A")

        temp_file_path = await save_uploaded_audio(audio_file)

        try:
            from app.services.vosk_pronunciation_service import check_pronunciation as check_vosk

            result = await run_in_threadpool(check_vosk, temp_file_path, target_text.strip())
            return PronunciationResponse(
                success=True,
                message="Kiểm tra phát âm bằng Vosk thành công",
                recognized_text=result["recognized_text"],
                accuracy_score=result["accuracy_score"],
                feedback=result["feedback"],
                model_used=result["model_used"]
            )
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi Vosk: {str(e)}")
