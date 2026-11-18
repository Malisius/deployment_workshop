# ==============================================================================
# Production Dockerfile - Deployment Workshop
# ==============================================================================
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    APP_ENV=production

WORKDIR /app

# Install curl for container HEALTHCHECK
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY wsgi.py .
COPY app/ app/

# Create a secure non-root user
RUN useradd -u 10001 -m -s /bin/bash appuser \
    && chown -R appuser:appuser /app

USER appuser

# Expose default application port
EXPOSE 5000

# Container healthcheck probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f "http://localhost:${PORT}/healthz?graceful=true" || exit 1

# Start production WSGI server using shell-variable expansion for dynamic PORT
CMD ["sh", "-c", "exec gunicorn --workers=2 --threads=4 --timeout=60 --bind=0.0.0.0:${PORT} wsgi:app"]
