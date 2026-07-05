import os
import requests
from PIL import Image
from datetime import datetime
import cloudinary
import cloudinary.uploader
from app.core.config import init_cloudinary
import logging
from typing import Optional

def _get_base_dir():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    return project_root

BASE_DIR = _get_base_dir()
ICONS_DIR = os.path.join(BASE_DIR, "icons")
CAO_ICONS_DIR = os.path.join(BASE_DIR, "images", "cao_icon")
CANVAS_EXPORTS_DIR = os.path.join(BASE_DIR, "canvas_exports")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
CAO_ICON_CATEGORY = "cao_icon"
CONTENT_CATEGORY_DIRS = {"dong_vat", "hinh_khoi", "trai_cay", "tien_vietnam"}
ROOT_CAO_ICON_CATEGORY = "nature"
CATEGORY_MAP = {
    "trai_cay": "fruits",
    "dong_vat": "animals",
    "hinh_khoi": "shapes",
    "tien_vietnam": "money",
    "thien_nhien": "nature",
}
CATEGORY_ALIASES = {
    "fruits": {"fruits", "fruit", "trai_cay"},
    "animals": {"animals", "animal", "dong_vat"},
    "shapes": {"shapes", "shape", "hinh_khoi"},
    "money": {"money", "tien_vietnam"},
    "nature": {"nature", "thien_nhien"},
}

os.makedirs(ICONS_DIR, exist_ok=True)
os.makedirs(CANVAS_EXPORTS_DIR, exist_ok=True)

logger = logging.getLogger(__name__)
logger.info(f"Icons directory: {ICONS_DIR}")
logger.info(f"Cao icons directory: {CAO_ICONS_DIR}")
logger.info(f"Canvas exports directory: {CANVAS_EXPORTS_DIR}")

init_cloudinary()

BASE_OPENMOJI = "https://raw.githubusercontent.com/hfg-gmuend/openmoji/master/color/72x72"

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
    "tao.png":          f"{BASE_OPENMOJI}/1F34E.png",
"tao_xanh.png":     f"{BASE_OPENMOJI}/1F34F.png",
"cam.png":          f"{BASE_OPENMOJI}/1F34A.png",
"chuoi.png":        f"{BASE_OPENMOJI}/1F34C.png",
"nho.png":          f"{BASE_OPENMOJI}/1F347.png",
"dau.png":          f"{BASE_OPENMOJI}/1F353.png",
"dua_hau.png":      f"{BASE_OPENMOJI}/1F349.png",
"xoai.png":         f"{BASE_OPENMOJI}/1F96D.png",
"le.png":           f"{BASE_OPENMOJI}/1F350.png",
"anh_dao.png":      f"{BASE_OPENMOJI}/1F352.png",
"dua.png":          f"{BASE_OPENMOJI}/1F34D.png",
"kiwi.png":         f"{BASE_OPENMOJI}/1F95D.png",
"dao.png":          f"{BASE_OPENMOJI}/1F351.png",
"dua_leo.png":      f"{BASE_OPENMOJI}/1F952.png",
"viet_quat.png":    f"{BASE_OPENMOJI}/1FAD0.png",
"ca_rot.png":       f"{BASE_OPENMOJI}/1F955.png",
"ca_chua.png":      f"{BASE_OPENMOJI}/1F345.png",
"bap_ngo.png":      f"{BASE_OPENMOJI}/1F33D.png",
"ot.png":           f"{BASE_OPENMOJI}/1F336.png",
"sup_lo.png":       f"{BASE_OPENMOJI}/1F966.png",
"hanh_tay.png":     f"{BASE_OPENMOJI}/1F9C5.png",
"khoai_tay.png":    f"{BASE_OPENMOJI}/1F954.png",
"ca_tim.png":       f"{BASE_OPENMOJI}/1F346.png",
"xa_lach.png":      f"{BASE_OPENMOJI}/1F96C.png",
"nam.png":          f"{BASE_OPENMOJI}/1F344.png",
"cho.png":          f"{BASE_OPENMOJI}/1F436.png",
"meo.png":          f"{BASE_OPENMOJI}/1F431.png",
"tho.png":          f"{BASE_OPENMOJI}/1F430.png",
"gau.png":          f"{BASE_OPENMOJI}/1F43B.png",
"lon.png":          f"{BASE_OPENMOJI}/1F437.png",
"bo.png":           f"{BASE_OPENMOJI}/1F42E.png",
"ga.png":           f"{BASE_OPENMOJI}/1F414.png",
"vit.png":          f"{BASE_OPENMOJI}/1F986.png",
"ca.png":           f"{BASE_OPENMOJI}/1F41F.png",
"ca_map.png":       f"{BASE_OPENMOJI}/1F988.png",
"ca_heo.png":       f"{BASE_OPENMOJI}/1F42C.png",
"rua.png":          f"{BASE_OPENMOJI}/1F422.png",
"ran.png":          f"{BASE_OPENMOJI}/1F40D.png",
"ech.png":          f"{BASE_OPENMOJI}/1F438.png",
"voi.png":          f"{BASE_OPENMOJI}/1F418.png",
"su_tu.png":        f"{BASE_OPENMOJI}/1F981.png",
"khi.png":          f"{BASE_OPENMOJI}/1F412.png",
"nga.png":          f"{BASE_OPENMOJI}/1F434.png",
"buom.png":         f"{BASE_OPENMOJI}/1F98B.png",
"ong.png":          f"{BASE_OPENMOJI}/1F41D.png",
"giot_nuoc.png":    f"{BASE_OPENMOJI}/1F4A7.png",
"song_bien.png":    f"{BASE_OPENMOJI}/1F30A.png",
"mua.png":          f"{BASE_OPENMOJI}/1F327.png",
"tuyet.png":        f"{BASE_OPENMOJI}/2744.png",
"nuoc_voi.png":     f"{BASE_OPENMOJI}/1F6BF.png",
"lua.png":          f"{BASE_OPENMOJI}/1F525.png",
"cau_vong.png":     f"{BASE_OPENMOJI}/1F308.png",
"bong_bong.png":    f"{BASE_OPENMOJI}/1F9FC.png",
"cay_xanh.png":     f"{BASE_OPENMOJI}/1F333.png",
"cay_thong.png":    f"{BASE_OPENMOJI}/1F332.png",
"hoa_vang.png":     f"{BASE_OPENMOJI}/1F33C.png",
"hoa_hong.png":     f"{BASE_OPENMOJI}/1F339.png",
"hoa_dao.png":      f"{BASE_OPENMOJI}/1F338.png",
"la_cay.png":       f"{BASE_OPENMOJI}/1F343.png",
"xuong_rong.png":   f"{BASE_OPENMOJI}/1F335.png",
"co.png":           f"{BASE_OPENMOJI}/1F33F.png",
"huong_duong.png":  f"{BASE_OPENMOJI}/1F33B.png",
"bong_lua.png":     f"{BASE_OPENMOJI}/1F33E.png",
"mat_troi.png":     f"{BASE_OPENMOJI}/2600.png",
"mat_trang.png":    f"{BASE_OPENMOJI}/1F315.png",
"ngoi_sao.png":     f"{BASE_OPENMOJI}/2B50.png",
"may.png":          f"{BASE_OPENMOJI}/2601.png",
"sam_set.png":      f"{BASE_OPENMOJI}/26C8.png",
"gio.png":          f"{BASE_OPENMOJI}/1F32C.png",
"sao_bang.png":     f"{BASE_OPENMOJI}/1F320.png",
"be_trai.png":      f"{BASE_OPENMOJI}/1F466.png",
"be_gai.png":       f"{BASE_OPENMOJI}/1F467.png",
"nguoi_lon.png":    f"{BASE_OPENMOJI}/1F468.png",
"phu_nu.png":       f"{BASE_OPENMOJI}/1F469.png",
"ong_gia.png":      f"{BASE_OPENMOJI}/1F474.png",
"ba_gia.png":       f"{BASE_OPENMOJI}/1F475.png",
"tre_em.png":       f"{BASE_OPENMOJI}/1F476.png",
"phi_hanh_gia.png": f"{BASE_OPENMOJI}/1F9D1.png",
"vo_si.png":        f"{BASE_OPENMOJI}/1F9D7.png",
"sach.png":         f"{BASE_OPENMOJI}/1F4DA.png",
"but_chi.png":      f"{BASE_OPENMOJI}/270F.png",
"thuoc.png":        f"{BASE_OPENMOJI}/1F4CF.png",
"keo_cat.png":      f"{BASE_OPENMOJI}/2702.png",
"may_tinh.png":     f"{BASE_OPENMOJI}/1F4BB.png",
"ba_lo.png":        f"{BASE_OPENMOJI}/1F392.png",
"truong_hoc.png":   f"{BASE_OPENMOJI}/1F3EB.png",
"kinh_hien_vi.png": f"{BASE_OPENMOJI}/1F52C.png",
"kinh_thien_van.png": f"{BASE_OPENMOJI}/1F52D.png",
"bong_den.png":     f"{BASE_OPENMOJI}/1F4A1.png",
"may_tinh_bang.png":f"{BASE_OPENMOJI}/1F4F1.png",
"xe_oto.png":       f"{BASE_OPENMOJI}/1F697.png",
"xe_bus.png":       f"{BASE_OPENMOJI}/1F68C.png",
"xe_dap.png":       f"{BASE_OPENMOJI}/1F6B2.png",
"may_bay.png":      f"{BASE_OPENMOJI}/2708.png",
"tau_hoa.png":      f"{BASE_OPENMOJI}/1F682.png",
"tau_thuy.png":     f"{BASE_OPENMOJI}/1F6A2.png",
"xe_may.png":       f"{BASE_OPENMOJI}/1F6F5.png",
"truc_thang.png":   f"{BASE_OPENMOJI}/1F681.png",
"ten_lua.png":      f"{BASE_OPENMOJI}/1F680.png",
"xe_tai.png":       f"{BASE_OPENMOJI}/1F69B.png",
"com.png":          f"{BASE_OPENMOJI}/1F35A.png",
"pho.png":          f"{BASE_OPENMOJI}/1F35C.png",
"banh_mi.png":      f"{BASE_OPENMOJI}/1F956.png",
"pizza.png":        f"{BASE_OPENMOJI}/1F355.png",
"banh_kem.png":     f"{BASE_OPENMOJI}/1F382.png",
"kem.png":          f"{BASE_OPENMOJI}/1F368.png",
"sua.png":          f"{BASE_OPENMOJI}/1F95B.png",
"nuoc_ep.png":      f"{BASE_OPENMOJI}/1F964.png",
"keo_ngot.png":     f"{BASE_OPENMOJI}/1F36C.png",
"trung_chien.png":  f"{BASE_OPENMOJI}/1F373.png",
"nha.png":          f"{BASE_OPENMOJI}/1F3E0.png",
"chung_cu.png":     f"{BASE_OPENMOJI}/1F3E2.png",
"xa_phong.png":    f"{BASE_OPENMOJI}/1F388.png",
"qua_tang.png":     f"{BASE_OPENMOJI}/1F381.png",
"cup.png":          f"{BASE_OPENMOJI}/1F3C6.png",
"huy_chuong.png":   f"{BASE_OPENMOJI}/1F947.png",
"bong_da.png":      f"{BASE_OPENMOJI}/26BD.png",
"bong_ro.png":      f"{BASE_OPENMOJI}/1F3C0.png",
"am_nhac.png":      f"{BASE_OPENMOJI}/1F3B5.png",
"guitar.png":       f"{BASE_OPENMOJI}/1F3B8.png",
"may_anh.png":      f"{BASE_OPENMOJI}/1F4F7.png",
"palette.png":      f"{BASE_OPENMOJI}/1F3A8.png",
"xep_hinh.png":     f"{BASE_OPENMOJI}/1F9E9.png",
"dieu.png":         f"{BASE_OPENMOJI}/1FA81.png",
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

def _is_safe_child(parent: str, child: str) -> bool:
    parent_abs = os.path.normcase(os.path.abspath(parent))
    child_abs = os.path.normcase(os.path.abspath(child))
    return os.path.commonpath([parent_abs, child_abs]) == parent_abs


def _normalize_category(category: Optional[str]) -> Optional[str]:
    if not category:
        return None

    category_lower = category.lower()
    for canonical, aliases in CATEGORY_ALIASES.items():
        if category_lower in aliases:
            return canonical
    return category_lower


def _matches_filter(icon: dict, category: Optional[str], style: Optional[str]) -> bool:
    if category and icon.get("category", "").lower() != _normalize_category(category):
        return False
    if style and icon.get("style", "").lower() != style.lower():
        return False
    return True


def _build_icon_filters(icons: list) -> dict:
    categories = sorted({icon["category"] for icon in icons if icon.get("category")}, key=str.lower)
    styles = sorted({icon["style"] for icon in icons if icon.get("style")}, key=str.lower)
    styles_by_category = {}

    for category_name in categories:
        styles_by_category[category_name] = sorted(
            {icon["style"] for icon in icons if icon.get("category") == category_name and icon.get("style")},
            key=str.lower
        )

    return {
        "categories": categories,
        "styles": styles,
        "styles_by_category": styles_by_category
    }


def _get_cao_icon_meta(root: str, filepath: str) -> dict:
    rel_path = os.path.relpath(filepath, root)
    parts = rel_path.split(os.sep)

    if parts[0] in CONTENT_CATEGORY_DIRS:
        category = CATEGORY_MAP.get(parts[0], parts[0])
        style = parts[1] if len(parts) >= 3 else "default"
    elif len(parts) >= 3:
        category = parts[0]
        style = parts[1]
    elif len(parts) == 2:
        category = ROOT_CAO_ICON_CATEGORY
        style = parts[0]
    else:
        category = ROOT_CAO_ICON_CATEGORY
        style = "default"

    icon_key = f"{CAO_ICON_CATEGORY}/" + rel_path.replace(os.sep, "/")
    icon_id = os.path.splitext(icon_key)[0].replace("/", "__").replace(" ", "_")

    return {
        "id": icon_id,
        "name": icon_key,
        "display_name": os.path.basename(filepath),
        "path": filepath,
        "category": category,
        "style": style,
        "source": "server",
        "size": (60, 60)
    }


def _scan_cao_icons() -> list:
    icons = []

    if not os.path.isdir(CAO_ICONS_DIR):
        return icons

    for root, _, files in os.walk(CAO_ICONS_DIR):
        files.sort(key=str.lower)
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in IMAGE_EXTENSIONS:
                continue

            filepath = os.path.join(root, filename)
            icons.append(_get_cao_icon_meta(CAO_ICONS_DIR, filepath))

    return icons


def get_all_icon_filters() -> dict:
    """Get all available icon filters."""
    return _build_icon_filters(get_all_icons())


def get_all_icons(category: Optional[str] = None, style: Optional[str] = None, download_missing: bool = False) -> list:
    """Get all available icons"""
    icons = []
    
    for name, url in ICON_URLS.items():
        filepath = os.path.join(ICONS_DIR, name)
        if download_missing and not os.path.exists(filepath):
            download_icon(url, name)
        
        if os.path.exists(filepath):
            try:
                img = Image.open(filepath).convert("RGBA").resize((60, 60))
                icons.append({
                    "id": name.replace(".png", ""),
                    "name": name,
                    "display_name": name,
                    "path": filepath,
                    "category": "default",
                    "style": "default",
                    "source": "default",
                    "size": (60, 60)
                })
            except Exception as e:
                print(f"Error loading icon {name}: {str(e)}")
    
    icons.extend(_scan_cao_icons())

    return [icon for icon in icons if _matches_filter(icon, category, style)]


def resolve_icon_path(icon_name: str) -> Optional[str]:
    """Resolve an icon key to a safe local file path."""
    normalized_name = icon_name.replace("\\", "/").lstrip("/")

    if normalized_name.startswith(f"{CAO_ICON_CATEGORY}/"):
        rel_path = normalized_name[len(CAO_ICON_CATEGORY) + 1:]
        filepath = os.path.abspath(os.path.join(CAO_ICONS_DIR, rel_path.replace("/", os.sep)))
        if _is_safe_child(CAO_ICONS_DIR, filepath) and os.path.isfile(filepath):
            return filepath
        return None

    filename = os.path.basename(normalized_name)
    filepath = os.path.abspath(os.path.join(ICONS_DIR, filename))
    if _is_safe_child(ICONS_DIR, filepath) and os.path.isfile(filepath):
        return filepath

    return None

def get_icon_image(icon_name: str) -> Image.Image or None:
    """Get icon image object"""
    filepath = resolve_icon_path(icon_name)
    
    if filepath:
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