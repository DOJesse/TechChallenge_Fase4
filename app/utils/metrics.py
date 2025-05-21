from typing import Any
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from flask import g, request, Response
import time
from config import METRICS_BUCKETS, MODEL_METRICS_BUCKETS

# Métricas HTTP
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'Latência das requisições HTTP',
    ['method', 'endpoint', 'http_status'],
    buckets=METRICS_BUCKETS
)

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total de requisições HTTP',
    ['method', 'endpoint', 'http_status']
)

# Métricas de inferência do modelo
MODEL_INFERENCE_LATENCY = Histogram(
    'model_inference_duration_seconds',
    'Duração da inferência do modelo',
    ['model'],
    buckets=MODEL_METRICS_BUCKETS
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

def start_timer() -> None:
    """Inicia o timer para medição de latência."""
    g.start_time = time.time()

def record_http_metrics(response: Response) -> Response:
    """Registra métricas HTTP após cada requisição."""
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

def get_metrics() -> tuple[bytes, str]:
    """Retorna as métricas no formato Prometheus."""
    return generate_latest(REGISTRY), CONTENT_TYPE_LATEST 