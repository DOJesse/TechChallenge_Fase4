import yfinance as yf
import pandas as pd
import psycopg2
from flask import Flask, jsonify
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Configurações do banco de dados
DB_HOST = 'db'
DB_NAME = 'finance_db'
DB_USER = 'postgres'
DB_PASSWORD = 'password'

# Conexão com o banco de dados
try:
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()
    print("Conexão com o banco de dados estabelecida com sucesso.")

except Exception as e:
    print(f"Erro ao conectar ou inserir dados no banco de dados: {e}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
        print("Conexão com o banco de dados encerrada.")

@app.route('/load-data', methods=['POST'])
def load_data():
    try:
        # Configurações para coleta de dados
        symbol = 'PETR4.SA'
        start_date = '2000-01-01'
        end_date = '2024-07-20'

        # Coleta de dados
        logging.info(f"Baixando dados para {symbol} de {start_date} até {end_date}...")
        df = yf.download(symbol, start=start_date, end=end_date)

        if df.empty:
            logging.warning("Nenhum dado foi baixado para o símbolo fornecido.")
            return jsonify({"error": "Nenhum dado foi baixado."}), 400

        # Verificar as colunas disponíveis no DataFrame
        logging.info(f"Colunas disponíveis no DataFrame: {df.columns.tolist()}")

        # Garantir que a coluna 'Adj Close' está presente
        if 'Adj Close' not in df.columns:
            logging.warning("A coluna 'Adj Close' não está presente nos dados retornados. Usando 'Close' como substituto.")
            df['Adj Close'] = df['Close']

        # Conexão com o banco de dados
        conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cursor = conn.cursor()
        logging.info("Conexão com o banco de dados estabelecida com sucesso.")

        # Inserir dados no banco
        for index, row in df.iterrows():
            cursor.execute('''
                INSERT INTO stock_data (date, open, high, low, close, adj_close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (date) DO NOTHING;
            ''', (
                index.to_pydatetime(),  # Converter o índice (data) para datetime
                None if pd.isna(row['Open']) else row['Open'],
                None if pd.isna(row['High']) else row['High'],
                None if pd.isna(row['Low']) else row['Low'],
                None if pd.isna(row['Close']) else row['Close'],
                None if pd.isna(row['Adj Close']) else row['Adj Close'],
                None if pd.isna(row['Volume']) else int(row['Volume'])
            ))
        conn.commit()
        logging.info("Dados inseridos no banco de dados com sucesso.")

        return jsonify({"message": "Dados carregados com sucesso."}), 200

    except Exception as e:
        logging.error(f"Erro ao carregar os dados: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            logging.info("Conexão com o banco de dados encerrada.")

@app.route('/get-data', methods=['GET'])
def get_data():
    try:
        # Conexão com o banco de dados
        conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cursor = conn.cursor()

        # Consultar as 10 primeiras linhas da tabela tbl_stock_data
        cursor.execute('SELECT * FROM stock_data LIMIT 10;')
        rows = cursor.fetchall()

        # Formatar os dados como uma lista de dicionários
        columns = [desc[0] for desc in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]

        return jsonify(data), 200

    except Exception as e:
        logging.error(f"Erro ao consultar os dados: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)