import difflib
from faster_whisper import WhisperModel

whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

def check_pronunciation(audio_file_path, target_text):
    """
    Check pronunciation using faster-whisper speech recognition (OpenAI Whisper reimplementation)
    
    faster-whisper is 4-5x faster than original Whisper and uses less RAM.
    It automatically handles multiple audio formats (WAV, MP3, WEBM, OGG, M4A, etc.)
    
    Args:
        audio_file_path: Path to audio file (any common audio format)
        target_text: Target text to compare against
        
    Returns:
        dict: Result with recognized text, accuracy score, and feedback
    """
    try:
       
        segments, info = whisper_model.transcribe(audio_file_path, beam_size=5)
        
        recognized_text = " ".join([segment.text for segment in segments]).strip()
        
        if not recognized_text:
            return {
                "recognized_text": "",
                "accuracy_score": "0%",
                "feedback": "Không nghe rõ, thử lại nhé!"
            }
        
        seq = difflib.SequenceMatcher(None, recognized_text.lower(), target_text.lower())
        accuracy = seq.ratio() * 100
        
        if accuracy == 100:
            feedback = "Tuyệt đối! (Perfect)"
        elif accuracy > 70:
            feedback = "Rất tốt (Good)"
        else:
            feedback = "Cần cố gắng (Try again)"
        
        return {
            "recognized_text": recognized_text,
            "accuracy_score": f"{accuracy:.1f}%",
            "feedback": feedback
        }
        
    except Exception as e:
        return {
            "recognized_text": "",
            "accuracy_score": "0%",
            "feedback": f"Lỗi xử lý âm thanh: {str(e)}"
        }
