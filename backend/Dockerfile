# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies + Marathi fonts
RUN apt-get update && apt-get install -y \
    ffmpeg \
    fonts-dejavu-core \
    fonts-noto \
    fonts-noto-cjk \
    fonts-indic \
    build-essential \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -fv

# Set the working directory in the container
WORKDIR /app

# Upgrade build tools and install CPU-only AI dependencies
# Using --extra-index-url ensures that sub-dependencies of basicsr/facexlib also find CPU wheels
ENV PIP_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu
ENV FORCE_CUDA=0
ENV TORCH_CUDA_ARCH_LIST=""

RUN pip install --no-cache-dir --upgrade pip setuptools wheel cython && \
    pip install --no-cache-dir \
    torch==2.2.2 \
    torchvision==0.17.2 \
    torchaudio==2.2.2 \
    numpy==1.23.4

# Copy requirements and install the rest
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Copy assets to a static location that isn't masked by a volume mount
RUN mkdir -p static_assets media/audio media/video media/anchor
COPY media/assets/ static_assets/

# Verification step: Fail build if core assets are missing in static_assets
RUN ls -la static_assets/ && \
    test -f static_assets/anchor_male.jpg && \
    test -f static_assets/anchor_female.jpg && \
    echo "✅ Core assets verified in static_assets"


# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/app"]
