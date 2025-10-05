# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Minimal build tools (optional but useful)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code
COPY app ./app

# Non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
