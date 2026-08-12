import difflib
import re
import unicodedata
from threading import Lock

from faster_whisper import WhisperModel


_whisper_model = None
_model_lock = Lock()


def get_whisper_model():
    """Nạp Faster-Whisper một lần khi có yêu cầu đầu tiên."""
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model

    with _model_lock:
        if _whisper_model is None:
            _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    return _whisper_model


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value or "").casefold()
    return " ".join(re.findall(r"[^\W_]+", normalized, flags=re.UNICODE))


def _target_language(target_text: str) -> str:
    vietnamese_marks = "ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ"
    return "vi" if any(char in vietnamese_marks for char in target_text.casefold()) else "en"

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
       
        segments, _ = get_whisper_model().transcribe(
            audio_file_path,
            beam_size=5,
            language=_target_language(target_text),
            condition_on_previous_text=False,
        )
        
        recognized_text = " ".join([segment.text for segment in segments]).strip()
        
        if not recognized_text:
            return {
                "recognized_text": "",
                "accuracy_score": "0%",
                "feedback": "Không nghe rõ, thử lại nhé!"
            }
        
        seq = difflib.SequenceMatcher(
            None,
            _normalize_text(recognized_text),
            _normalize_text(target_text),
        )
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
        
    except Exception as exc:
        raise RuntimeError(f"Không thể nhận dạng file âm thanh: {exc}") from exc
