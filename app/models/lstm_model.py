from typing import Any, Tuple
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from config import MODEL_PATH, SEQUENCE_LENGTH

class LSTMModel:
    def __init__(self) -> None:
        """Inicializa o modelo LSTM."""
        self.model = load_model(MODEL_PATH)
        self.scaler = MinMaxScaler()
        self.close_index = 3  # Índice da coluna 'Close' nas features

    def preprocess_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, MinMaxScaler]:
        """Pré-processa os dados para inferência."""
        features = data[['Open', 'High', 'Low', 'Close', 'Volume']].values.astype(float)
        scaled = self.scaler.fit_transform(features)
        return scaled, self.scaler

    def prepare_sequence(self, scaled_data: np.ndarray) -> np.ndarray:
        """Prepara a sequência para inferência."""
        if len(scaled_data) < SEQUENCE_LENGTH:
            raise ValueError('Dados insuficientes para sequência')
        return np.expand_dims(scaled_data[-SEQUENCE_LENGTH:], axis=0)

    def predict(self, input_seq: np.ndarray) -> float:
        """Realiza a predição usando o modelo."""
        y_pred = self.model.predict(input_seq)
        return float(y_pred.flatten()[0])

    def denormalize_prediction(self, pred: float, scaler: MinMaxScaler) -> float:
        """Desnormaliza a predição usando os parâmetros do scaler."""
        min_c = scaler.data_min_[self.close_index]
        max_c = scaler.data_max_[self.close_index]
        return pred * (max_c - min_c) + min_c 