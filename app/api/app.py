# app/api/app.py

from flask import Flask, request, jsonify, render_template, Response
import pandas as pd
from services.prediction_service import PredictionService
from utils.metrics import start_timer, record_http_metrics, get_metrics
from config import API_HOST, API_PORT, TEMPLATES_DIR
from prometheus_client import CONTENT_TYPE_LATEST
from datetime import datetime, timedelta
import yfinance as yf

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
    try:
        metrics_data, content_type = get_metrics()
        return Response(metrics_data, content_type=content_type)
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar métricas: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Endpoint para verificar o status de saúde do serviço."""
    return {"status": "healthy"}, 200

@app.route('/predict_b3', methods=['POST', 'GET'])
def predict_b3():
    """Endpoint para predição de preços das 10 maiores empresas da B3."""
    companies = {
        "Petrobras (PETR4)": "PETR4.SA",
        "Itaú Unibanco (ITUB4)": "ITUB4.SA",
        "Vale S.A. (VALE3)": "VALE3.SA",
        "Ambev (ABEV3)": "ABEV3.SA",
        "BTG Pactual (BPAC11)": "BPAC11.SA",
        "Weg (WEGE3)": "WEGE3.SA",
        "Bradesco (BBDC4)": "BBDC4.SA",
        "Banco do Brasil (BBAS3)": "BBAS3.SA",
        "Itaúsa (ITSA4)": "ITSA4.SA",
        "Santander Brasil (SANB11)": "SANB11.SA",
    }

    company_name = request.json.get("company") if request.method == 'POST' else request.args.get("company")
    if not company_name or company_name not in companies:
        return jsonify({"error": "Empresa inválida ou não especificada."}), 400

    ticker = companies[company_name]
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    try:
        # 1) Baixa e prepara o DataFrame
        data = yf.download(
            ticker,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d')
        )
        if data.empty:
            return jsonify({"error": "Não foi possível baixar os dados da empresa."}), 400

        data.reset_index(inplace=True)
        data.rename(columns={data.columns[0]: 'Date'}, inplace=True)
        data = data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]

        # 2) Chama o PredictionService diretamente, sem CSV intermediário
        result, status_code = prediction_service.process_prediction(data)
        if status_code == 200:
            return jsonify({
                "company": company_name,
                "predicted_close": result["predicted_close"]
            }), 200
        else:
            return jsonify({"error": result.get("error")}), status_code

    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

def run_app():
    """Inicia a aplicação Flask."""
    app.run(host=API_HOST, port=API_PORT)

if __name__ == '__main__':
    run_app()
