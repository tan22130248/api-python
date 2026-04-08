from fastapi import FastAPI, HTTPException
from app.api import tts
from app.core.config import init_cloudinary
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Service - Text to Speech (TTS)",
    description="API for converting Vietnamese text to speech and uploading to Cloudinary",
    version="1.0.0"
)

# Initialize Cloudinary
init_cloudinary()

# Include routers
app.include_router(tts.router, prefix="/api/tts", tags=["TTS"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Service - TTS",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "service": "AI Service - Text to Speech",
        "version": "1.0.0",
        "endpoints": {
            "convert": "/api/tts/convert",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
