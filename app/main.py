from flask import Flask, request, jsonify, render_template
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import os
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)

# Caminho para o modelo treinado
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'model_lstm.keras')
model = load_model(MODEL_PATH)

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files or request.files['file'].filename == '':
            return jsonify({'error': 'Nenhum arquivo enviado ou selecionado'}), 400

        file = request.files['file']
        data = pd.read_csv(file)

        # Verificar se as colunas necessárias existem
        required_columns = ['Date', 'Close', 'Open', 'High', 'Low', 'Volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            return jsonify({'error': f'As colunas necessárias estão ausentes: {missing_columns}'}), 400

        # Converter coluna Date para datetime
        data['Date'] = pd.to_datetime(data['Date'])

        # Garantir que existam pelo menos 60 registros
        if len(data) < 60:
            return jsonify({'error': 'São necessários pelo menos 60 registros para realizar a previsão.'}), 400

        # Armazenar a data da última entrada (assumimos que ela é cronologicamente correta)
        last_date = data['Date'].iloc[-1]
        next_date = last_date + pd.Timedelta(days=1)

        # Selecionar apenas as features para o modelo
        feature_cols = ['Close', 'Open', 'High', 'Low', 'Volume']
        features = data[feature_cols]

        # Normalizar os dados
        scaler = MinMaxScaler()
        scaled_features = scaler.fit_transform(features)

        # Criar a sequência de entrada para o modelo (últimos 60 dias)
        sequence_length = 60
        input_sequence = scaled_features[-sequence_length:]
        input_sequence = np.expand_dims(input_sequence, axis=0)  # (1, 60, 5)

        # Prever
        prediction = model.predict(input_sequence)
        predicted_close_scaled = prediction.flatten()[0]  # apenas um valor

        # Preparar vetor para inverter a normalização corretamente
        padding = np.zeros((1, len(feature_cols)))  # cria vetor com 5 colunas
        padding[0, 0] = predicted_close_scaled  # insere valor previsto de 'Close' na posição correta

        inversed = scaler.inverse_transform(padding)
        predict_real = inversed[0, 0]  # extrai apenas o valor de 'Close'

        return jsonify({
            'predicted_close_scaled': float(predicted_close_scaled),
            'last_date': last_date.strftime('%Y-%m-%d'),
            'predicted_for_date': next_date.strftime('%Y-%m-%d'),
            'predict_real': float(predict_real)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
