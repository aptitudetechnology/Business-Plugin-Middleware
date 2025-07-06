# BigCapitalPy Dockerfile
# Multi-stage build for Python Flask application

# Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements-python.txt ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements-python.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    FLASK_APP=app.py \
    FLASK_ENV=production

# Schema checking environment variables (passive mode)
ENV SCHEMA_CHECK_MODE=warning \
    SCHEMA_CHECK_STRICT=false \
    SCHEMA_CHECK_ENABLED=true \
    SCHEMA_CHECK_FAIL_ON_ERROR=false \
    SCHEMA_CHECK_LOG_LEVEL=warning

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r bigcapital && useradd -r -g bigcapital bigcapital

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . .

# Copy the schema checker script and ensure scripts directory exists
RUN mkdir -p /app/scripts
COPY scripts/check_schema.py /app/scripts/check_schema.py

# Create necessary directories and set permissions
RUN mkdir -p uploads logs static && \
    chown -R bigcapital:bigcapital /app

# Switch to non-root user
USER bigcapital

# Expose port
EXPOSE 5000

# Health check (application only, no schema validation to avoid crashes)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["python", "app.py"]