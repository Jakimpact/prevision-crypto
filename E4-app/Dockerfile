# Multi-stage build for E4 Flask application
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_HOME=/app \
    PORT=5000

WORKDIR $APP_HOME

# System deps (add any OS packages if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && rm -rf /var/lib/apt/lists/*

# Install dependencies first (better layer caching)
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source
COPY . .

# Optionally disable monitoring unless explicitly enabled at runtime
ENV DISABLE_MONITORING=1

EXPOSE 5000

# Healthcheck (simple: ensure process up)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:5000/ || exit 1

CMD ["python", "app.py"]
