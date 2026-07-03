from pydantic import BaseModel, Field
from typing import Optional, List


class TranslateRequest(BaseModel):
    text: str = Field(..., description="Text to translate")
    source_lang: str = Field(default="vi", description="Source language: 'vi' or 'en'")
    target_lang: str = Field(default="en", description="Target language: 'vi' or 'en'")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Xin chào, tôi là giáo viên tiểu học.",
                "source_lang": "vi",
                "target_lang": "en"
            }
        }


class TranslateResponse(BaseModel):
    success: bool
    message: str
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Dịch thành công",
                "original_text": "Xin chào, tôi là giáo viên tiểu học.",
                "translated_text": "Hello, I am a primary school teacher.",
                "source_lang": "vi",
                "target_lang": "en"
            }
        }


class DocumentTranslateRequest(BaseModel):
    text: str = Field(..., description="Long document text to translate")
    source_lang: str = Field(default="vi", description="Source language: 'vi' or 'en'")
    target_lang: str = Field(default="en", description="Target language: 'vi' or 'en'")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Bài 1: Phép cộng trong phạm vi 100.\nHọc sinh cần nắm vững các phép cộng cơ bản.",
                "source_lang": "vi",
                "target_lang": "en"
            }
        }


class TranslatedSegment(BaseModel):
    original: str
    translated: str


class DocumentTranslateResponse(BaseModel):
    success: bool
    message: str
    original_text: str
    translated_text: str
    segments: List[TranslatedSegment]
    source_lang: str
    target_lang: str
    total_segments: int
