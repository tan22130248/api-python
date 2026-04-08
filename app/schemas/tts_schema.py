from pydantic import BaseModel
from typing import Optional

class TTSRequest(BaseModel):
    text: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Đây là một quả táo đỏ"
            }
        }

class TTSResponse(BaseModel):
    success: bool
    message: str
    filename: Optional[str] = None
    audio_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Chuyển đổi thành công",
                "filename": "output_audio_vi.mp3"
            }
        }

