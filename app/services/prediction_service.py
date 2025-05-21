from typing import Tuple, Dict, Any
import pandas as pd
import time
from models.lstm_model import LSTMModel
from utils.metrics import (
    MODEL_INFERENCE_LATENCY,
    MODEL_PREDICTION_COUNT,
    MODEL_PREDICTION_ERROR
)
from config import REQUIRED_COLUMNS

class PredictionService:
    def __init__(self) -> None:
        """Inicializa o serviço de predição."""
        self.model = LSTMModel()

    def validate_data(self, data: pd.DataFrame) -> Tuple[bool, str]:
        """Valida os dados de entrada."""
        missing = [c for c in REQUIRED_COLUMNS if c not in data.columns]
        if missing:
            return False, f'Colunas faltando: {missing}'
        return True, ''

    def process_prediction(self, data: pd.DataFrame) -> Tuple[Dict[str, Any], int]:
        """Processa a predição com métricas."""
        # Validação
        is_valid, error_msg = self.validate_data(data)
        if not is_valid:
            return {'error': error_msg}, 400

        try:
            # Pré-processamento
            data['Date'] = pd.to_datetime(data['Date'])
            data.sort_values('Date', inplace=True)
            scaled_data, scaler = self.model.preprocess_data(data)
            input_seq = self.model.prepare_sequence(scaled_data)

            # Inferência com métricas
            inf_start = time.time()
            pred = self.model.predict(input_seq)
            inference_time = time.time() - inf_start

            # Desnormalização
            pred_price = self.model.denormalize_prediction(pred, scaler)

            # Atualização de métricas
            MODEL_INFERENCE_LATENCY.labels(model='lstm').observe(inference_time)
            MODEL_PREDICTION_COUNT.labels(model='lstm').inc()
            true_last = data['Close'].iloc[-1]
            MODEL_PREDICTION_ERROR.labels(model='lstm').set(abs(pred_price - true_last))

            return {'predicted_close': pred_price}, 200

        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': f'Erro interno: {str(e)}'}, 500 