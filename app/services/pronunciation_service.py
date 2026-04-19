import glob
import os
import json
import wave
import audioop
import contextlib
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
from pydub.utils import which
import difflib

MODEL_PATH = "vosk-model-small-en-us-0.15"

def download_vosk_model():
    """Download Vosk model if not exists"""
    if not os.path.exists(MODEL_PATH):
        print("Downloading Vosk model...")
        import urllib.request
        import zipfile
        
        url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        zip_path = "vosk-model-small-en-us-0.15.zip"
        
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        os.remove(zip_path)
        print("Model downloaded and extracted successfully!")
    else:
        print("Vosk model already exists.")

from pydub.utils import which


def find_ffmpeg_binary():
    binary = which('ffmpeg') or which('ffmpeg.exe')
    if binary:
        return binary

    local_appdata = os.path.expanduser(os.path.join('~', 'AppData', 'Local'))
    patterns = [
        os.path.join(local_appdata, 'Microsoft', 'WinGet', 'Packages', 'Gyan.FFmpeg_*', 'ffmpeg-*', 'bin', 'ffmpeg.exe'),
        os.path.join(local_appdata, 'Programs', 'Gyan', 'FFmpeg', '*', 'bin', 'ffmpeg.exe'),
        os.path.join(local_appdata, 'Programs', 'FFmpeg', '*', 'bin', 'ffmpeg.exe'),
        os.path.join(local_appdata, 'ffmpeg', '*', 'bin', 'ffmpeg.exe'),
    ]

    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]

    return None

FFMPEG_BINARY = find_ffmpeg_binary()

if not FFMPEG_BINARY:
    print('Warning: ffmpeg binary not found in PATH. Please install ffmpeg or add it to PATH.')
else:
    print(f'Using ffmpeg binary at: {FFMPEG_BINARY}')
    AudioSegment.converter = FFMPEG_BINARY


def preprocess_wav_audio(audio_path):
    """Read WAV files directly without ffmpeg if possible."""
    with contextlib.closing(wave.open(audio_path, 'rb')) as wf:
        channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        sample_rate = wf.getframerate()
        frames = wf.readframes(wf.getnframes())

    if sample_width != 2:
        frames = audioop.lin2lin(frames, sample_width, 2)

    if channels > 1:
        frames = audioop.tomono(frames, 2, 1, 1)

    if sample_rate != 16000:
        frames, _ = audioop.ratecv(frames, 2, channels, sample_rate, 16000, None)

    return frames


def preprocess_audio(audio_path):
    """Convert audio to 16kHz mono WAV for Vosk"""
    if audio_path.lower().endswith('.wav'):
        try:
            return preprocess_wav_audio(audio_path)
        except Exception as e:
            raise RuntimeError(
                'Không thể xử lý file WAV. ' 
                'Hãy đảm bảo file WAV hợp lệ. ' 
                f'Chi tiết: {e}'
            )

    if not FFMPEG_BINARY:
        raise RuntimeError(
            'Không thể xử lý file âm thanh vì ffmpeg chưa được cài đặt. ' 
            'Hãy cài ffmpeg hoặc gửi file WAV.'
        )

    try:
        audio = AudioSegment.from_file(audio_path)
    except Exception as e:
        raise RuntimeError(
            'Không thể xử lý file âm thanh. ' 
            'Hãy đảm bảo ffmpeg đã được cài đặt và file có định dạng audio hợp lệ. ' 
            f'Chi tiết: {e}'
        )
    audio = audio.set_frame_rate(16000).set_channels(1)
    return audio.raw_data

def check_pronunciation(audio_file_path, target_text):
    """
    Check pronunciation using Vosk speech recognition
    
    Args:
        audio_file_path: Path to audio file
        target_text: Target text to compare against
        
    Returns:
        dict: Result with recognized text, accuracy score, and feedback
    """
    try:
        download_vosk_model()
        
        model = Model(MODEL_PATH)
        rec = KaldiRecognizer(model, 16000)
        
        audio_data = preprocess_audio(audio_file_path)
        
        rec.AcceptWaveform(audio_data)
        result = json.loads(rec.FinalResult())
        recognized_text = result.get('text', '').strip()
        
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
            "accuracy_score": "Err",
            "feedback": f"Lỗi hệ thống: {str(e)}"
        }
