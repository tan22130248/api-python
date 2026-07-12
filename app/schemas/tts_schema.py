from pydantic import BaseModel, Field
from typing import Optional


class TTSRequest(BaseModel):
    text: str
    language: str = Field(default="vi", description="Mã ngôn ngữ gTTS: vi, en, fr, ja, ko, zh-cn")
    slow: bool = Field(default=False, description="Đọc chậm")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Đây là một quả táo đỏ",
                "language": "vi",
                "slow": False,
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
                "filename": "output_audio_vi.mp3",
            }
        }
