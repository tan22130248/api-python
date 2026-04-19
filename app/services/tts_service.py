from gtts import gTTS
import os
from datetime import datetime

AUDIO_OUTPUT_DIR = "audios"

if not os.path.exists(AUDIO_OUTPUT_DIR):
    os.makedirs(AUDIO_OUTPUT_DIR)

def convert_text_to_speech(text: str) -> str:
    """
    Convert Vietnamese text to speech using gTTS
    
    Args:
        text: Vietnamese text to convert
        
    Returns:
        Filename of the generated audio file
        
    Raises:
        Exception: If conversion fails
    """
    if not text or text.strip() == "":
        raise Exception("Text không được để trống")
    
    try:
        tts = gTTS(text=text, lang='vi', slow=False)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"output_audio_{timestamp}.mp3"
        filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
        
        tts.save(filepath)
        
        return os.path.abspath(filepath)
        
    except Exception as e:
        raise Exception(f"Lỗi chuyển đổi: {str(e)}")

def cleanup_audio_file(filepath: str):
    """
    Delete audio file after uploading to Cloudinary
    
    Args:
        filepath: Path to the audio file to delete
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Lỗi xóa file: {str(e)}")
