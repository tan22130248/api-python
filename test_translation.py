import sys
import os

# Add app to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.services.translation_service import translate_text

try:
    print("Translating vi -> en...")
    en = translate_text("Xin chào, tôi là giáo viên.", "vi", "en")
    print(f"vi->en: {en}")
    
    print("Translating en -> vi...")
    vi = translate_text("Hello, I am a teacher.", "en", "vi")
    print(f"en->vi: {vi}")
except Exception as e:
    print(f"Error: {e}")
