import os
from pathlib import Path

# Diretório base do projeto
BASE_DIR = Path(__file__).parent

# Caminhos dos arquivos
MODEL_PATH = BASE_DIR / 'assets' / 'model_lstm.keras'
TEMPLATES_DIR = BASE_DIR / 'templates'

# Configurações do modelo
SEQUENCE_LENGTH = 50
REQUIRED_COLUMNS = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

# Configurações da API
API_HOST = '0.0.0.0'
API_PORT = 5001

# Configurações de métricas
METRICS_BUCKETS = [0.005, 0.01, 0.025, 0.05, 0.1, 0.3, 1.0, 3.0, 10.0]
MODEL_METRICS_BUCKETS = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0] 