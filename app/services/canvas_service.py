import os
import requests
from PIL import Image
from datetime import datetime
import cloudinary
import cloudinary.uploader
from app.core.config import init_cloudinary
import logging

def _get_base_dir():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    return project_root

BASE_DIR = _get_base_dir()
ICONS_DIR = os.path.join(BASE_DIR, "icons")
CANVAS_EXPORTS_DIR = os.path.join(BASE_DIR, "canvas_exports")

os.makedirs(ICONS_DIR, exist_ok=True)
os.makedirs(CANVAS_EXPORTS_DIR, exist_ok=True)

logger = logging.getLogger(__name__)
logger.info(f"Icons directory: {ICONS_DIR}")
logger.info(f"Canvas exports directory: {CANVAS_EXPORTS_DIR}")

init_cloudinary()

ICON_URLS = {
    "tao.png": "https://cdn-icons-png.flaticon.com/128/415/415733.png",       
    "cam.png": "https://cdn-icons-png.flaticon.com/128/135/135620.png",       
    "chuoi.png": "https://cdn-icons-png.flaticon.com/128/1135/1135543.png",   
    "meo.png": "https://cdn-icons-png.flaticon.com/128/616/616408.png",       
    "sao.png": "https://cdn-icons-png.flaticon.com/128/1828/1828884.png",    
    "cho.png": "https://cdn-icons-png.flaticon.com/128/1998/1998668.png",      
    "trao.png": "https://cdn-icons-png.flaticon.com/128/833/833472.png",     
    "sach.png": "https://cdn-icons-png.flaticon.com/128/2991/2991148.png",   
    "nha.png": "https://cdn-icons-png.flaticon.com/128/684/684908.png",      
}

def download_icon(url: str, filename: str) -> bool:
    """Download icon from URL"""
    filepath = os.path.join(ICONS_DIR, filename)
    
    if os.path.exists(filepath):
        return True
    
    try:
        r = requests.get(url, timeout=10)
        with open(filepath, 'wb') as f:
            f.write(r.content)
        return True
    except Exception as e:
        print(f"Error downloading {filename}: {str(e)}")
        return False

def get_all_icons() -> list:
    """Get all available icons"""
    icons = []
    
    for name, url in ICON_URLS.items():
        download_icon(url, name)
        filepath = os.path.join(ICONS_DIR, name)
        
        if os.path.exists(filepath):
            try:
                img = Image.open(filepath).convert("RGBA").resize((60, 60))
                icons.append({
                    "id": name.replace(".png", ""),
                    "name": name,
                    "path": filepath,
                    "size": (60, 60)
                })
            except Exception as e:
                print(f"Error loading icon {name}: {str(e)}")
    
    return icons

def get_icon_image(icon_name: str) -> Image.Image or None:
    """Get icon image object"""
    filepath = os.path.join(ICONS_DIR, icon_name)
    
    if os.path.exists(filepath):
        try:
            return Image.open(filepath).convert("RGBA").resize((60, 60))
        except:
            return None
    return None

def crop_canvas_by_bounds(canvas_image: Image.Image, placed_items: list) -> Image.Image:
    """
    Crop canvas to fit all placed items with padding
    
    Args:
        canvas_image: PIL Image of the canvas
        placed_items: List of placed icon dictionaries with x, y, width, height
    
    Returns:
        Cropped PIL Image
    """
    if not placed_items:
        return canvas_image
    
    try:
        min_x = min(item['x'] - item['width']/2 for item in placed_items)
        min_y = min(item['y'] - item['height']/2 for item in placed_items)
        max_x = max(item['x'] + item['width']/2 for item in placed_items)
        max_y = max(item['y'] + item['height']/2 for item in placed_items)
        
        padding = 5
        crop_left = max(0, int(min_x - padding))
        crop_top = max(0, int(min_y - padding))
        crop_right = min(canvas_image.width, int(max_x + padding))
        crop_bottom = min(canvas_image.height, int(max_y + padding))
        
        cropped = canvas_image.crop((crop_left, crop_top, crop_right, crop_bottom))
        
        return cropped
    except Exception as e:
        print(f"Error cropping canvas: {str(e)}")
        return canvas_image

def crop_canvas_by_auto_bounds(canvas_image: Image.Image) -> Image.Image:
    """
    Automatically crop canvas to remove whitespace
    Detects non-white pixels and crops to fit content
    
    Args:
        canvas_image: PIL Image of the canvas
    
    Returns:
        Cropped PIL Image with whitespace removed
    """
    try:
        import numpy as np
        
        if canvas_image.mode != 'RGB':
            canvas_image = canvas_image.convert('RGB')
        
        img_array = np.array(canvas_image)
        
        white = np.array([255, 255, 255])
        non_white_mask = np.any(img_array != white, axis=2)
        
        rows = np.any(non_white_mask, axis=1)
        cols = np.any(non_white_mask, axis=0)
        
        if not np.any(rows):
            return canvas_image
        
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        
        padding = 3
        crop_top = max(0, rmin - padding)
        crop_bottom = min(canvas_image.height, rmax + padding + 1)
        crop_left = max(0, cmin - padding)
        crop_right = min(canvas_image.width, cmax + padding + 1)
        
        cropped = canvas_image.crop((crop_left, crop_top, crop_right, crop_bottom))
        return cropped
    except ImportError:
        try:
            if canvas_image.mode != 'RGB':
                canvas_image = canvas_image.convert('RGB')
            
            canvas_image.putalpha(1)
            bbox = canvas_image.getbbox()
            
            if bbox:
                padding = 3
                crop_left = max(0, bbox[0] - padding)
                crop_top = max(0, bbox[1] - padding)
                crop_right = min(canvas_image.width, bbox[2] + padding)
                crop_bottom = min(canvas_image.height, bbox[3] + padding)
                
                return canvas_image.crop((crop_left, crop_top, crop_right, crop_bottom))
            return canvas_image
        except Exception as e:
            print(f"Error in fallback crop: {str(e)}")
            return canvas_image
    except Exception as e:
        print(f"Error auto-cropping canvas: {str(e)}")
        return canvas_image

def save_canvas_export(canvas_image: Image.Image) -> str:
    """
    Save canvas export to Cloudinary
    
    Returns:
        Cloudinary URL of the uploaded image
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"canvas_export_{timestamp}.png"
    filepath = os.path.join(CANVAS_EXPORTS_DIR, filename)
    
    canvas_image.save(filepath)
    
    try:
        upload_result = cloudinary.uploader.upload(filepath, 
            folder="canvas_images",
            public_id=f"canvas_{timestamp}",
            resource_type="image"
        )
        
        os.remove(filepath)
        
        return upload_result['secure_url']
    except Exception as e:
        print(f"Error uploading to Cloudinary: {str(e)}")
        return os.path.abspath(filepath)