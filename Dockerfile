FROM python:3.12-slim

# Install Tesseract and OpenCV system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY backend ./backend
COPY frontend ./frontend
COPY models ./models

# Create uploads directory
RUN mkdir -p uploads

# Render provides the PORT environment variable
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}