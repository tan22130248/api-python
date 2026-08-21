FROM python:3.11-slim

# Install system dependencies needed for compiling some packages and system libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    ffmpeg \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download the recognition model during image build so the first student request never waits for it.
ENV WHISPER_MODEL_NAME=base
ENV WHISPER_DOWNLOAD_ROOT=/opt/faster-whisper
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu', compute_type='int8', download_root='/opt/faster-whisper')"
# Copy application source code
COPY . .

# Expose the API port
EXPOSE 8001

# Command to run the application
CMD ["python", "run.py"]
