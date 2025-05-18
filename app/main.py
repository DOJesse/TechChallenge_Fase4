from flask import Flask, request, jsonify, render_template, Response, g
import numpy as np
import pandas as pd
import time
import os
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST, REGISTRY

app = Flask(__name__)

# Métricas HTTP
def start_timer():
    g.start_time = time.time()  # inicia medição de tempo

@app.before_request
def before_request():
    start_timer()

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'Latência das requisições HTTP',
    ['method', 'endpoint', 'http_status'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.3, 1.0, 3.0, 10.0]
)
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total de requisições HTTP',
    ['method', 'endpoint', 'http_status']
)

@app.after_request
def record_http_metrics(response):
    request_latency = time.time() - g.start_time
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.path,
        http_status=response.status_code
    ).observe(request_latency)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        http_status=response.status_code
    ).inc()
    return response

# Métricas de inferência do modelo
MODEL_INFERENCE_LATENCY = Histogram(
    'model_inference_duration_seconds',
    'Duração da inferência do modelo',
    ['model'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)
MODEL_PREDICTION_COUNT = Counter(
    'model_predictions_total',
    'Total de predições realizadas pelo modelo',
    ['model']
)
MODEL_PREDICTION_ERROR = Gauge(
    'model_prediction_error_absolute',
    'Erro absoluto da predição do modelo',
    ['model']
)

# Carrega o modelo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'model_lstm.keras')
model = load_model(MODEL_PATH)

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Validação de arquivo
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    data = pd.read_csv(request.files['file'])
    required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    missing = [c for c in required_cols if c not in data.columns]
    if missing:
        return jsonify({'error': f'Colunas faltando: {missing}'}), 400

    # Pré-processamento
    data['Date'] = pd.to_datetime(data['Date'])
    data.sort_values('Date', inplace=True)
    features = data[['Open', 'High', 'Low', 'Close', 'Volume']].values.astype(float)

    # Escala dinâmica dos dados de entrada
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(features)

    # Cria sequência para inferência (últimos 50 registros)
    seq_len = 50
    if len(scaled) < seq_len:
        return jsonify({'error': 'Dados insuficientes para sequência'}), 400
    input_seq = np.expand_dims(scaled[-seq_len:], axis=0)

    # Inferência com métricas
    inf_start = time.time()
    y_pred = model.predict(input_seq)
    inference_time = time.time() - inf_start

    # Desnormaliza predição usando os parâmetros do scaler local
    close_ix = 3
    min_c = scaler.data_min_[close_ix]
    max_c = scaler.data_max_[close_ix]
    pred_price = float(y_pred.flatten()[0] * (max_c - min_c) + min_c)

    # Atualiza métricas do modelo
    MODEL_INFERENCE_LATENCY.labels(model='lstm').observe(inference_time)
    MODEL_PREDICTION_COUNT.labels(model='lstm').inc()
    true_last = features[-1, close_ix]
    MODEL_PREDICTION_ERROR.labels(model='lstm').set(abs(pred_price - true_last))

    return jsonify({'predicted_close': pred_price}), 200

@app.route('/metrics')
def metrics():
    return Response(generate_latest(REGISTRY), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
