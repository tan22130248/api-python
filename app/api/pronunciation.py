from fastapi import APIRouter, HTTPException, File, Form, UploadFile
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

        suffix = get_audio_suffix(audio_file.filename, content_type)
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(await audio_file.read())
            temp_file_path = temp_file.name
        
        try:
            from app.services.pronunciation_service import check_pronunciation as check_svc
            
            result = check_svc(temp_file_path, target_text)
            
            return PronunciationResponse(
                success=True,
                message="Kiểm tra phát âm thành công",
                recognized_text=result["recognized_text"],
                accuracy_score=result["accuracy_score"],
                feedback=result["feedback"]
            )
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi: {str(e)}")