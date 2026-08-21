from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
import logging
from urllib.parse import quote
from app.services.file_translation_service import translate_docx_file, translate_txt_file, translate_pptx_file

router = APIRouter(prefix="/api/translate", tags=["translate-file"])
logger = logging.getLogger(__name__)


def _translated_content_disposition(filename: str) -> str:
    """Build an ASCII-only HTTP header while preserving Unicode names via RFC 5987."""
    original_name = (filename or "document").replace("\\", "/").split("/")[-1]
    translated_name = f"translated_{original_name}"
    ascii_name = "".join(
        char if char.isascii() and (char.isalnum() or char in ".-_") else "_"
        for char in translated_name
    ).strip(".") or "translated_document"
    encoded_name = quote(translated_name, safe="")
    return f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{encoded_name}"


@router.post("/document/file")
async def translate_document_file(
    file: UploadFile = File(...),
    source_lang: str = Form(default="vi"),
    target_lang: str = Form(default="en")
):
    """
    Upload a document file, translate its content, return translated file.
    User can choose to save or discard the result.
    Supports: .docx, .txt
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Tên tệp không hợp lệ")

    filename = file.filename.lower()
    content = await file.read()

    try:
        if filename.endswith(".docx"):
            translated_bytes = translate_docx_file(content, source_lang, target_lang)
            return Response(
                content=translated_bytes,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={"Content-Disposition": _translated_content_disposition(file.filename)}
            )

        elif filename.endswith(".txt"):
            translated_bytes = translate_txt_file(content, source_lang, target_lang)
            return Response(
                content=translated_bytes,
                media_type="text/plain",
                headers={"Content-Disposition": _translated_content_disposition(file.filename)}
            )

        elif filename.endswith(".pptx"):
            translated_bytes = translate_pptx_file(content, source_lang, target_lang)
            return Response(
                content=translated_bytes,
                media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                headers={"Content-Disposition": _translated_content_disposition(file.filename)}
            )

        else:
            raise HTTPException(
                status_code=400,
                detail="Chỉ hỗ trợ .docx, .txt và .pptx."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error translating file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi dịch tài liệu: {str(e)}")
