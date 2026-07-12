from gtts import gTTS
import os
from datetime import datetime

AUDIO_OUTPUT_DIR = "audios"

if not os.path.exists(AUDIO_OUTPUT_DIR):
    os.makedirs(AUDIO_OUTPUT_DIR)

# Ngôn ngữ hỗ trợ (gTTS codes)
SUPPORTED_LANGUAGES = {
    "vi": "Tiếng Việt",
    "en": "English",
}


def convert_text_to_speech(text: str, language: str = "vi", slow: bool = False) -> str:
    """
    Convert text to speech using gTTS (multi-language).
    """
    if not text or text.strip() == "":
        raise Exception("Text không được để trống")

    lang = (language or "vi").strip().lower()
    if lang not in SUPPORTED_LANGUAGES:
        # Fallback common aliases
        aliases = {"zh": "zh-cn", "cn": "zh-cn", "jp": "ja", "kr": "ko"}
        lang = aliases.get(lang, "vi")
        if lang not in SUPPORTED_LANGUAGES:
            lang = "vi"

    try:
        tts = gTTS(text=text, lang=lang, slow=bool(slow))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"output_audio_{lang}_{timestamp}.mp3"
        filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)

        tts.save(filepath)

        return os.path.abspath(filepath)

    except Exception as e:
        raise Exception(f"Lỗi chuyển đổi: {str(e)}")


def cleanup_audio_file(filepath: str):
    """Delete audio file after uploading to Cloudinary."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Lỗi xóa file: {str(e)}")
