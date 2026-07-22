from fastapi import APIRouter, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, field_validator
from typing import List, Optional
import mimetypes
from datetime import datetime

router = APIRouter()

class PlacedIcon(BaseModel):
    id: int
    icon_name: str
    x: int
    y: int
    width: int = 60
    height: int = 60
    
    @field_validator('x', 'y', 'width', 'height', mode='before')
    def convert_to_int(cls, v):
        """Convert float values to int by rounding"""
        if isinstance(v, float):
            return round(v)
        return int(v)

class SaveCanvasRequest(BaseModel):
    placed_items: List[PlacedIcon]

class IconInfo(BaseModel):
    id: str
    name: str
    url: str

class CanvasSaveResponse(BaseModel):
    success: bool
    message: str
    image_path: str = None
    error: str = None

@router.get("/health")
async def canvas_health():
    """Canvas Service health check"""
    return {
        "status": "healthy",
        "service": "Canvas API"
    }

@router.get("/icons")
async def get_icons(request: Request, category: Optional[str] = None, style: Optional[str] = None):
    """Get all available icons"""
    from app.services.canvas_service import get_all_icons, get_all_icon_filters
    
    try:
        # download_missing=True so deploy containers without pre-seeded icons still work
        icons = get_all_icons(category=category, style=style, download_missing=True)
        filters = get_all_icon_filters()
        # Prefer relative path so browser uses same-origin /python-api proxy
        base = str(request.base_url).rstrip("/")
        return JSONResponse(
            content={
                "success": True,
                "data": [
                    {
                        "id": icon["id"],
                        "name": icon["name"],
                        "display_name": icon.get("display_name", icon["name"]),
                        "category": icon.get("category", "default"),
                        "style": icon.get("style", "default"),
                        "source": icon.get("source", "default"),
                        "url": f"/api/canvas/icon/{icon['name']}",
                    }
                    for icon in icons
                ],
                "filters": filters
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/icon/{icon_name:path}")
async def get_icon_file(icon_name: str):
    """Get icon image file"""
    from app.services.canvas_service import resolve_icon_path
    
    try:
        icon_path = resolve_icon_path(icon_name)
        
        if icon_path:
            media_type = mimetypes.guess_type(icon_path)[0] or "image/png"
            return FileResponse(
                icon_path,
                media_type=media_type,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET,OPTIONS",
                    "Access-Control-Allow-Headers": "*"
                }
            )
        else:
            raise HTTPException(status_code=404, detail=f"Icon not found: {icon_name}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading icon: {str(e)}")

@router.post("/save")
async def save_canvas(request: SaveCanvasRequest):
    """
    Save canvas with placed icons
    Creates an image of the canvas with all placed items
    """
    from PIL import Image
    from app.services.canvas_service import get_icon_image, crop_canvas_by_bounds, save_canvas_export
    
    try:
        if not request.placed_items:
            raise HTTPException(status_code=400, detail="No items placed on canvas")
        
        canvas = Image.new("RGB", (400, 300), color="white")
        
        for item in request.placed_items:
            icon_img = get_icon_image(item.icon_name)
            if icon_img:
                paste_x = item.x - item.width // 2
                paste_y = item.y - item.height // 2
                
                icon_resized = icon_img.resize((item.width, item.height))
                canvas.paste(icon_resized, (paste_x, paste_y), icon_resized)
        
        cropped_canvas = crop_canvas_by_bounds(canvas, request.placed_items)
        
        image_path = save_canvas_export(cropped_canvas)
        
        return CanvasSaveResponse(
            success=True,
            message="Canvas saved successfully",
            image_path=image_path
        )
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/save-blob")
async def save_canvas_blob(file: UploadFile = File(...)):
    """
    Save canvas blob directly from frontend
    Receives PNG image from canvas.toBlob()
    """
    from PIL import Image
    from io import BytesIO
    from app.services.canvas_service import crop_canvas_by_auto_bounds, save_canvas_export
    
    try:
        contents = await file.read()
        
        canvas = Image.open(BytesIO(contents))
        canvas = canvas.convert("RGB")
        
        cropped_canvas = crop_canvas_by_auto_bounds(canvas)
        
        # Save canvas
        image_path = save_canvas_export(cropped_canvas)
        
        return CanvasSaveResponse(
            success=True,
            message="Canvas saved successfully",
            image_path=image_path
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload image to Cloudinary
    Frontend sends image file, we upload to Cloudinary and return URL
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        import cloudinary.uploader
        from io import BytesIO
        from PIL import Image
        
        contents = await file.read()
        
        img = Image.open(BytesIO(contents))
        
        result = cloudinary.uploader.upload(
            BytesIO(contents),
            folder="image_generation",
            resource_type="auto",
            public_id=f"uploaded_{int(datetime.now().timestamp())}"
        )
        
        if result.get('secure_url'):
            return {
                "success": True,
                "message": "Image uploaded successfully",
                "image_url": result['secure_url'],
                "public_id": result.get('public_id')
            }
        else:
            raise HTTPException(status_code=500, detail="Upload to Cloudinary failed")
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error uploading image: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")


@router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload audio file to Cloudinary
    Frontend sends audio file, we upload to Cloudinary and return URL
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        import cloudinary.uploader
        from io import BytesIO
        
        contents = await file.read()
        
        result = cloudinary.uploader.upload(
            BytesIO(contents),
            folder="audio_uploads",
            resource_type="auto",
            public_id=f"audio_{int(datetime.now().timestamp())}",
            type="upload"
        )
        
        if result.get('secure_url'):
            return {
                "success": True,
                "message": "Audio uploaded successfully",
                "audio_url": result['secure_url'],
                "public_id": result.get('public_id')
            }
        else:
            raise HTTPException(status_code=500, detail="Upload to Cloudinary failed")
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error uploading audio: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error uploading audio: {str(e)}")