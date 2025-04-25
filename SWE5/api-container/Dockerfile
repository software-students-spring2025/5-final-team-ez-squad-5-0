FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for PyAudio and speech recognition
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    libportaudio2 \
    libportaudiocpp0 \
    libasound-dev \
    libpulse-dev \
    libsndfile1 \
    ffmpeg \
    swig \
    curl \
    build-essential \
    libffi-dev \
    libssl-dev \
    git \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5001

# Run the app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
