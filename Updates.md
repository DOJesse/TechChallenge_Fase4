# Registro de Atualizações

## 19/03/2024 - 18:48:49
- Atualizado README.md com:
  - Nova estrutura de diretórios do projeto
  - Adicionado Poetry como pré-requisito
  - Atualizada porta da API de 5000 para 5001
  - Adicionadas instruções para execução local usando Poetry
  - Melhorada formatação dos blocos de código

## 19/03/2024 - 18:55:00
- Atualizados arquivos Docker:
  - Dockerfile:
    - Adicionado suporte ao Poetry
    - Atualizada porta de 5000 para 5001
    - Ajustado caminho do módulo principal para api.app:app
  - docker-compose.yml:
    - Atualizada porta de 5000 para 5001
    - Atualizado healthcheck para usar a nova porta

## 19/03/2024 - 19:00:00
- Removida pasta app/model:
  - Removido arquivo model_lstm.keras
  - Ajustada estrutura do projeto para usar apenas a pasta models 