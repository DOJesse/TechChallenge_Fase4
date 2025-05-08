from flask import Flask, request, jsonify, render_template
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import os

app = Flask(__name__)

# Caminho ajustado para dentro do container Docker
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'model_lstm.keras')
model = load_model(MODEL_PATH)

@app.route('/')
def upload_file():
    print("Rendering upload.html")  # Adicionado para depuração
    return render_template('upload.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files or request.files['file'].filename == '':
            return jsonify({'error': 'Nenhum arquivo enviado ou selecionado'}), 400

        file = request.files['file']
        data = pd.read_csv(file)

        if 'Close' not in data.columns:
            return jsonify({'error': 'O arquivo CSV deve conter a coluna "Close"'}), 400

        historical_prices = data['Close'].values.reshape(-1, 1)
        input_data = np.array(historical_prices).reshape(1, -1, 1)

        predictions = model.predict(input_data)

        return jsonify({'today_close_prediction': predictions.flatten()[-1].item()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

