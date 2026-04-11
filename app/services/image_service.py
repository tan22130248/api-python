from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import requests

IMAGES_OUTPUT_DIR = "images"

if not os.path.exists(IMAGES_OUTPUT_DIR):
    os.makedirs(IMAGES_OUTPUT_DIR)

from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import random

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