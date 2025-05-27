#!/bin/bash

# Adiciona o diretório raiz ao PYTHONPATH
export PYTHONPATH=$(pwd)

# Inicia a API Flask com Gunicorn em segundo plano
gunicorn --workers 4 --bind 0.0.0.0:5001 api.app:app &

# Inicia o Streamlit em primeiro plano
streamlit run frontend.py --server.port=8501 --server.address=0.0.0.0

