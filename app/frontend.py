import streamlit as st
import requests
from prometheus_client import start_http_server, Counter, REGISTRY
import threading

# Métrica de requisições ao Streamlit
if "streamlit_request_count" not in REGISTRY._names_to_collectors:
    REQUEST_COUNT = Counter("streamlit_request_count", "Número de requisições ao Streamlit")

# Conta requisições
if "REQUEST_COUNT" in locals():
    REQUEST_COUNT.inc()

st.title("Previsão de Preços de Ações - LSTM")

API_URL = "http://localhost:5001"

# Inicializa página padrão
if "page" not in st.session_state:
    st.session_state.page = "upload"

def go_to_page(page):
    st.session_state.page = page

# === Página de upload ===
if st.session_state.page == "upload":
    st.title("📁 Upload de Dados Históricos")

    uploaded_file = st.file_uploader(
        "Escolha um arquivo .csv",
        type="csv",
        accept_multiple_files=False
    )

    if uploaded_file is not None:
        st.success(f"Ação selecionada: {uploaded_file.name}")

        if st.button("Gerar Estimativa"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            response = requests.post(f"{API_URL}/predict", files=files)
            if response.status_code == 200:
                data = response.json()
                predicted_close = data.get("predicted_close", None)
                st.info(f"Fechamento previsto: R${predicted_close:.2f}")
            else:
                st.error(f"❌ Erro ao enviar: {response.text}")

    # Navegação para seleção de empresas com um clique
    st.button(
        "Selecionar Empresa da B3",
        on_click=go_to_page,
        args=("select_company",)
    )

# === Página de seleção de empresas da B3 ===
if st.session_state.page == "select_company":
    st.title("📈 Seleção de Empresas da B3")

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

    selected_company = st.selectbox("Selecione uma empresa:", companies)

    if st.button("Obter Previsão"):
        response = requests.post(
            f"{API_URL}/predict_b3",
            json={"company": selected_company}
        )
        if response.status_code == 200:
            data = response.json()
            predicted_close = data.get("predicted_close", None)
            st.success(f"Previsão de fechamento para {selected_company}: R${predicted_close:.2f}")
        else:
            st.error(f"Erro: {response.json().get('error', 'Erro desconhecido')}")

    # Botão Voltar com um clique
    st.button(
        "Voltar",
        on_click=go_to_page,
        args=("upload",)
    )
