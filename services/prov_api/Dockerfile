FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY common ./common
COPY services/prov_api ./prov_api

RUN pip install --no-cache-dir --upgrade pip


WORKDIR /app/common
RUN pip install --no-cache-dir .

WORKDIR /app/prov_api
RUN pip install --no-cache-dir .


EXPOSE 5000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app.main:create_app()"]