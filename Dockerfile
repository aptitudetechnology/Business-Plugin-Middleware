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

# Create necessary directories and set permissions
RUN mkdir -p logs uploads config database data

# Copy default configuration if it doesn't exist
RUN if [ ! -f config/config.ini ]; then cp config/config.ini.example config/config.ini || true; fi

# Create non-root user
RUN useradd --create-home --shell /bin/bash middleware

# Create startup script to handle permissions
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'echo "🚀 Starting Business Plugin Middleware..."' >> /app/start.sh && \
    echo 'echo "📁 Created necessary directories"' >> /app/start.sh && \
    echo 'mkdir -p /app/logs /app/uploads /app/data /app/config' >> /app/start.sh && \
    echo 'chmod 755 /app/logs /app/uploads /app/data /app/config' >> /app/start.sh && \
    echo 'echo "🐍 Starting Python application..."' >> /app/start.sh && \
    echo 'cd /app && python web/app.py' >> /app/start.sh && \
    chmod +x /app/start.sh

# Set ownership but run as root to handle volume permissions
RUN chown -R middleware:middleware /app

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=web/app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Use startup script to handle permissions and start app
CMD ["/app/start.sh"]
