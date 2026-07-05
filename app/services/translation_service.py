import logging
import os
import re
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

_models: Dict[str, object] = {}
_tokenizers: Dict[str, object] = {}

MODEL_MAP = {
    ("vi", "en"): "Helsinki-NLP/opus-mt-vi-en",
    ("en", "vi"): "Helsinki-NLP/opus-mt-en-vi",
}

SUPPORTED_LANGUAGES = {
    "vi": "Tiếng Việt",
    "en": "English",
}

MAX_SEGMENT_LENGTH = 512
MODEL_CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'model_cache'))
os.makedirs(MODEL_CACHE_DIR, exist_ok=True)


def _load_model(source_lang: str, target_lang: str):
    """
    Lazy-load MarianMT model and tokenizer for a given language pair.
    Models are cached after first load.
    """
    key = (source_lang, target_lang)
    if key in _models and key in _tokenizers:
        return _tokenizers[key], _models[key]

    model_name = MODEL_MAP.get(key)
    if not model_name:
        raise ValueError(f"Không hỗ trợ cặp ngôn ngữ: {source_lang} → {target_lang}")

    logger.info(f"Loading MarianMT model: {model_name} (cache: {MODEL_CACHE_DIR}) ...")
    try:
        from transformers import MarianMTModel, MarianTokenizer

        tokenizer = MarianTokenizer.from_pretrained(model_name, cache_dir=MODEL_CACHE_DIR)
        model = MarianMTModel.from_pretrained(model_name, cache_dir=MODEL_CACHE_DIR)
        model.eval()

        _tokenizers[key] = tokenizer
        _models[key] = model

        logger.info(f"Model {model_name} loaded successfully!")
        return tokenizer, model
    except Exception as e:
        logger.error(f"Failed to load model {model_name}: {e}")
        raise Exception(f"Lỗi tải mô hình dịch: {str(e)}")


def _split_into_segments(text: str, max_length: int = 400) -> List[str]:
    """
    Split long text into segments at sentence boundaries for MarianMT.
    Each segment should not exceed max_length characters.
    """
    sentences = re.split(r'(?<=[.!?。])\s+', text.strip())

    segments = []
    current_segment = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(sentence) > max_length:
            if current_segment:
                segments.append(current_segment.strip())
                current_segment = ""

            sub_parts = sentence.split('\n')
            for part in sub_parts:
                part = part.strip()
                if not part:
                    continue
                if len(part) <= max_length:
                    segments.append(part)
                else:
                    # Force split at max_length boundaries
                    for i in range(0, len(part), max_length):
                        segments.append(part[i:i + max_length].strip())
            continue

        if current_segment and len(current_segment) + len(sentence) + 1 > max_length:
            segments.append(current_segment.strip())
            current_segment = sentence
        else:
            current_segment = (current_segment + " " + sentence).strip() if current_segment else sentence

    if current_segment.strip():
        segments.append(current_segment.strip())

    return segments if segments else [text.strip()]


def translate_text(text: str, source_lang: str = "vi", target_lang: str = "en") -> str:
    """
    Translate a short text using MarianMT.

    Args:
        text: Text to translate
        source_lang: Source language code ('vi' or 'en')
        target_lang: Target language code ('vi' or 'en')

    Returns:
        Translated text string
    """
    if not text or text.strip() == "":
        raise ValueError("Text không được để trống")

    if source_lang == target_lang:
        return text

    if source_lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Ngôn ngữ nguồn không hỗ trợ: {source_lang}")
    if target_lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Ngôn ngữ đích không hỗ trợ: {target_lang}")

    tokenizer, model = _load_model(source_lang, target_lang)

    try:
        import torch

        inputs = tokenizer(text.strip(), return_tensors="pt", padding=True, truncation=True, max_length=MAX_SEGMENT_LENGTH)

        with torch.no_grad():
            translated = model.generate(**inputs)

        result = tokenizer.decode(translated[0], skip_special_tokens=True)
        return result
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise Exception(f"Lỗi dịch thuật: {str(e)}")


def translate_document(text: str, source_lang: str = "vi", target_lang: str = "en") -> Dict:
    """
    Translate a long document by splitting into segments.

    Args:
        text: Long document text
        source_lang: Source language code
        target_lang: Target language code

    Returns:
        Dictionary with translated segments and full text
    """
    if not text or text.strip() == "":
        raise ValueError("Text không được để trống")

    if source_lang == target_lang:
        return {
            "translated_text": text,
            "segments": [{"original": text, "translated": text}],
            "total_segments": 1,
        }

    segments = _split_into_segments(text)
    translated_segments = []
    translated_parts = []

    for segment in segments:
        translated = translate_text(segment, source_lang, target_lang)
        translated_segments.append({
            "original": segment,
            "translated": translated,
        })
        translated_parts.append(translated)

    return {
        "translated_text": " ".join(translated_parts),
        "segments": translated_segments,
        "total_segments": len(segments),
    }


def get_supported_languages() -> Dict[str, str]:
    """Return supported languages."""
    return SUPPORTED_LANGUAGES
