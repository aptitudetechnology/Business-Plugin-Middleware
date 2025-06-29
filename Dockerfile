# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs uploads config database data

# Copy default configuration if it doesn't exist
RUN if [ ! -f config/config.ini ]; then cp config/config.ini.example config/config.ini || true; fi

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=web/app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Create non-root user
RUN useradd --create-home --shell /bin/bash middleware
RUN chown -R middleware:middleware /app
USER middleware

# Run application
CMD ["python", "web/app.py"]
