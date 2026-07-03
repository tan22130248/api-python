from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps, ImageFilter
import os
from datetime import datetime
import random
import requests
import io
import base64
from urllib.parse import unquote, urlparse

IMAGES_OUTPUT_DIR = "images"

if not os.path.exists(IMAGES_OUTPUT_DIR):
    os.makedirs(IMAGES_OUTPUT_DIR)

def generate_image_from_description(description: str) -> str:
    """
    Generate image from description using Pillow

    Args:
        description: Text description for the image

    Returns:
        Filename of the generated image file

    Raises:
        Exception: If generation fails
    """
    if not description or description.strip() == "":
        raise Exception("Description không được để trống")

    try:
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 40)
            small_font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        desc_lower = description.lower()

        if 'mèo' in desc_lower or 'cat' in desc_lower:
            draw.rectangle([300, 200, 500, 400], fill='orange', outline='black')
            draw.ellipse([320, 220, 380, 280], fill='orange')  # head
            draw.ellipse([340, 240, 360, 260], fill='black')  # ears
            draw.ellipse([440, 240, 460, 260], fill='black')  # ears
            draw.ellipse([350, 250, 370, 270], fill='yellow')  # eyes
            draw.ellipse([430, 250, 450, 270], fill='yellow')  # eyes
            draw.rectangle([380, 300, 420, 320], fill='pink')  # nose

        elif 'chó' in desc_lower or 'dog' in desc_lower:
            draw.rectangle([300, 200, 500, 400], fill='brown', outline='black')
            draw.ellipse([320, 220, 380, 280], fill='brown')  # head
            draw.ellipse([350, 250, 370, 270], fill='black')  # eyes
            draw.ellipse([430, 250, 450, 270], fill='black')  # eyes
            draw.rectangle([380, 300, 420, 320], fill='black')  # nose
            draw.rectangle([360, 320, 440, 380], fill='brown')  # body

        elif 'táo' in desc_lower or 'apple' in desc_lower:
            draw.ellipse([350, 200, 450, 300], fill='red', outline='black')
            draw.rectangle([395, 180, 405, 200], fill='green')  # stem

        elif 'cam' in desc_lower or 'orange' in desc_lower:
            draw.ellipse([350, 200, 450, 300], fill='orange', outline='black')

        elif 'sao' in desc_lower or 'star' in desc_lower:
            draw.polygon([(400, 150), (410, 180), (440, 180), (420, 200), (430, 230),
                         (400, 210), (370, 230), (380, 200), (360, 180), (390, 180)],
                        fill='yellow', outline='black')

        else:
            for _ in range(5):
                x1 = random.randint(100, 700)
                y1 = random.randint(100, 500)
                x2 = x1 + random.randint(50, 150)
                y2 = y1 + random.randint(50, 150)
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                draw.rectangle([x1, y1, x2, y2], fill=color, outline='black')

        text_bbox = draw.textbbox((0, 0), description, font=small_font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (800 - text_width) // 2
        draw.text((text_x, 550), description, fill='black', font=small_font)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"generated_image_{timestamp}.png"
        filepath = os.path.join(IMAGES_OUTPUT_DIR, filename)

        img.save(filepath)

        return os.path.abspath(filepath)

    except Exception as e:
        raise Exception(f"Lỗi tạo ảnh: {str(e)}")

def load_image(source: str) -> Image.Image:
    """Load image from url, base64, or local path"""
    if source.startswith("data:image"):
        try:
            header, encoded = source.split(",", 1)
            data = base64.b64decode(encoded)
            return Image.open(io.BytesIO(data))
        except Exception as e:
            raise Exception(f"Error parsing base64 image data: {str(e)}")
    elif source.startswith("http://") or source.startswith("https://"):
        try:
            # Server icons are exposed by this same FastAPI process. Loading one
            # through HTTP here can deadlock a single-worker server because the
            # current request blocks while waiting for itself to serve the icon.
            parsed = urlparse(source)
            icon_prefix = "/api/canvas/icon/"
            if parsed.path.startswith(icon_prefix):
                from app.services.canvas_service import ICONS_DIR

                icon_name = os.path.basename(unquote(parsed.path[len(icon_prefix):]))
                icon_path = os.path.join(ICONS_DIR, icon_name)
                if os.path.isfile(icon_path):
                    return Image.open(icon_path)
            response = requests.get(source, timeout=15)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content))
        except Exception as e:
            raise Exception(f"Error downloading image from URL {source}: {str(e)}")
    elif os.path.exists(source):
        return Image.open(source)
    else:
        # Check if it exists in the outputs directory
        local_path = os.path.join(IMAGES_OUTPUT_DIR, source)
        if os.path.exists(local_path):
            return Image.open(local_path)
        raise Exception(f"Image source not found: {source}")

def process_image_operations(source: str, operations: list, return_type: str = "file", export_format: str = "png", quality: int = 90) -> str:
    """
    Process image using Pillow based on list of operations:
    - crop: box: [left, top, right, bottom], is_percentage: bool
    - rotate: angle: float, expand: bool
    - flip: direction: 'horizontal' | 'vertical'
    - resize: width: int, height: int
    - brightness: factor: float
    - transparency: opacity: float (0.0 to 1.0)
    - filter: name: 'grayscale' | 'sepia' | 'invert'
    - tint: color: hex, amount: float (0.0 to 1.0)
    - text: text: str, x: int, y: int, font_size: int, color: hex
    - watermark: text: str, opacity: float, color: hex
    - overlay: overlay_image_url: str, x: int, y: int, width: int, height: int
    - chroma_key: color: hex, tolerance: int
    - merge: images: list, layout: 'horizontal' | 'vertical' | 'grid', spacing: int, background_color: hex
    - color_adjust: contrast: float, color: float, sharpness: float
    - create_transparent: width: int, height: int
    - blur: radius: float
    - sharpen: amount: float
    - border: thickness: int, color: hex
    - shadow: offset_x: int, offset_y: int, blur: float, color: hex, opacity: float

    Output:
    - return_type: 'base64' | 'cloudinary' | <file>
    - export_format: 'png' | 'jpg' (jpg flattens transparency onto white)
    - quality: int (JPEG quality, default 90)
    """
    try:
        # Check if we should create a transparent background image
        if source == "transparent" or (operations and operations[0].get("type") == "create_transparent"):
            width = 800
            height = 600
            if operations and operations[0].get("type") == "create_transparent":
                width = int(operations[0].get("width", 800))
                height = int(operations[0].get("height", 600))
                # Remove it so we don't process it again in the loop
                operations = operations[1:]
            img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        else:
            img = load_image(source)
            
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        
        for op in operations:
            op_type = op.get("type")
            if not op_type:
                continue
                
            if op_type == "crop":
                box = op.get("box")
                if box and len(box) == 4:
                    is_percentage = op.get("is_percentage", False)
                    if is_percentage:
                        w, h = img.size
                        left = int(box[0] * w / 100)
                        top = int(box[1] * h / 100)
                        right = int(box[2] * w / 100)
                        bottom = int(box[3] * h / 100)
                    else:
                        left, top, right, bottom = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                    
                    # Ensure coordinates are within image bounds
                    w, h = img.size
                    left = max(0, min(w - 1, left))
                    top = max(0, min(h - 1, top))
                    right = max(left + 1, min(w, right))
                    bottom = max(top + 1, min(h, bottom))
                    
                    img = img.crop((left, top, right, bottom))
                    
                    # Support multiple crop shapes
                    crop_shape = op.get("shape", "rectangle")
                    if crop_shape == "circle":
                        mask = Image.new("L", img.size, 0)
                        draw = ImageDraw.Draw(mask)
                        draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
                        orig_alpha = img.split()[3]
                        new_alpha = Image.composite(orig_alpha, Image.new("L", img.size, 0), mask)
                        img.putalpha(new_alpha)
                    elif crop_shape == "rounded":
                        radius = int(op.get("radius", min(img.size) // 10))
                        mask = Image.new("L", img.size, 0)
                        draw = ImageDraw.Draw(mask)
                        draw.rounded_rectangle((0, 0, img.size[0], img.size[1]), radius=radius, fill=255)
                        orig_alpha = img.split()[3]
                        new_alpha = Image.composite(orig_alpha, Image.new("L", img.size, 0), mask)
                        img.putalpha(new_alpha)
                    elif crop_shape == "freeform":
                        points = op.get("points", [])
                        if len(points) >= 3:
                            pts = []
                            for pt in points:
                                px = int(pt[0] * w / 100) - left
                                py = int(pt[1] * h / 100) - top
                                pts.append((px, py))
                            mask = Image.new("L", img.size, 0)
                            draw = ImageDraw.Draw(mask)
                            draw.polygon(pts, fill=255)
                            orig_alpha = img.split()[3]
                            new_alpha = Image.composite(orig_alpha, Image.new("L", img.size, 0), mask)
                            img.putalpha(new_alpha)
                    
            elif op_type == "rotate":
                angle = float(op.get("angle", 0))
                expand = op.get("expand", True)
                img = img.rotate(-angle, expand=expand, resample=Image.BICUBIC)
                
            elif op_type == "flip":
                direction = op.get("direction", "horizontal")
                if direction == "horizontal":
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                elif direction == "vertical":
                    img = img.transpose(Image.FLIP_TOP_BOTTOM)
                    
            elif op_type == "resize":
                width = int(op.get("width", img.size[0]))
                height = int(op.get("height", img.size[1]))
                img = img.resize((width, height), resample=Image.LANCZOS)
                
            elif op_type == "brightness":
                factor = float(op.get("factor", 1.0))
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(factor)
                
            elif op_type == "transparency":
                opacity = float(op.get("opacity", 1.0))
                r, g, b, a = img.split()
                a = a.point(lambda p: int(p * opacity))
                img = Image.merge("RGBA", (r, g, b, a))
                
            elif op_type == "filter":
                filter_name = op.get("name", "none")
                if filter_name == "grayscale":
                    alpha = img.split()[3]
                    img = ImageOps.grayscale(img).convert("RGBA")
                    img.putalpha(alpha)
                elif filter_name == "sepia":
                    sepia_matrix = (
                        0.393, 0.769, 0.189, 0,
                        0.349, 0.686, 0.168, 0,
                        0.272, 0.534, 0.131, 0
                    )
                    alpha = img.split()[3]
                    img = img.convert("RGB").convert("RGB", matrix=sepia_matrix).convert("RGBA")
                    img.putalpha(alpha)
                elif filter_name == "invert":
                    alpha = img.split()[3]
                    img = ImageOps.invert(img.convert("RGB")).convert("RGBA")
                    img.putalpha(alpha)
                    
            elif op_type == "tint":
                color_hex = op.get("color", "#ffffff").lstrip('#')
                tint_color = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
                tint_img = Image.new("RGBA", img.size, tint_color + (255,))
                img = Image.blend(img, tint_img, float(op.get("amount", 0.5)))
                
            elif op_type == "text":
                text = op.get("text", "")
                x = int(op.get("x", 0))
                y = int(op.get("y", 0))
                font_size = int(op.get("font_size", 20))
                color_hex = op.get("color", "#000000").lstrip('#')
                color = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4)) + (255,)
                
                bold = bool(op.get("bold", False))
                italic = bool(op.get("italic", False))
                underline = bool(op.get("underline", False))

                if bold and italic:
                    font_candidates = [
                        "arialbi.ttf",
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
                    ]
                elif bold:
                    font_candidates = [
                        "arialbd.ttf",
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    ]
                elif italic:
                    font_candidates = [
                        "ariali.ttf",
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
                    ]
                else:
                    font_candidates = [
                        "arial.ttf",
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    ]

                font = None
                for font_name in font_candidates:
                    try:
                        font = ImageFont.truetype(font_name, font_size)
                        break
                    except (OSError, IOError):
                        continue
                if font is None:
                    font = ImageFont.load_default()

                draw = ImageDraw.Draw(img)
                draw.text((x, y), text, fill=color, font=font)
                if underline and text:
                    text_bbox = draw.textbbox((x, y), text, font=font)
                    line_y = min(img.size[1] - 1, text_bbox[3] + max(1, font_size // 30))
                    line_width = max(1, font_size // 18)
                    draw.line((text_bbox[0], line_y, text_bbox[2], line_y), fill=color, width=line_width)
                
            elif op_type == "watermark":
                text = op.get("text", "WATERMARK")
                opacity = float(op.get("opacity", 0.3))
                color_hex = op.get("color", "#ffffff").lstrip('#')
                color = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4)) + (int(255 * opacity),)
                
                txt_img = Image.new("RGBA", img.size, (255, 255, 255, 0))
                draw = ImageDraw.Draw(txt_img)
                try:
                    font = ImageFont.truetype("arial.ttf", int(img.size[0] * 0.05))
                except:
                    font = ImageFont.load_default()
                
                text_bbox = draw.textbbox((0, 0), text, font=font)
                w = text_bbox[2] - text_bbox[0]
                h = text_bbox[3] - text_bbox[1]
                draw.text(((img.size[0] - w) // 2, (img.size[1] - h) // 2), text, fill=color, font=font)
                
                txt_img = txt_img.rotate(45, resample=Image.BICUBIC)
                img = Image.alpha_composite(img, txt_img)
                
            elif op_type == "remove_background":
                try:
                    from rembg import remove
                    if img.mode != "RGBA":
                        img = img.convert("RGBA")
                    img = remove(img)
                except Exception as ex:
                    import traceback
                    print(f"Error removing background: {traceback.format_exc()}")
                    raise Exception(f"Lỗi xóa nền: {str(ex)}")
                    
            elif op_type == "overlay":
                overlay_source = op.get("overlay_image_url")
                if overlay_source:
                    ox = int(op.get("x", 0))
                    oy = int(op.get("y", 0))
                    ow = op.get("width")
                    oh = op.get("height")
                    
                    overlay = load_image(overlay_source).convert("RGBA")
                    if ow and oh:
                        overlay = overlay.resize((int(ow), int(oh)), resample=Image.LANCZOS)
                    
                    temp = Image.new("RGBA", img.size, (255, 255, 255, 0))
                    temp.paste(overlay, (ox, oy), overlay)
                    img = Image.alpha_composite(img, temp)
                    
            elif op_type == "chroma_key":
                key_color_hex = op.get("color", "#ffffff").lstrip('#')
                key_color = tuple(int(key_color_hex[i:i+2], 16) for i in (0, 2, 4))
                tolerance = int(op.get("tolerance", 30))
                
                try:
                    import numpy as np
                    img_np = np.array(img)
                    r = img_np[:,:,0].astype(np.int32)
                    g = img_np[:,:,1].astype(np.int32)
                    b = img_np[:,:,2].astype(np.int32)
                    dist = np.sqrt((r - key_color[0])**2 + (g - key_color[1])**2 + (b - key_color[2])**2)
                    img_np[dist < tolerance, 3] = 0
                    img = Image.fromarray(img_np)
                except ImportError:
                    datas = img.getdata()
                    new_data = []
                    for item in datas:
                        dist = sum((item[i] - key_color[i]) ** 2 for i in range(3)) ** 0.5
                        if dist < tolerance:
                            new_data.append((item[0], item[1], item[2], 0))
                        else:
                            new_data.append(item)
                    img.putdata(new_data)
                    
            elif op_type == "merge":
                merge_sources = op.get("images", [])
                layout = op.get("layout", "horizontal")
                spacing = int(op.get("spacing", 0))
                bg_hex = op.get("background_color", "#ffffff").lstrip('#')
                if len(bg_hex) == 6:
                    bg_color = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4)) + (255,)
                elif len(bg_hex) == 8:
                    bg_color = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4, 6))
                else:
                    bg_color = (255, 255, 255, 0)
                
                all_images = [img]
                for src in merge_sources:
                    try:
                        all_images.append(load_image(src).convert("RGBA"))
                    except Exception as e:
                        print(f"Error loading image for merge: {e}")
                
                if len(all_images) > 1:
                    if layout == "horizontal":
                        total_width = sum(i.size[0] for i in all_images) + spacing * (len(all_images) - 1)
                        max_height = max(i.size[1] for i in all_images)
                        merged_img = Image.new("RGBA", (total_width, max_height), bg_color)
                        current_x = 0
                        for i in all_images:
                            paste_y = (max_height - i.size[1]) // 2
                            merged_img.paste(i, (current_x, paste_y), i)
                            current_x += i.size[0] + spacing
                        img = merged_img
                    elif layout == "vertical":
                        max_width = max(i.size[0] for i in all_images)
                        total_height = sum(i.size[1] for i in all_images) + spacing * (len(all_images) - 1)
                        merged_img = Image.new("RGBA", (max_width, total_height), bg_color)
                        current_y = 0
                        for i in all_images:
                            paste_x = (max_width - i.size[0]) // 2
                            merged_img.paste(i, (paste_x, current_y), i)
                            current_y += i.size[1] + spacing
                        img = merged_img
                    elif layout == "grid":
                        n = len(all_images)
                        cols = int(n ** 0.5)
                        if cols * cols < n:
                            cols += 1
                        rows = (n + cols - 1) // cols
                        cell_w = max(i.size[0] for i in all_images)
                        cell_h = max(i.size[1] for i in all_images)
                        grid_w = cell_w * cols + spacing * (cols - 1)
                        grid_h = cell_h * rows + spacing * (rows - 1)
                        merged_img = Image.new("RGBA", (grid_w, grid_h), bg_color)
                        for idx, i in enumerate(all_images):
                            r = idx // cols
                            c = idx % cols
                            px = c * (cell_w + spacing) + (cell_w - i.size[0]) // 2
                            py = r * (cell_h + spacing) + (cell_h - i.size[1]) // 2
                            merged_img.paste(i, (px, py), i)
                        img = merged_img
                        
            elif op_type == "color_adjust":
                if "contrast" in op:
                    contrast_factor = float(op["contrast"])
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(contrast_factor)
                if "color" in op:
                    color_factor = float(op["color"])
                    enhancer = ImageEnhance.Color(img)
                    img = enhancer.enhance(color_factor)
                if "sharpness" in op:
                    sharpness_factor = float(op["sharpness"])
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(sharpness_factor)

            elif op_type == "blur":
                radius = float(op.get("radius", 2))
                img = img.filter(ImageFilter.GaussianBlur(radius=radius))

            elif op_type == "sharpen":
                amount = float(op.get("amount", 2))
                percent = int(max(0, amount) * 75)
                img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=percent, threshold=3))

            elif op_type == "border":
                thickness = int(op.get("thickness", 10))
                color_hex = op.get("color", "#000000").lstrip('#')
                if len(color_hex) == 6:
                    border_color = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4)) + (255,)
                elif len(color_hex) == 8:
                    border_color = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4, 6))
                else:
                    border_color = (0, 0, 0, 255)
                img = ImageOps.expand(img, border=thickness, fill=border_color)

            elif op_type == "shadow":
                offset_x = int(op.get("offset_x", 10))
                offset_y = int(op.get("offset_y", 10))
                blur_radius = float(op.get("blur", 8))
                color_hex = op.get("color", "#000000").lstrip('#')
                shadow_opacity = float(op.get("opacity", 0.5))
                if len(color_hex) >= 6:
                    sc = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
                else:
                    sc = (0, 0, 0)
                shadow_rgba = sc + (int(255 * shadow_opacity),)
                margin = int(blur_radius * 2 + max(abs(offset_x), abs(offset_y)))
                canvas_w = img.size[0] + margin * 2
                canvas_h = img.size[1] + margin * 2
                # Build shadow from the image's alpha silhouette
                alpha = img.split()[3]
                shadow_layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
                solid = Image.new("RGBA", img.size, shadow_rgba)
                shadow_layer.paste(solid, (margin + offset_x, margin + offset_y), alpha)
                shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
                base = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
                base = Image.alpha_composite(base, shadow_layer)
                base.paste(img, (margin, margin), img)
                img = base

        # Determine output format (jpg flattens transparency onto white)
        fmt = (export_format or "png").lower()
        is_jpeg = fmt in ("jpg", "jpeg")

        def _flatten_for_jpeg(image):
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            bg = Image.new("RGBA", image.size, (255, 255, 255, 255))
            return Image.alpha_composite(bg, image).convert("RGB")

        if return_type == "base64":
            buffered = io.BytesIO()
            if is_jpeg:
                _flatten_for_jpeg(img).save(buffered, format="JPEG", quality=int(quality), optimize=True)
                img_str = base64.b64encode(buffered.getvalue()).decode()
                return f"data:image/jpeg;base64,{img_str}"
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"

        elif return_type == "cloudinary":
            import cloudinary.uploader
            buffered = io.BytesIO()
            if is_jpeg:
                _flatten_for_jpeg(img).save(buffered, format="JPEG", quality=int(quality), optimize=True)
            else:
                img.save(buffered, format="PNG")
            buffered.seek(0)
            upload_result = cloudinary.uploader.upload(
                buffered,
                folder="image_generation",
                resource_type="image",
                public_id=f"edited_{int(datetime.now().timestamp())}"
            )
            return upload_result.get("secure_url") or ""

        else:
            if not os.path.exists(IMAGES_OUTPUT_DIR):
                os.makedirs(IMAGES_OUTPUT_DIR)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            if is_jpeg:
                filename = f"edited_image_{timestamp}.jpg"
                filepath = os.path.join(IMAGES_OUTPUT_DIR, filename)
                _flatten_for_jpeg(img).save(filepath, format="JPEG", quality=int(quality), optimize=True)
            else:
                filename = f"edited_image_{timestamp}.png"
                filepath = os.path.join(IMAGES_OUTPUT_DIR, filename)
                img.save(filepath, format="PNG")
            return os.path.abspath(filepath)
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise Exception(f"Lỗi xử lý ảnh bằng Pillow: {str(e)}")

def cleanup_image_file(filepath: str):
    """
    Delete image file after uploading to Cloudinary

    Args:
        filepath: Path to the image file to delete
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Lỗi xóa file: {str(e)}")
