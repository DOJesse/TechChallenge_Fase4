# Usar uma imagem base do Python
FROM python:3.12-slim

# Definir o diretório de trabalho
WORKDIR /app

# Instalar dependências de sistema necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivo de dependências
COPY Docker/requirements.txt ./requirements.txt

# Instalar pacotes Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar modelo
COPY ../modelTraining/model_lstm.keras /app/model/model_lstm.keras


# Variável de ambiente
ENV PYTHONUNBUFFERED=1

# Expor a porta do Flask
EXPOSE 5000

# Copiar o app (assume que main.py está em ../app no host, portanto ./app no contexto)
COPY ./app /app

# Comando padrão para rodar o Flask
CMD ["python", "main.py"]
