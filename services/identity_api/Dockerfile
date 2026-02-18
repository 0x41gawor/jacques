FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# kopiujemy TYLKO potrzebne rzeczy
COPY common ./common
COPY services/identity_api ./identity_api

RUN pip install --no-cache-dir --upgrade pip

# instalujemy common
WORKDIR /app/common
RUN pip install --no-cache-dir . 

# instalujemy serwis
WORKDIR /app/identity_api
RUN pip install --no-cache-dir .

EXPOSE 5000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app.main:create_app()"]
