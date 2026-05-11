# syntax=docker/dockerfile:1.6

# ─── Stage 1: build the Vite/React frontend ────────────────────────────────
FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# ─── Stage 2: Django runtime ───────────────────────────────────────────────
FROM python:3.13-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (lxml etc. needs libxml; curl-cffi pulls binaries already).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libxml2-dev libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install .

# Backend source
COPY backend/ ./backend/

# Built frontend from stage 1 — Django serves this via WhiteNoise.
COPY --from=frontend /app/frontend/dist ./frontend/dist

WORKDIR /app/backend
ENV DJANGO_SETTINGS_MODULE=config.settings \
    DEBUG=False

# Collect static + run migrations at build time so the image is self-contained.
# (Migrations also run at startup in case the volume schema is behind.)
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD sh -c "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 4 --timeout 90"
