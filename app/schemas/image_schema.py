from pydantic import BaseModel
from typing import Optional

class ImageRequest(BaseModel):
    description: str

class ImageResponse(BaseModel):
    success: bool
    message: str
    image_url: Optional[str] = None
    error: Optional[str] = None