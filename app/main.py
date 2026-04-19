from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .api import tts, image, canvas, pronunciation
from .core.config import init_cloudinary
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Service - Text to Speech and Image Generation",
    description="API for converting Vietnamese text to speech and generating images from descriptions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

init_cloudinary()

app.include_router(tts.router, prefix="/api/tts", tags=["TTS"])
app.include_router(image.router, prefix="/api/image", tags=["Image"])
app.include_router(canvas.router, prefix="/api/canvas", tags=["Canvas"])
app.include_router(pronunciation.router, prefix="/api/pronunciation", tags=["Pronunciation"])

from app.services.canvas_service import ICONS_DIR, CANVAS_EXPORTS_DIR
if os.path.exists(CANVAS_EXPORTS_DIR):
    app.mount("/canvas_exports", StaticFiles(directory=CANVAS_EXPORTS_DIR), name="canvas_exports")

@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Service - TTS & Image",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "service": "AI Service - Text to Speech & Image Generation",
        "version": "1.0.0",
        "endpoints": {
            "convert": "/api/tts/convert",
            "generate": "/api/image/generate",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
