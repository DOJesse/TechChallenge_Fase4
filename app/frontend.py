import streamlit as st
import requests

st.title("Previsão de Preços de Ações - LSTM")

API_URL = "http://localhost:5001"

# Navegação simples com sessão
if "page" not in st.session_state:
    st.session_state.page = "upload"

def go_to_page(page):
    st.session_state.page = page

# Página de upload
if st.session_state.page == "upload":
    st.title("📁 Upload de Dados Históricos")

    uploaded_file = st.file_uploader("Escolha um arquivo .csv", 
                                     type="csv",
                                     accept_multiple_files=False)

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
