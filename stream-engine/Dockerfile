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

# Environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the streamer
CMD ["python", "streamer.py"]
