from flask import Flask, request, jsonify, render_template, Response
import pandas as pd
from services.prediction_service import PredictionService
from utils.metrics import start_timer, record_http_metrics, get_metrics
from config import API_HOST, API_PORT, TEMPLATES_DIR

app = Flask(__name__, template_folder=str(TEMPLATES_DIR))
prediction_service = PredictionService()

@app.before_request
def before_request():
    """Inicializa o timer antes de cada requisição."""
    start_timer()

@app.after_request
def after_request(response: Response) -> Response:
    """Registra métricas após cada requisição."""
    return record_http_metrics(response)

@app.route('/')
def upload_file():
    """Renderiza a página de upload."""
    return render_template('upload.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint para predição de preços."""
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    try:
        data = pd.read_csv(request.files['file'])
        result, status_code = prediction_service.process_prediction(data)
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({'error': f'Erro ao processar arquivo: {str(e)}'}), 400

@app.route('/metrics')
def metrics():
    """Endpoint para métricas Prometheus."""
    return Response(*get_metrics())

def run_app():
    """Inicia a aplicação Flask."""
    app.run(host=API_HOST, port=API_PORT)

if __name__ == '__main__':
    run_app() 