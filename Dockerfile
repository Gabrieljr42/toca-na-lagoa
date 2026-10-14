# Stage 1: build the Vue front end with Vite.
FROM node:22.12-alpine AS frontend

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY frontend/ ./
RUN npm run build

# Stage 2: Python API serving the built front end.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/app/data \
    FRONTEND_DIST=/app/frontend/dist \
    TZ=America/Sao_Paulo

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY --from=frontend /frontend/dist ./frontend/dist

RUN useradd --create-home --uid 1000 appuser && mkdir -p /app/data && chown appuser /app/data
USER appuser

EXPOSE 8080
# PORT is set by hosting platforms such as Railway; docker-compose uses the default.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --proxy-headers --forwarded-allow-ips='*'"]
