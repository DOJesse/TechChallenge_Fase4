FROM python:3.12-slim

WORKDIR /app

# Instala curl, poetry e limpa cache do apt
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 -

# Copia arquivos de configuração do Poetry
COPY ../app/pyproject.toml ../app/poetry.lock ./

# Instala dependências usando Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copia todo o código da app
COPY ../app/ ./

EXPOSE 5001

CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5001", "api.app:app"]
