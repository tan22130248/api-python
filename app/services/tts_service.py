from gtts import gTTS
import os
from datetime import datetime

AUDIO_OUTPUT_DIR = "audios"

# Create audios directory if not exists
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
        # Create gTTS instance for Vietnamese
        tts = gTTS(text=text, lang='vi', slow=False)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"output_audio_{timestamp}.mp3"
        filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
        
        # Save audio file
        tts.save(filepath)
        
        # Return absolute path so backend can access the file correctly
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
