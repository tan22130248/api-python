from gtts import gTTS
import base64
import os
from datetime import datetime
from typing import Tuple

AUDIO_OUTPUT_DIR = "audios"

if not os.path.exists(AUDIO_OUTPUT_DIR):
    os.makedirs(AUDIO_OUTPUT_DIR)

SUPPORTED_LANGUAGES = {
    "vi": "Tiếng Việt",
    "en": "English",
}


def convert_text_to_speech(text: str, language: str = "vi", slow: bool = False) -> Tuple[str, str]:
    """
    Convert text to speech using gTTS.
    Returns (absolute_filepath, base64_audio) so remote callers can upload without shared disk.
    """
    if not text or text.strip() == "":
        raise Exception("Text không được để trống")

    lang = (language or "vi").strip().lower()
    if lang not in SUPPORTED_LANGUAGES:
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
        abs_path = os.path.abspath(filepath)

        with open(abs_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("ascii")

        # Best-effort cleanup of local temp file
        try:
            os.remove(abs_path)
        except OSError:
            pass

        return abs_path, audio_b64

    except Exception as e:
        raise Exception(f"Lỗi chuyển đổi: {str(e)}")


def cleanup_audio_file(filepath: str):
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Lỗi xóa file: {str(e)}")
