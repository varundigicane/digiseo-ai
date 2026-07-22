# DigiSEO Worker — Railway optional service
# Root Directory = repo root (needs apps/api + apps/worker)

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY apps/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY apps/api /app/apps/api
COPY apps/worker /app/apps/worker

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/apps/api:/app/apps/worker \
    APP_ENV=production

WORKDIR /app/apps/worker
CMD ["python", "-m", "worker.main"]
