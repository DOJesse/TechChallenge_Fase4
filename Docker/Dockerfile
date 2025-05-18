FROM python:3.12-slim

WORKDIR /app

# Instala curl e limpa cache do apt
RUN apt-get update \
 && apt-get install -y curl \
 && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install prometheus_client gunicorn

# Copia todo o código da app (incluindo app/model/model_lstm.keras)
COPY ../app/ ./

EXPOSE 5000

CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "main:app"]
