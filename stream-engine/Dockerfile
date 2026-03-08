# Use Python as base for streaming logic
FROM python:3.11-slim

# Install FFmpeg for streaming
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Generate a placeholder video so the stream engine never crashes
RUN mkdir -p media/assets media/ads media/video && \
    ffmpeg -y -f lavfi -i color=c=blue:s=1920x1080:d=10 -f lavfi -i anullsrc=r=48000:cl=stereo -c:v libx264 -c:a aac -shortest media/assets/placeholder_loop.mp4

# Environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the streamer
CMD ["python", "streamer.py"]
