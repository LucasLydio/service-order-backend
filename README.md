# Service Order Management System

Backend em FastAPI para gerenciar ordens de serviço (service orders).

## Principais recursos

- Autenticação JWT e recuperação de senha
- Controle de perfis (RBAC): `admin`, `manager`, `client`
- CRUD de clientes, peças e ordens de serviço
- Controle de estoque e uso de peças (baixa automática)
- Histórico de eventos (`history`) para operações importantes
- Regras de negócio: limite de 5 ordens em andamento por técnico, motivo de cancelamento obrigatório, não editar OS concluída
- Relatórios gerenciais básicos (`/reports`)
- Rate limiting por IP

## Endpoints principais

- `POST /auth/` — registro / login / recuperação de senha
- `GET/POST/PUT/DELETE /customers`
- `GET/POST/PUT/DELETE /parts`
- `GET/POST/PUT/DELETE /service-orders` + ações específicas:
  - `PATCH /service-orders/{id}/assign` — atribuir técnico (muda para `IN_PROGRESS`)
  - `PATCH /service-orders/{id}/complete` — marcar concluída
  - `PATCH /service-orders/{id}/cancel` — cancelar (motivo obrigatório)
  - `POST /service-orders/{id}/parts/{part_id}` — usar peça na OS (baixa de estoque)
- `GET /reports/*` — relatórios (tempo médio, peças mais usadas, OS por técnico, OS por status)

## Pré-requisitos

- Python 3.10+
- MySQL 8.0+

## Instalação e execução rápida

1. Clone o repositório
2. Copie `.env.example` para `.env` e ajuste credenciais
3. Crie e ative um ambiente virtual:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate
```

4. Instale dependências:

```bash
pip install -r requirements.txt
```

5. Crie o banco MySQL e rode as migrações:

```bash
# aplicar todas as migrações existentes
alembic upgrade head
```

Observação: foi adicionada uma migração adicional em `app/infra/migrations/versions/0006_add_service_order_timestamps_and_reason.py` que introduz campos de tempo de atendimento e motivo de cancelamento — certifique-se de aplicar as migrações no banco alvo.

6. (Opcional) Criar admin e popular dados de demonstração:

```bash
python scripts/create_admin.py
python scripts/bootstrap_database.py
```

7. Executar o servidor:

```bash
uvicorn app.main:app --reload
```

A documentação interativa estará em `http://localhost:8000/docs` (Swagger).

## Testes

Instale o pytest e execute a suíte:

```bash
pip install pytest
pytest tests/ -v
```

Na minha verificação local a suíte passou (6 tests).

## Arquitetura e organização

Estrutura em camadas (HTTP → Services → Repositories → Models). Principais pastas:

- `app/http/` — controllers, routes, schemas, services
- `app/infra/` — models, repositories, migrations
- `app/shared/` — exceções, respostas, segurança

## Observações finais

- A branch `review/service-order-rules` contém mudanças recentes relacionadas às regras de negócio (limite de ordens por técnico, histórico, campos adicionados à `service_orders`) e já foi enviada ao remote para revisão.
- Se for necessário alinhar o `README` com mais detalhes (ex.: exemplos de requests, coleção Postman em `docs/`), eu posso adicionar essas seções.

---

