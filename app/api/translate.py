from fastapi import APIRouter, HTTPException
from app.schemas.translate_schema import (
    TranslateRequest,
    TranslateResponse,
    DocumentTranslateRequest,
    DocumentTranslateResponse,
    TranslatedSegment,
)

router = APIRouter()


@router.get("/health")
async def translate_health():
    """Translation Service health check"""
    return {
        "status": "healthy",
        "service": "Translation API (MarianMT)"
    }


@router.get("")
async def translate_info():
    """Translation service info endpoint"""
    return {
        "service": "Vietnamese-English Translation Service",
        "model": "MarianMT (Helsinki-NLP)",
        "endpoints": {
            "translate": "POST /api/translate/translate",
            "document": "POST /api/translate/document",
            "languages": "GET /api/translate/languages",
            "health": "GET /api/translate/health",
        }
    }


@router.get("/languages")
async def get_languages():
    """Get supported language pairs"""
    from app.services.translation_service import get_supported_languages

    languages = get_supported_languages()
    return {
        "success": True,
        "languages": languages,
        "supported_pairs": [
            {"source": "vi", "target": "en", "label": "Việt → Anh"},
            {"source": "en", "target": "vi", "label": "Anh → Việt"},
        ]
    }


@router.post("/translate", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    """
    Translate text between Vietnamese and English using MarianMT.

    Args:
        request: TranslateRequest with text, source_lang, target_lang

    Returns:
        TranslateResponse with translated text
    """
    try:
        if not request.text or request.text.strip() == "":
            raise HTTPException(status_code=400, detail="Text không được để trống")

        if len(request.text) > 10000:
            raise HTTPException(status_code=400, detail="Text không được vượt quá 10000 ký tự")

        if request.source_lang not in ("vi", "en"):
            raise HTTPException(status_code=400, detail="Ngôn ngữ nguồn chỉ hỗ trợ 'vi' hoặc 'en'")

        if request.target_lang not in ("vi", "en"):
            raise HTTPException(status_code=400, detail="Ngôn ngữ đích chỉ hỗ trợ 'vi' hoặc 'en'")

        if request.source_lang == request.target_lang:
            return TranslateResponse(
                success=True,
                message="Ngôn ngữ nguồn và đích giống nhau",
                original_text=request.text,
                translated_text=request.text,
                source_lang=request.source_lang,
                target_lang=request.target_lang,
            )

        from app.services.translation_service import translate_text as do_translate

        translated = do_translate(
            request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )

        return TranslateResponse(
            success=True,
            message="Dịch thành công",
            original_text=request.text,
            translated_text=translated,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi dịch thuật: {str(e)}")


@router.post("/document", response_model=DocumentTranslateResponse)
async def translate_document(request: DocumentTranslateRequest):
    """
    Translate a long document by splitting into segments.

    Args:
        request: DocumentTranslateRequest with text, source_lang, target_lang

    Returns:
        DocumentTranslateResponse with translated segments
    """
    try:
        if not request.text or request.text.strip() == "":
            raise HTTPException(status_code=400, detail="Text không được để trống")

        if len(request.text) > 50000:
            raise HTTPException(status_code=400, detail="Tài liệu không được vượt quá 50000 ký tự")

        from app.services.translation_service import translate_document as do_translate_doc

        result = do_translate_doc(
            request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )

        segments = [
            TranslatedSegment(original=s["original"], translated=s["translated"])
            for s in result["segments"]
        ]

        return DocumentTranslateResponse(
            success=True,
            message="Dịch tài liệu thành công",
            original_text=request.text,
            translated_text=result["translated_text"],
            segments=segments,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            total_segments=result["total_segments"],
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi dịch tài liệu: {str(e)}")
