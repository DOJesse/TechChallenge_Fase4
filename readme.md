# Tech Challenge Fase 4

## 📖 Descrição
Esta aplicação é uma **API RESTful** desenvolvida em Flask que utiliza um modelo **LSTM** para prever o fechamento de ações com base em dados históricos.  
O fluxo completo inclui:  
1. **Download** dos dados de mercado com `yfinance`.  
2. **Pré-processamento** e **treinamento** do modelo LSTM.  
3. **Deploy** da API para receber CSVs de histórico e retornar previsões.  
4. **Monitoramento** em produção via Prometheus & Grafana. 

---

## 📂 Estrutura do Projeto

```text
├── downloadData/
│   ├── data/
│   │   └── <SYMBOL>_data.csv        # Dados históricos baixados
│   └── downloadData.py              # Script de download de dados
│
├── modelTraining/
│   └── train_lstm.py                # Script de treino do modelo LSTM
│
├── app/
│   ├── api/
│   │   └── app.py                   # Código principal da API Flask
│   ├── models/
│   │   └── lstm_model.py            # Implementação do modelo LSTM
│   ├── services/
│   │   └── prediction_service.py    # Serviço de predição
│   ├── utils/
│   │   └── metrics.py               # Métricas Prometheus
│   ├── templates/
│   │   └── upload.html              # Formulário de upload CSV
│   ├── config.py                    # Configurações da aplicação
│   └── pyproject.toml               # Dependências e scripts (Poetry)
│
├── grafana/                         # Dashboards e provisioning do Grafana
│   ├── dashboards/
│   └── provisioning/
│
├── Docker/                          # Dockerfile e docker-compose
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
│
└── README.md                        # Este arquivo
```

---

## ⚙️ Pré-requisitos
- Docker & Docker Compose  
- Python 3.8+ (se for treinar localmente)  
- Poetry (gerenciamento de dependências) 

---

## 🚀 Passo a Passo

### 1. Baixar dados históricos
```bash
cd downloadData
python downloadData.py
```
Isso gera um CSV em `downloadData/data/<SYMBOL>_data.csv`. 

### 2. Treinar o modelo LSTM (opcional)
```bash
cd modelTraining
python train_lstm.py
```
O script consome o CSV, faz pré-processamento, cria sequências, treina e salva:
- `app/model/model_lstm.keras`  
- `app/model/scaler.pkl` 

### 3. Executar a aplicação localmente
```bash
cd app
poetry install
poetry run python -m api.app
```
- **API Flask** ➜ http://localhost:5001 

### 4. Subir toda a stack em containers
```bash
cd Docker
docker-compose up --build
```
- **API Flask** ➜ http://localhost:5001  
- **Prometheus** ➜ http://localhost:9090  
- **Grafana** ➜ http://localhost:3000 

---

## 📡 Uso da API

### 📁 Upload de CSV
1. Acesse http://localhost:5001/  
2. Envie um arquivo CSV com colunas `Date, Open, High, Low, Close, Volume`.  
3. O JSON de resposta conterá `predicted_close`. 

### 📈 Previsão B3 (10 maiores empresas)
1. **Via GET**  
   ```
   http://localhost:5001/predict_b3?company=<Empresa>
   ```
2. **Via POST** (JSON)
   ```json
   { "company": "Petrobras (PETR4)" }
   ```
3. Parâmetro `company` deve ser um dos nomes abaixo:
   - Petrobras (PETR4)  
   - Itaú Unibanco (ITUB4)  
   - Vale S.A. (VALE3)  
   - Ambev (ABEV3)  
   - BTG Pactual (BPAC11)  
   - Weg (WEGE3)  
   - Bradesco (BBDC4)  
   - Banco do Brasil (BBAS3)  
   - Itaúsa (ITSA4)  
   - Santander Brasil (SANB11)  
4. Exemplo GET:
   ```
   http://localhost:5001/predict_b3?company=Vale%20S.A.%20(VALE3)
   ```  
Resposta:
```json
{ "company": "Vale S.A. (VALE3)", "predicted_close": 105.23 }
```  
 Para mais detalhes de implementação, veja `app.py` 

---

## 📊 Monitoramento & Dashboards Grafana

Para acompanhar tempo de resposta, consumo de recursos e inferência:

### Infraestrutura do Processo Python
- **CPU (média 5m)**
  ```promql
  rate(process_cpu_seconds_total[5m])
  ```
- **Memória residente (RSS)**
  ```promql
  process_resident_memory_bytes
  ```
- **GC por minuto**
  ```promql
  rate(python_gc_objects_collected_total[1m])
  ``` 

### Métricas HTTP da API
- **Requisições (1m)**
  ```promql
  sum(rate(http_requests_total[1m])) by (method, status)
  ```
- **Latência 95º perc. (5m)**
  ```promql
  histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
  ``` 

### Métricas de Inferência do Modelo
- **Latência inferência 50º perc.**
  ```promql
  histogram_quantile(0.50, sum(rate(model_inference_duration_seconds_bucket[5m])) by (le))
  ```
- **Latência inferência 95º perc.**
  ```promql
  histogram_quantile(0.95, sum(rate(model_inference_duration_seconds_bucket[5m])) by (le))
  ```
- **Taxa de predições (1m)**
  ```promql
  sum(rate(model_predictions_total[1m]))
  ```
- **MAE últimas 1h**
  ```promql
  avg_over_time(model_prediction_error_absolute[1h])
  ``` 

---

## 📝 Dicas de Organização no Grafana
- Agrupe **CPU**, **Memória** e **GC** em “Health”.  
- Coloque **Requisições** e **Latência HTTP** em “API Performance”.  
- Separe **Inferência** em “Model Monitoring”.  
- Ajuste intervalos (e.g. 5m, 1h) conforme necessidade.