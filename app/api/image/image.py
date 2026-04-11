from fastapi import APIRouter, HTTPException, File, UploadFile
from app.schemas.image_schema import ImageRequest, ImageResponse
from pydantic import BaseModel
import os

router = APIRouter()

class ImageGenerateResponse(BaseModel):
    success: bool
    message: str
    filename: str = None
    error: str = None

@router.get("/health")
async def image_health():
    """Image Service health check"""
    return {
        "status": "healthy",
        "service": "Image Generation API"
    }

@router.get("")
async def image_endpoint():
    """Image service info endpoint"""
    return {
        "service": "Image Generation Service",
        "endpoints": {
            "generate": "POST /api/image/generate",
            "health": "GET /api/image/health"
        }
    }

@router.post("/generate", response_model=ImageGenerateResponse)
async def generate_image(request: ImageRequest):
    """
    Generate image from description

    Args:
        request: ImageRequest with description field

    Returns:
        ImageGenerateResponse with filename of generated image
    """
    try:
        if not request.description or request.description.strip() == "":
            raise HTTPException(status_code=400, detail="Description không được để trống")

        if len(request.description) > 1000:
            raise HTTPException(status_code=400, detail="Description không được vượt quá 1000 ký tự")

        from app.services.image_service import generate_image_from_description

        filename = generate_image_from_description(request.description)

        if not filename:
            raise HTTPException(status_code=400, detail="Lỗi tạo ảnh")

        return ImageGenerateResponse(
            success=True,
            message="Tạo ảnh thành công",
            filename=filename
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi: {str(e)}")