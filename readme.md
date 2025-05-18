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
│   ├── main.py                      # Código principal da API Flask
│   ├── upload.html                  # Formulário de upload CSV
│   └── model/
│       └── model_lstm.keras         # Modelo treinado
│
├── grafana/                         # Dashboards e provisioning do Grafana
│   ├── dashboards/
│   └── provisioning/
│
├── Docker/                          # Dockerfile da API Flask
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
│
└── README.md                        # Este arquivo

---

## ⚙️ Pré-requisitos
- Docker & Docker Compose  
- Python 3.8+ (se for treinar localmente)

---

## 🚀 Passo a Passo

### 1. Baixar dados históricos
\`\`\`bash
cd downloadData
python downloadData.py
\`\`\`
Isso gera um CSV em \`downloadData/data/<SYMBOL>_data.csv\`.

### 2. Treinar o modelo LSTM (opcional)
\`\`\`bash
cd modelTraining
python train_lstm.py
\`\`\`
O script consome o CSV, faz pré-processamento, cria sequências, treina e salva:
- \`app/model/model_lstm.keras\`  
- \`app/model/scaler.pkl\`

### 3. Subir toda a stack em containers
\`\`\`bash
cd Docker
docker-compose up --build
\`\`\`
- **API Flask** ➜ http://localhost:5000  
- **Prometheus** ➜ http://localhost:9090  
- **Grafana** ➜ http://localhost:3000  

---

## 📡 Uso da API

1. Acesse a página de upload:  
   http://localhost:5000/  
2. Envie um arquivo CSV com colunas \`Date, Open, High, Low, Close, Volume\`.  
3. Receba o JSON com a previsão do preço de fechamento.

---

## 📊 Monitoramento & Dashboards Grafana

Para rastrear em produção o **tempo de resposta** e a **utilização de recursos**, crie estes painéis no Grafana:

### 1. Infraestrutura do Processo Python
- **CPU do processo (média 5m)**
  \`\`\`promql
  rate(process_cpu_seconds_total[5m])
  \`\`\`

   *Mostra a taxa de uso de CPU do processo Python, permitindo identificar picos de consumo.*

- **Memória residente (RSS)**
  \`\`\`promql
  process_resident_memory_bytes
  \`\`\`

  *Exibe em bytes a memória RAM ocupada pelo processo, útil para detectar vazamentos.*

- **Coletas de Garbage Collector (GC) por minuto**
  \`\`\`promql
  rate(python_gc_objects_collected_total[1m])
  \`\`\`

  *Indica quantos objetos o Garbage Collector liberou por minuto, mostrando carga de coleta.*

### 2. Métricas HTTP da API
- **Taxa de requisições (1m)**
  \`\`\`promql
  sum(rate(http_requests_total[1m])) by (method, status)
  \`\`\`

  *Quantidade de chamadas HTTP por segundo, agrupadas por método e código de status.*

- **Latência HTTP – 95º percentil (5m)**
  \`\`\`promql
  histogram_quantile(
    0.95,
    sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
  )
  \`\`\`

  *Tempo de resposta no percentil 95, útil para identificar casos de alta latência.*

### 3. Métricas de Inferência do Modelo
- **Latência de inferência – mediana (50º)**
  \`\`\`promql
  histogram_quantile(
    0.50,
    sum(rate(model_inference_duration_seconds_bucket[5m])) by (le)
  )
  \`\`\`

  *Mostra o tempo de inferência do modelo no median, indicando desempenho geral e piores casos.*

- **Latência de inferência – 95º percentil (5m)**
  \`\`\`promql
  histogram_quantile(
    0.95,
    sum(rate(model_inference_duration_seconds_bucket[5m])) by (le)
  )
  \`\`\`

  *Mostra o tempo de inferência do modelo no 95º percentil, indicando desempenho geral e piores casos.*

- **Taxa de predições (1m)**
  \`\`\`promql
  sum(rate(model_predictions_total[1m]))
  \`\`\`

  *Número de previsões do modelo por segundo, para medir throughput.*

- **Erro absoluto médio (MAE) nas últimas 1h**
  \`\`\`promql
  avg_over_time(model_prediction_error_absolute[1h])
  \`\`\`

  *Média do erro absoluto das previsões na última hora, avaliando acurácia em produção.*

---

## 📝 Dicas de Organização no Grafana
- Agrupe **CPU**, **memória** e **GC** em um painel “Health”.  
- Coloque **taxa** e **latência HTTP** em “API Performance”.  
- Separe as **métricas de inferência** em “Model Monitoring”.  
- Ajuste o intervalo de avaliação (e.g. 5m, 1h) conforme a granularidade desejada.

---
