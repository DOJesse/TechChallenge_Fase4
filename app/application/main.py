from flask import Flask, request, jsonify, render_template
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import os

app = Flask(__name__)

# Carregar o modelo LSTM treinado
MODEL_PATH = '../../modelTraining/model_lstm.keras'
model = load_model(MODEL_PATH)

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Verifica se o arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

        # Lê o arquivo CSV enviado
        data = pd.read_csv(file)

        # Verifica se o arquivo contém a coluna necessária
        if 'Close' not in data.columns:
            return jsonify({'error': 'O arquivo CSV deve conter a coluna "Close"'}), 400

        # Prepara os dados para o modelo
        historical_prices = data['Close'].values.reshape(-1, 1)
        input_data = np.array(historical_prices).reshape(1, -1, 1)

        # Faz a previsão
        predictions = model.predict(input_data)

        # Retorna a previsão do fechamento da ação no dia atual
        return jsonify({'today_close_prediction': predictions.flatten()[-1].item()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)