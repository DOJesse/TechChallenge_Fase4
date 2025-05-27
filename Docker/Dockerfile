FROM python:3.12-slim

WORKDIR /app

# Instala curl, poetry e limpa cache do apt
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

# Copia arquivos de configuração do Poetry
COPY ../app/pyproject.toml ./

# Instala dependências usando Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Ensure yfinance is installed
RUN pip install yfinance

# Copia todo o código da app
COPY ../app/ ./

# Dá permissão de execução ao script de inicialização
RUN chmod +x start.sh

# Expõe as portas necessárias
EXPOSE 5001 8501

# Usa o script como ponto de entrada
CMD ["./start.sh"]
