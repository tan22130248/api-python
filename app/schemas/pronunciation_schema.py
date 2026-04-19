from pydantic import BaseModel
from typing import Optional

class PronunciationRequest(BaseModel):
    target_text: str
    audio_file: Optional[str] = None  
    
    class Config:
        json_schema_extra = {
            "example": {
                "target_text": "apple",
                "audio_file": "/path/to/audio.wav"
            }
        }

class PronunciationResponse(BaseModel):
    success: bool
    message: str
    recognized_text: Optional[str] = None
    accuracy_score: Optional[str] = None
    feedback: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Kiểm tra phát âm thành công",
                "recognized_text": "apple",
                "accuracy_score": "95.2%",
                "feedback": "Tuyệt đối! (Perfect)"
            }
        }