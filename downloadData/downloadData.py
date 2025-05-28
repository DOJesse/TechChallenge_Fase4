import yfinance as yf
import os
import logging
import pandas as pd

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_petrobras_data():
    try:
        # Configurações para coleta de dados
        symbol = 'WEGE3.SA'
        start_date = '2025-05-01'
        end_date = '2025-05-27'

        # Coleta de dados
        logging.info(f"Baixando dados para {symbol} de {start_date} até {end_date}...")
        df = yf.download(symbol, start=start_date, end=end_date)

        if df.empty:
            logging.warning("Nenhum dado foi baixado para o símbolo fornecido.")
            return

        # Atualizar o caminho para salvar os dados na pasta 'data' dentro de 'downloadData'
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)
        csv_path = os.path.join(data_dir, f"{symbol}_data.csv")
        df.to_csv(csv_path)
        logging.info(f"Dados salvos em {csv_path}")

        # Processar o arquivo CSV para ajustar o cabeçalho
        df = pd.read_csv(csv_path, header=None)
        df = df.drop([1, 2])  # Remover as linhas 2 e 3
        df.columns = df.iloc[0]  # Definir a primeira linha como cabeçalho
        df = df[1:]  # Remover a linha antiga do cabeçalho
        df.rename(columns={df.columns[0]: 'Date'}, inplace=True)  # Substituir a célula A1 por 'Date'
        df.to_csv(csv_path, index=False)  # Salvar o arquivo processado
        logging.info(f"Arquivo CSV processado e atualizado em {csv_path}")

    except Exception as e:
        logging.error(f"Erro ao carregar os dados: {e}")

if __name__ == '__main__':
    download_petrobras_data()

