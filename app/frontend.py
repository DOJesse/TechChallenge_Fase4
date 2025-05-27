import streamlit as st
import requests
from prometheus_client import start_http_server, Counter, REGISTRY
import threading

# Inicia o contador de requisições ao Streamlit (Prometheus)
if 'streamlit_request_count' not in REGISTRY._names_to_collectors:
    REQUEST_COUNT = Counter('streamlit_request_count', 'Número de requisições ao Streamlit')

PROMETHEUS_SERVER_STARTED = threading.Event()
try:
    if not PROMETHEUS_SERVER_STARTED.is_set():
        start_http_server(8502)
        PROMETHEUS_SERVER_STARTED.set()
except OSError as e:
    st.error(f"Falha ao iniciar o servidor Prometheus: {e}")

if 'REQUEST_COUNT' in locals():
    REQUEST_COUNT.inc()

st.title("Previsão de Preços de Ações - LSTM")

API_URL = "http://localhost:5001"

# Controla a página atual na sessão
if "page" not in st.session_state:
    st.session_state.page = "upload"

def go_to_page(page):
    st.session_state.page = page

# === Página 1: Upload de CSV ===
if st.session_state.page == "upload":
    st.header("📁 Upload de Dados Históricos")
    uploaded_file = st.file_uploader("Escolha um arquivo .csv", type="csv")
    if uploaded_file is not None:
        st.success(f"Ação selecionada: {uploaded_file.name}")
        if st.button("Gerar Estimativa"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            response = requests.post(f"{API_URL}/predict", files=files)
            if response.status_code == 200:
                data = response.json()
                close = data.get("predicted_close", None)
                st.success(f"Fechamento previsto: R$ {close:.2f}")
            else:
                st.error(f"❌ Erro: {response.text}")

    if st.button("Selecionar Empresa da B3"):
        go_to_page("select_company")

# === Página 2: Seleção de Empresas da B3 ===
elif st.session_state.page == "select_company":
    st.header("📈 Seleção de Empresas da B3")

    companies = [
        "Petrobras (PETR4)",
        "Itaú Unibanco (ITUB4)",
        "Vale S.A. (VALE3)",
        "Ambev (ABEV3)",
        "BTG Pactual (BPAC11)",
        "Weg (WEGE3)",
        "Bradesco (BBDC4)",
        "Banco do Brasil (BBAS3)",
        "Itaúsa (ITSA4)",
        "Santander Brasil (SANB11)"
    ]

    selected = st.selectbox("Selecione uma empresa:", companies)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Obter Previsão"):
            response = requests.post(
                f"{API_URL}/predict_b3",
                json={"company": selected}
            )
            if response.status_code == 200:
                resultado = response.json()
                close = resultado.get("predicted_close", None)
                st.success(f"Previsão de fechamento para {selected}: R$ {close:.2f}")
            else:
                err = response.json().get("error", "Erro desconhecido")
                st.error(f"❌ {err}")
    with col2:
        if st.button("← Voltar"):
            go_to_page("upload")
