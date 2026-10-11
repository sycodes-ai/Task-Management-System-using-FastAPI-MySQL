# Stage 1: build the React app
FROM node:20-alpine AS frontend
WORKDIR /build

COPY my-react-app/package.json my-react-app/package-lock.json ./
RUN npm ci

COPY my-react-app/ ./
# Set to "false" to hide the demo accounts box on the login page
ARG VITE_DEMO_MODE=true
ENV VITE_DEMO_MODE=$VITE_DEMO_MODE
RUN npm run build


# Stage 2: FastAPI serving the API and the built React app
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STATIC_DIR=/app/static

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY app ./app
COPY --from=frontend /build/dist ./static

# Run as a normal user; /app must be writable for the default SQLite file (./tasks.db)
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/api/v1/health' % os.environ.get('PORT', '8000'), timeout=3)"

# Render sets PORT; "exec" lets uvicorn receive the stop signal
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
