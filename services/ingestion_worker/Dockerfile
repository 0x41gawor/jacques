FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY common ./common
COPY services/ingestion_worker ./ingestion_worker

RUN pip install --no-cache-dir --upgrade pip

WORKDIR /app/common
RUN pip install --no-cache-dir .

WORKDIR /app/ingestion_worker
RUN pip install --no-cache-dir .

EXPOSE 5000

CMD ["python", "-m", "app.main", "--log-level", "INFO"]