# TechChallenge Fase 4

## Descrição
Esta aplicação é uma API RESTful desenvolvida em Flask que utiliza um modelo LSTM para prever o fechamento de ações com base em dados históricos. A aplicação permite que os usuários façam upload de arquivos CSV contendo os dados históricos e obtenham previsões para o fechamento do dia atual.

## Estrutura do Projeto
A estrutura do projeto é organizada da seguinte forma:

```
app/
    application/
        main.py  # Código principal da aplicação Flask
    Docker/
        docker-compose.yml  # Configuração do Docker Compose
        Dockerfile  # Configuração do Docker
        requirements.txt  # Dependências da aplicação

modelTraining/
    model_lstm.keras  # Modelo LSTM treinado
    modelTrainingLTSM.ipynb  # Notebook para treinamento do modelo

downloadData/
    downloadData.py  # Script para download de dados históricos
    data/
        PETR4.SA_data.csv  # Dados históricos de exemplo
        VALE3.SA_data.csv  # Dados históricos de exemplo
```

## Funcionalidades
- **Previsão de Fechamento de Ações**: A API utiliza um modelo LSTM para prever o fechamento de ações com base em dados históricos fornecidos pelo usuário.
- **Upload de Arquivo CSV**: Os usuários podem fazer upload de arquivos CSV com a mesma formatação do arquivo `PETR4.SA_data.csv`.
- **Serviço Dockerizado**: A aplicação é totalmente containerizada usando Docker e Docker Compose.

## Como Executar

### Requisitos
- Python 3.9 ou superior
- Docker e Docker Compose instalados

### Passos para Execução

1. **Clonar o Repositório**:
   ```bash
   git clone <url-do-repositorio>
   cd TechChallenge_Fase4
   ```

2. **Construir o Container Docker**:
   ```bash
   cd app/Docker
   docker-compose build
   ```

3. **Iniciar o Serviço**:
   ```bash
   docker-compose up
   ```

4. **Acessar a Aplicação**:
   A aplicação estará disponível em `http://localhost:5000`.

5. **Fazer Upload de Arquivo CSV**:
   - Acesse a página inicial da aplicação.
   - Faça o upload de um arquivo CSV com a coluna `Close`.
   - Receba a previsão do fechamento da ação no dia atual.

## Exemplo de Uso

### Requisição
Envie um arquivo CSV com a seguinte estrutura:

| Date       | Open  | High  | Low   | Close  | Volume |
|------------|-------|-------|-------|--------|--------|
| 2025-01-01 | 10.00 | 10.50 | 9.80  | 10.20  | 100000 |
| 2025-01-02 | 10.20 | 10.70 | 10.10 | 10.50  | 120000 |

### Resposta
A API retornará um JSON com a previsão do fechamento:
```json
{
  "today_close_prediction": 10.75
}
```

## Desenvolvimento

### Treinamento do Modelo
O modelo LSTM foi treinado utilizando o arquivo `modelTraining/modelTrainingLTSM.ipynb`. O modelo é salvo no formato `.keras` e carregado pela aplicação Flask.

### Script de Download de Dados
O script `downloadData/downloadData.py` pode ser utilizado para baixar dados históricos de ações utilizando a biblioteca `yfinance`.

## Dependências
As dependências da aplicação estão listadas no arquivo `requirements.txt` e incluem:
- Flask
- TensorFlow
- Pandas
- NumPy
- yfinance

## Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests no repositório.

## Licença
Este projeto está licenciado sob a licença MIT.