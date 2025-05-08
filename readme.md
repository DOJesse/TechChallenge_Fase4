# TechChallenge Fase 4

## Descrição
Esta aplicação é uma API web desenvolvida com **Flask** que utiliza um modelo **LSTM** treinado em **TensorFlow** para prever o fechamento de ações com base em dados históricos. A aplicação permite que o usuário faça upload de um arquivo CSV e obtenha uma previsão com base nesses dados.

## Estrutura do Projeto

```
TechChallenge_Fase4/
│
├── app/
│   ├── main.py                 # Código principal da aplicação Flask
│   ├── templates/
│   │   └── upload.html         # Interface para upload de arquivos
│
├── Docker/
│   ├── docker-compose.yml      # Configuração do Docker Compose
│   ├── Dockerfile              # Dockerfile da aplicação
│   └── requirements.txt        # Dependências da aplicação
│
├── modelTraining/
│   ├── model_lstm.keras        # Modelo LSTM treinado
│   └── modelTrainingLTSM.ipynb # Notebook com o treinamento do modelo
│
├── downloadData/
│   ├── downloadData.py         # Script para baixar dados históricos
│   └── data/
│       ├── PETR4.SA_data.csv   # Exemplo de dados históricos
│       └── VALE3.SA_data.csv   # Exemplo de dados históricos
```

## Funcionalidades

- **Previsão com LSTM**: Utiliza um modelo recorrente para prever o valor de fechamento de ações com base na coluna `Close`.
- **Upload de CSV via interface web**: Interface web simples para envio de arquivos com dados históricos.
- **Aplicação Dockerizada**: Totalmente containerizada, facilitando testes, deploy e reprodutibilidade.

## Como Executar

### Requisitos

- Docker e Docker Compose instalados

### Passos

1. **Clonar o Repositório**:
   ```bash
   git clone <url-do-repositorio>
   cd TechChallenge_Fase4
   ```

2. **Construir a Imagem Docker**:
   ```bash
   cd Docker
   docker-compose build --no-cache
   ```

3. **Iniciar o Container**:
   ```bash
   docker-compose up
   ```

4. **Acessar a Interface Web**:
   Acesse a aplicação em:  
   [http://localhost:5000](http://localhost:5000)

5. **Usar a Aplicação**:
   - Faça upload de um arquivo `.csv` com a coluna `Close`.
   - A API retorna um JSON com a previsão do fechamento do dia atual.

## Exemplo de Entrada e Saída

### Exemplo de CSV:

| Date       | Open  | High  | Low   | Close  | Volume |
|------------|-------|-------|-------|--------|--------|
| 2025-01-01 | 10.00 | 10.50 | 9.80  | 10.20  | 100000 |
| 2025-01-02 | 10.20 | 10.70 | 10.10 | 10.50  | 120000 |

### Exemplo de Resposta:

```json
{
  "today_close_prediction": 10.75
}
```

## Detalhes Técnicos

- **Modelo LSTM**: O modelo foi treinado com dados históricos e salvo no formato `.keras`. Ele está localizado em `modelTraining/model_lstm.keras`.
- **Renderização com Jinja2**: O Flask utiliza um template HTML (`upload.html`) localizado no diretório `app/templates/`.
- **Script de Coleta de Dados**: O script `downloadData.py` coleta dados da API do Yahoo Finance com a biblioteca `yfinance`.

## Dependências Principais

Listadas em `Docker/requirements.txt`:

- `Flask`
- `TensorFlow`
- `Pandas`
- `NumPy`
- `yfinance`