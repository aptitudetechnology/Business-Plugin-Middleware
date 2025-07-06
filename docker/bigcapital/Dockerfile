# Dockerfile for BigCapitalPy using pre-built image
# This extends the caston81/bigcapitalpy:latest image with any custom configuration

FROM caston81/bigcapitalpy:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# Schema checking environment variables (passive mode)
ENV SCHEMA_CHECK_MODE=warning \
    SCHEMA_CHECK_STRICT=false \
    SCHEMA_CHECK_ENABLED=true \
    SCHEMA_CHECK_FAIL_ON_ERROR=false \
    SCHEMA_CHECK_LOG_LEVEL=warning

# Create necessary directories if they don't exist
USER root
RUN mkdir -p /app/uploads /app/logs /app/static && \
    chown -R bigcapital:bigcapital /app/uploads /app/logs /app/static || true

# Switch back to non-root user
USER bigcapital

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# The pre-built image should already have the correct CMD, but we can override if needed
# CMD ["python", "app.py"]