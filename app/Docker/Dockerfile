# Usar uma imagem base do Python
FROM python:3.9-slim

# Definir o diretório de trabalho
WORKDIR /app

# Copiar os arquivos necessários
COPY Docker/requirements.txt ./requirements.txt
COPY application/main.py ./main.py

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Comando padrão
CMD ["python", "main.py"]