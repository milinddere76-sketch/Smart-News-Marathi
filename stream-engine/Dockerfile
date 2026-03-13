# Use Python as base for streaming logic
FROM python:3.11-slim

# Install FFmpeg for streaming + Marathi fonts
RUN apt-get update && apt-get install -y \
    ffmpeg \
    fonts-noto \
    fonts-noto-cjk \
    fonts-indic \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -fv

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure media directories exist
RUN mkdir -p media/assets media/ads media/video

# Environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the streamer
CMD ["python", "streamer.py"]
