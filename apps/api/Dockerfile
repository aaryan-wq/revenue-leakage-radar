FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Fail the image build if domain modules are missing (wrong Railway root directory / context).
RUN python -c "import ingestion.pipeline; import verification.engine.pipeline; import workers.celery_app"

CMD ["sh", "worker.sh"]
