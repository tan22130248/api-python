import difflib
import json
import os
from pathlib import Path
from threading import Lock

import av
from vosk import KaldiRecognizer, Model, SetLogLevel


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "vosk-model-small-en-us-0.15"
VOSK_MODEL_PATH = Path(os.getenv("VOSK_MODEL_PATH", str(DEFAULT_MODEL_PATH))).resolve()
SAMPLE_RATE = 16_000

_model = None
_model_lock = Lock()


def get_vosk_model() -> Model:
    """Nạp model Vosk một lần và tái sử dụng cho các request sau."""
    global _model
    if _model is not None:
        return _model

    with _model_lock:
        if _model is None:
            if not VOSK_MODEL_PATH.is_dir():
                raise RuntimeError(f"Không tìm thấy model Vosk tại: {VOSK_MODEL_PATH}")
            SetLogLevel(-1)
            _model = Model(str(VOSK_MODEL_PATH))
    return _model


def _pcm_chunks(audio_file_path: str):
    """Giải mã mọi định dạng PyAV hỗ trợ thành PCM mono 16-bit, 16 kHz."""
    try:
        with av.open(audio_file_path) as container:
            if not container.streams.audio:
                raise RuntimeError("File không có luồng âm thanh")

            stream = container.streams.audio[0]
            resampler = av.AudioResampler(format="s16", layout="mono", rate=SAMPLE_RATE)
            for frame in container.decode(stream):
                for converted in resampler.resample(frame):
                    yield converted.to_ndarray().tobytes()
            for converted in resampler.resample(None):
                yield converted.to_ndarray().tobytes()
    except (av.error.FFmpegError, OSError, ValueError) as exc:
        raise RuntimeError(f"Không thể đọc file âm thanh: {exc}") from exc


def _feedback(accuracy: float) -> str:
    if accuracy >= 99.95:
        return "Tuyệt đối! (Perfect)"
    if accuracy > 70:
        return "Rất tốt (Good)"
    return "Cần cố gắng (Try again)"


def check_pronunciation(audio_file_path: str, target_text: str) -> dict:
    """Nhận dạng bằng Vosk và chấm độ tương đồng với câu mẫu."""
    recognizer = KaldiRecognizer(get_vosk_model(), SAMPLE_RATE)
    recognizer.SetWords(True)
    recognized_parts = []

    for chunk in _pcm_chunks(audio_file_path):
        if chunk and recognizer.AcceptWaveform(chunk):
            text = json.loads(recognizer.Result()).get("text", "").strip()
            if text:
                recognized_parts.append(text)

    final_text = json.loads(recognizer.FinalResult()).get("text", "").strip()
    if final_text:
        recognized_parts.append(final_text)

    recognized_text = " ".join(recognized_parts).strip()
    if not recognized_text:
        return {
            "recognized_text": "",
            "accuracy_score": "0%",
            "feedback": "Không nghe rõ, thử lại nhé!",
            "model_used": "vosk",
        }

    accuracy = difflib.SequenceMatcher(
        None, recognized_text.casefold(), target_text.strip().casefold()
    ).ratio() * 100
    return {
        "recognized_text": recognized_text,
        "accuracy_score": f"{accuracy:.1f}%",
        "feedback": _feedback(accuracy),
        "model_used": "vosk",
    }
