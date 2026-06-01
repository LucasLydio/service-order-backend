# Service Order Backend

---

## Índice

- [Descrição do Projeto](#descrição-do-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Arquitetura Escolhida](#arquitetura-escolhida)
- [Modelagem de Dados](#modelagem-de-dados)
- [Funcionalidades Implementadas](#funcionalidades-implementadas)
- [Endpoints da API](#endpoints-da-api)
- [Autenticação e Autorização](#autenticação-e-autorização)
- [Rate Limiting](#rate-limiting)
- [Regras de Negócio](#regras-de-negócio)
- [Testes Automatizados](#testes-automatizados)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Execução](#execução)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Coleção da API](#coleção-da-api)
- [Scripts Utilitários](#scripts-utilitários)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Equipe](#equipe)

---

## Descrição do Projeto

Backend RESTful para um sistema de **gerenciamento de ordens de serviço** em empresas de assistência técnica. O sistema permite o controle completo do ciclo de vida de uma ordem de serviço, desde a abertura pelo atendente até o encerramento pelo técnico, incluindo:

- Cadastro e autenticação de usuários com diferentes perfis de acesso
- Gerenciamento de clientes com integração ao ViaCEP para preenchimento automático de endereço
- Abertura, acompanhamento e encerramento de ordens de serviço com controle de prioridade
- Atribuição de técnicos às ordens de serviço
- Controle de peças e estoque com validação de disponibilidade
- Histórico de movimentações e eventos do sistema
- Relatórios gerenciais (tempo médio de atendimento, peças mais utilizadas, OS por técnico/status)

---

## Tecnologias Utilizadas

| Categoria | Tecnologia | Versão | Finalidade |
|-----------|-----------|--------|-----------| 
| **Linguagem** | Python | 3.10+ | Linguagem principal do backend |
| **Framework Web** | FastAPI | 0.104.1 | Framework assíncrono para APIs REST |
| **Servidor ASGI** | Uvicorn | 0.24.0 | Servidor de aplicação para rodar o FastAPI |
| **ORM** | SQLAlchemy | 2.0.23 | Mapeamento objeto-relacional (ORM) |
| **Migrações** | Alembic | 1.13.2 | Controle de versionamento do banco de dados |
| **Banco de Dados** | MySQL | 8.0+ | Sistema gerenciador de banco de dados relacional |
| **Driver MySQL** | PyMySQL | 1.1.0 | Conector Python para MySQL |
| **Validação** | Pydantic | 2.5.0 | Validação de dados e serialização de schemas |
| **Configuração** | Pydantic Settings | 2.1.0 | Gerenciamento de variáveis de ambiente |
| **Autenticação** | PyJWT | 2.8.0 | Geração e validação de tokens JWT |
| **Hashing** | Passlib | 1.7.4 | Hash de senhas com pbkdf2_sha256 |
| **Validação de E-mail** | email-validator | 2.1.1 | Validação de endereços de e-mail |
| **HTTP Client** | Requests | 2.31.0 | Consumo de APIs externas (ViaCEP) |
| **Upload** | python-multipart | 0.0.6 | Suporte a formulários multipart |
| **Testes** | Pytest | — | Framework de testes unitários |
| **Documentação** | Swagger UI / ReDoc | Integrado | Documentação interativa automática do FastAPI |

---

## Arquitetura Escolhida

O projeto adota uma **arquitetura em camadas (Layered Architecture)** com separação clara de responsabilidades, inspirada em princípios de **Clean Architecture**. Cada camada possui uma função específica e se comunica apenas com a camada adjacente:

```
┌─────────────────────────────────────────────────┐
│                   HTTP Layer                     │
│  (Routes → Middlewares → Controllers → Schemas)  │
├─────────────────────────────────────────────────┤
│                 Service Layer                    │
│         (Regras de negócio e orquestração)        │
├─────────────────────────────────────────────────┤
│               Repository Layer                   │
│           (Acesso e persistência de dados)        │
├─────────────────────────────────────────────────┤
│                 Model Layer                      │
│          (Entidades ORM / SQLAlchemy)             │
├─────────────────────────────────────────────────┤
│                    MySQL                         │
└─────────────────────────────────────────────────┘
```

### Descrição das Camadas

| Camada | Diretório | Responsabilidade |
|--------|-----------|-----------------| 
| **HTTP** | `app/http/` | Recebe as requisições HTTP, valida dados de entrada (schemas), aplica middlewares de autenticação/autorização e delega para os serviços |
| **Services** | `app/http/services/` | Contém a lógica de negócio: validações, integrações externas (ViaCEP), regras de domínio |
| **Repositories** | `app/infra/repositories/` | Abstrai o acesso ao banco de dados com operações CRUD usando SQLAlchemy |
| **Models** | `app/infra/models/` | Define as entidades do banco (tabelas) como classes ORM do SQLAlchemy |
| **Core** | `app/core/` | Configurações centrais da aplicação (variáveis de ambiente, settings) |
| **Shared** | `app/shared/` | Utilitários transversais: segurança (JWT, hash), exceções customizadas, envelope de resposta padrão |

### Fluxo de uma Requisição

```
Cliente HTTP (Postman/Frontend)
  │
  ▼
Routes (APIRouter) ─── define método + path
  │
  ▼
Middlewares ─── verify_token() → require_roles()
  │
  ▼
Controller ─── valida schema, instancia service
  │
  ▼
Service ─── aplica regras de negócio
  │
  ▼
Repository ─── executa query no banco
  │
  ▼
Model (SQLAlchemy) ─── mapeia para tabela MySQL
  │
  ▼
MySQL Database
```

### Padrão de Resposta

Todas as respostas da API seguem um **envelope padrão**:

```json
{
  "success": true,
  "message": "Operação realizada com sucesso",
  "data": { },
  "error": null
}
```

---

## Modelagem de Dados

### Diagrama Entidade-Relacionamento

```mermaid
erDiagram
    users ||--o{ password_recovery : "solicita"
    customers ||--o{ service_orders : "possui"
    technicians ||--o{ service_orders : "atende"
    service_orders ||--o{ order_parts : "utiliza"
    parts ||--o{ order_parts : "compõe"
    service_orders ||--o{ history : "registra"
    parts ||--o{ history : "registra"

    users {
        CHAR_36 id PK "UUID"
        VARCHAR_255 email UK
        VARCHAR_255 password
        VARCHAR_255 full_name
        VARCHAR_20 role "admin | manager | client"
        BOOLEAN is_active
        DATETIME created_at
        DATETIME updated_at
    }

    password_recovery {
        CHAR_36 id PK "UUID"
        CHAR_36 user_id FK
        VARCHAR_6 recovery_code UK
        INTEGER is_used "0 ou 1"
        DATETIME created_at
        DATETIME expires_at
    }

    customers {
        CHAR_36 id PK "UUID"
        VARCHAR_255 nome
        VARCHAR_20 cpf UK
        VARCHAR_20 telefone
        VARCHAR_255 email UK
        VARCHAR_255 endereco
        DATETIME created_at
        DATETIME updated_at
    }

    service_orders {
        CHAR_36 id PK "UUID"
        CHAR_36 customer_id FK
        CHAR_36 technician_id FK "nullable"
        VARCHAR_255 title
        TEXT description
        ENUM status "PENDING | IN_PROGRESS | COMPLETED | CANCELLED"
        ENUM priority "BAIXA | MEDIA | ALTA | URGENTE"
        DATETIME created_at
        DATETIME updated_at
    }

    technicians {
        CHAR_36 id PK "UUID"
        VARCHAR_255 full_name
        VARCHAR_255 email UK
        VARCHAR_20 phone
        VARCHAR_100 specialty
        BOOLEAN is_active
        DATETIME created_at
        DATETIME updated_at
    }

    parts {
        CHAR_36 id PK "UUID"
        VARCHAR_255 name
        VARCHAR_80 sku UK
        VARCHAR_500 description
        INTEGER quantity
        DECIMAL price "10 2"
        DATETIME created_at
        DATETIME updated_at
    }

    order_parts {
        CHAR_36 id PK "UUID"
        CHAR_36 service_order_id FK
        CHAR_36 part_id FK
        INTEGER quantity
        DATETIME created_at
    }

    history {
        CHAR_36 id PK "UUID"
        VARCHAR_50 event_type
        TEXT description
        CHAR_36 service_order_id FK "nullable"
        CHAR_36 part_id FK "nullable"
        DATETIME created_at
    }
```

### Entidades do Sistema

| Entidade | Tabela | Descrição | Status |
|----------|--------|-----------|--------|
| **User** | `users` | Usuários do sistema (admin, manager, client) | Implementado |
| **PasswordRecovery** | `password_recovery` | Códigos de recuperação de senha | Implementado |
| **Customer** | `customers` | Clientes da assistência técnica | Implementado |
| **ServiceOrder** | `service_orders` | Ordens de serviço com prioridade e técnico | Implementado |
| **Technician** | `technicians` | Técnicos responsáveis pelos atendimentos | Implementado |
| **Part** | `parts` | Peças e insumos do estoque | Implementado |
| **OrderPart** | `order_parts` | Relação N:N entre ordens de serviço e peças | Implementado |
| **History** | `history` | Registro de eventos e movimentações do sistema | Implementado |

---

## Funcionalidades Implementadas

### Por Integrante

| # | Responsabilidade | Status | Entregas |
|---|-----------------|--------|----------|
| 1 | **Documentação** | Concluido | README completo, Coleção Postman, Swagger automático |
| 2 | **Segurança e Rate Limiting** | Concluido | JWT, perfis (admin/manager/client), rate limiting por IP |
| 3 | **Banco de Dados e Infraestrutura** | Concluido | Repositório GitHub, 5 migrations (Alembic), seeds de dados |
| 4 | **Clientes e Integração Externa** | Concluido | CRUD de clientes, integração ViaCEP para endereço automático |
| 5 | **Ordens de Serviço** | Concluido | CRUD completo, controle de status/prioridade, atribuição de técnico, conclusão de OS |
| 6 | **Peças e Históricos** | Concluido | CRUD de peças, controle de estoque, uso de peças com baixa automática, histórico de eventos |
| 7 | **Relatórios e Testes** | Concluido | 4 relatórios gerenciais, 3 arquivos de testes unitários com regras de negócio validadas |

---

## Endpoints da API

### Autenticação — `/auth`

| Método | Rota | Descrição | Auth | Roles |
|--------|------|-----------|:----:|-------|
| `POST` | `/auth/register` | Registrar novo usuário | Nao | — |
| `POST` | `/auth/login` | Fazer login e obter token JWT | Nao | — |
| `POST` | `/auth/password-recovery/request` | Solicitar código de recuperação | Nao | — |
| `POST` | `/auth/password-recovery/confirm` | Confirmar código e redefinir senha | Nao | — |
| `GET` | `/auth/me` | Obter dados do usuário logado | Sim | Qualquer |

### Clientes — `/customers`

| Método | Rota | Descrição | Auth | Roles |
|--------|------|-----------|:----:|-------|
| `POST` | `/customers/` | Cadastrar novo cliente | Sim | admin, manager |
| `GET` | `/customers/` | Listar clientes (com filtros) | Sim | admin, manager |
| `GET` | `/customers/{id}` | Buscar cliente por ID | Sim | admin, manager |
| `PUT` | `/customers/{id}` | Atualizar dados do cliente | Sim | admin, manager |
| `DELETE` | `/customers/{id}` | Excluir cliente | Sim | admin |

> **Filtros disponíveis (query params):** `nome`, `cpf`, `email`, `telefone` — busca parcial com `LIKE`, lógica `OR`.

### Ordens de Serviço — `/service-orders`

| Método | Rota | Descrição | Auth | Roles |
|--------|------|-----------|:----:|-------|
| `POST` | `/service-orders/?customer_id={uuid}` | Abrir nova ordem de serviço | Sim | admin, manager |
| `GET` | `/service-orders/` | Listar todas as OS (com filtros) | Sim | admin, manager, client |
| `GET` | `/service-orders/{id}` | Consultar ordem por ID | Sim | admin, manager, client |
| `GET` | `/service-orders/customer/{customer_id}` | Listar OS de um cliente | Sim | admin, manager, client |
| `PUT` | `/service-orders/{id}` | Atualizar ordem de serviço | Sim | admin, manager |
| `PATCH` | `/service-orders/{id}/assign` | Atribuir técnico à OS | Sim | admin, manager |
| `PATCH` | `/service-orders/{id}/complete` | Marcar OS como concluída | Sim | admin, manager |
| `DELETE` | `/service-orders/{id}` | Excluir ordem de serviço | Sim | admin |

> **Filtros disponíveis (query params):** `status` (PENDING, IN_PROGRESS, COMPLETED, CANCELLED), `priority` (BAIXA, MEDIA, ALTA, URGENTE).

### Peças — `/parts`

| Método | Rota | Descrição | Auth | Roles |
|--------|------|-----------|:----:|-------|
| `POST` | `/parts/` | Cadastrar nova peça | Sim | admin, manager |
| `GET` | `/parts/` | Listar todas as peças | Sim | admin, manager, technician |
| `GET` | `/parts/{id}` | Buscar peça por ID | Sim | admin, manager, technician |
| `PUT` | `/parts/{id}` | Atualizar dados da peça | Sim | admin, manager |
| `DELETE` | `/parts/{id}` | Remover peça do sistema | Sim | admin |

### Relatórios — `/reports`

| Método | Rota | Descrição | Auth |
|--------|------|-----------|:----:|
| `GET` | `/reports/average-service-time` | Tempo médio de atendimento das OS concluídas | Nao |
| `GET` | `/reports/most-used-parts` | Ranking das peças mais utilizadas | Nao |
| `GET` | `/reports/orders-by-technician` | Quantidade de OS por técnico | Nao |
| `GET` | `/reports/orders-by-status` | Quantidade de OS por status | Nao |

### Utilitários

| Método | Rota | Descrição | Auth |
|--------|------|-----------|:----:|
| `GET` | `/` | Mensagem de boas-vindas da API | Nao |
| `GET` | `/health` | Health check do servidor | Nao |

---

## Autenticação e Autorização

### Mecanismo

O sistema utiliza **JWT (JSON Web Token)** para autenticação stateless:

1. O usuário faz login em `POST /auth/login` com e-mail e senha
2. O servidor retorna um `access_token` JWT assinado com HS256
3. O cliente inclui o token em todas as requisições protegidas via header:
   ```
   Authorization: Bearer <access_token>
   ```
4. O middleware `verify_token` decodifica o token e extrai os dados do usuário
5. O middleware `require_roles` verifica se o papel do usuário permite o acesso

### Payload do Token JWT

```json
{
  "sub": "uuid-do-usuario",
  "email": "usuario@email.com",
  "role": "admin",
  "exp": 1717027200
}
```

### Perfis de Acesso (RBAC)

| Perfil | Descrição | Permissões |
|--------|-----------|-----------| 
| `admin` | Administrador do sistema | Acesso total: CRUD completo de todos os recursos, incluindo exclusão |
| `manager` | Gerente / Atendente | Cadastro e edição de clientes, OS e peças (sem permissão de exclusão) |
| `client` | Cliente | Visualização limitada: pode consultar ordens de serviço |

### Fluxo de Recuperação de Senha

1. `POST /auth/password-recovery/request` — envia código de 6 dígitos (válido por 1 hora)
2. `POST /auth/password-recovery/confirm` — valida o código e redefine a senha

---

## Rate Limiting

O sistema possui um middleware de **rate limiting por IP** para proteção contra abuso:

- **Limite:** 10 requisições por minuto por endereço IP
- **Resposta ao exceder:** HTTP `429 Too Many Requests`
- **Mecanismo:** Sliding window em memória com rastreamento de timestamps por IP

---

## Regras de Negócio

### Ordens de Serviço

| Regra | Descrição | Exceção Lançada |
|-------|-----------|----------------|
| **OS concluída não pode ser editada** | Uma vez que o status é `COMPLETED`, nenhuma alteração é permitida (editar, deletar, atribuir técnico) | `CompletedOrderNotEditableException` (HTTP 400) |
| **Conclusão exige técnico** | Só é possível concluir uma OS (`COMPLETED`) se houver um técnico atribuído (`technician_id` não nulo) | `OrderWithoutTechnicianException` (HTTP 400) |
| **Atribuir técnico muda status** | Quando um técnico é atribuído via `PATCH /assign`, o status é automaticamente alterado para `IN_PROGRESS` | — |
| **Validação de status** | Somente valores válidos são aceitos: `PENDING`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED` | HTTP 400 |
| **Validação de prioridade** | Somente valores válidos são aceitos: `BAIXA`, `MEDIA`, `ALTA`, `URGENTE` | HTTP 400 |

### Peças e Estoque

| Regra | Descrição | Exceção Lançada |
|-------|-----------|----------------|
| **Estoque não pode ficar negativo** | Ao usar uma peça (`use_part`), a quantidade solicitada não pode exceder o estoque disponível | `InsufficientStockException` (HTTP 400) |
| **Quantidade não pode ser negativa** | Validação no schema: a quantidade da peça não aceita valores negativos | Erro de validação Pydantic (HTTP 422) |
| **Preço não pode ser negativo** | Validação no schema: o preço da peça não aceita valores negativos | Erro de validação Pydantic (HTTP 422) |
| **Histórico automático** | Toda operação de peça (criação, atualização, exclusão, uso) é registrada automaticamente na tabela `history` | — |

### Clientes

| Regra | Descrição | Exceção Lançada |
|-------|-----------|----------------|
| **Endereço obrigatório** | Na criação, deve ser fornecido o campo `endereco` ou o `cep` para busca automática via ViaCEP | HTTP 400 |
| **Integração ViaCEP** | Se um `cep` é fornecido, o sistema consulta a API ViaCEP e formata o endereço completo automaticamente | `CepNotFoundException` (HTTP 404) ou `ExternalIntegrationException` (HTTP 502) |

---

## Testes Automatizados

O projeto possui testes unitários na pasta `tests/`, utilizando **Pytest** com mocks para isolar a lógica de negócio do banco de dados.

### Arquivos de Teste

| Arquivo | Descrição | Testes |
|---------|-----------|--------|
| `tests/test_service_order.py` | Regras de negócio de Ordens de Serviço | 2 testes |
| `tests/test_reports.py` | Cálculo de relatórios gerenciais | 1 teste |
| `tests/test_stock.py` | Regras de estoque de peças | 1 teste |

### Detalhamento dos Testes

#### `test_service_order.py`

| Teste | O que valida |
|-------|-------------|
| `test_complete_order_without_technician` | Garante que não é possível concluir uma OS sem técnico atribuído (deve lançar `OrderWithoutTechnicianException`) |
| `test_completed_order_cannot_be_edited` | Garante que uma OS com status `COMPLETED` não pode ser editada (deve lançar `CompletedOrderNotEditableException`) |

#### `test_reports.py`

| Teste | O que valida |
|-------|-------------|
| `test_average_service_time_report_calculates_completed_orders` | Valida que o cálculo do tempo médio de atendimento retorna valores corretos (2 OS com 2h e 4h de duração devem resultar em média de 3h / 10800 segundos) |

#### `test_stock.py`

| Teste | O que valida |
|-------|-------------|
| `test_stock_cannot_be_negative_when_using_part` | Garante que ao tentar usar 3 unidades de uma peça com apenas 2 em estoque, o sistema lança `InsufficientStockException` e **não** atualiza o banco nem registra histórico |

### Como Executar os Testes

```bash
# Instalar pytest (se ainda não tiver)
pip install pytest

# Executar todos os testes
pytest tests/ -v

# Executar um arquivo específico
pytest tests/test_service_order.py -v

# Executar um teste específico
pytest tests/test_stock.py::test_stock_cannot_be_negative_when_using_part -v
```

---

## Pré-requisitos

Antes de iniciar, certifique-se de ter instalado:

- [Python](https://www.python.org/downloads/) 3.10 ou superior
- [MySQL](https://dev.mysql.com/downloads/) 8.0 ou superior
- [Git](https://git-scm.com/downloads)

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/LucasLydio/service-order-backend.git
cd service-order-backend
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com as suas configurações locais (veja a seção [Variáveis de Ambiente](#-variáveis-de-ambiente)).

### 5. Crie o banco de dados

Acesse o MySQL e execute:

```sql
CREATE DATABASE service_order CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Execute as migrações do banco

```bash
alembic upgrade head
```

### 7. (Opcional) Crie o usuário administrador

```bash
python scripts/create_admin.py
```

### 8. (Opcional) Popule com dados de demonstração

```bash
python scripts/bootstrap_database.py
```

Este script cria automaticamente:
- 4 usuários (admin, técnico, cliente, gerente)
- 3 técnicos
- 3 peças no estoque
- 5 clientes

---

## Execução

### Iniciar o servidor de desenvolvimento

```bash
uvicorn app.main:app --reload
```

### Acessar a aplicação

| Recurso | URL |
|---------|-----|
| **API Base** | http://localhost:8000 |
| **Swagger UI** (documentação interativa) | http://localhost:8000/docs |
| **ReDoc** (documentação alternativa) | http://localhost:8000/redoc |
| **Health Check** | http://localhost:8000/health |

### Iniciar em porta personalizada

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
```

---

## Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# ─── Banco de Dados ──────────────────────────────
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=service_order
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha_aqui

# Alternativa: URL completa (sobrescreve as variáveis acima)
# DATABASE_URL=mysql+pymysql://root:senha@localhost:3306/service_order

# ─── JWT ──────────────────────────────────────────
JWT_SECRET_KEY=sua-chave-secreta-aqui
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# ─── Ambiente ─────────────────────────────────────
ENVIRONMENT=development

# ─── Admin Inicial ────────────────────────────────
ADMIN_NAME=Admin
ADMIN_EMAIL=admin@email.com
ADMIN_PASSWORD=SenhaSegura123
```

---

## Coleção da API

A coleção completa da API para testes está disponível no arquivo:

**`docs/Service_Order_API.postman_collection.json`**

Para importar:
1. Abra o **Postman** (ou **Insomnia**)
2. Clique em **Import**
3. Selecione o arquivo `Service_Order_API.postman_collection.json`
4. A coleção será carregada com todos os endpoints, exemplos de request/response e o fluxo de autenticação configurado

> A documentação interativa também está disponível automaticamente em `/docs` (Swagger UI) ao executar o servidor.

---

## Scripts Utilitários

Localizados na pasta `scripts/`:

| Script | Comando | Descrição |
|--------|---------|-----------| 
| Bootstrap completo | `python scripts/bootstrap_database.py` | Executa migrações + popula dados de demonstração |
| Criar admin | `python scripts/create_admin.py` | Cria o admin a partir das variáveis de ambiente |
| Criar admin (dev) | `python scripts/create_admin_user.py` | Cria admin com credenciais fixas para desenvolvimento |
| Gerar token | `python scripts/generate_admin_token.py` | Gera um token JWT de admin para testes |
| Seed de clientes | `python scripts/seed_customers.py` | Insere 1 cliente de exemplo |
| Seed completa | `python scripts/seed_demo_data.py` | Popula usuários, técnicos, peças e clientes |
| Testes de API | `python scripts/api_test.py` | Testa login e CRUD de clientes |
| Testes estendidos | `python scripts/api_extended_tests.py` | Testa clientes e ordens de serviço |

---

## Estrutura de Pastas

```
service-order-backend/
│
├── app/                                 # Código-fonte da aplicação
│   ├── main.py                          # Ponto de entrada do FastAPI
│   │
│   ├── core/                            # Configurações centrais
│   │   └── config.py                    # Settings com Pydantic BaseSettings
│   │
│   ├── http/                            # Camada HTTP (Interface)
│   │   ├── controllers/                 # Controladores (orquestram request → service)
│   │   │   ├── auth_controller.py
│   │   │   ├── customer_controller.py
│   │   │   ├── part_controller.py       # CRUD de peças
│   │   │   ├── reports_controller.py    # Relatórios gerenciais
│   │   │   └── service_order_controller.py
│   │   ├── middlewares/                 # Middlewares de segurança
│   │   │   ├── auth_middleware.py       # Validação do token JWT
│   │   │   ├── role_middleware.py       # Controle de acesso por perfil
│   │   │   └── rate_limit_middleware.py # Limitação de requisições por IP
│   │   ├── routes/                      # Definição de rotas (APIRouter)
│   │   │   ├── auth_routes.py           # /auth
│   │   │   ├── customer_routes.py       # /customers
│   │   │   ├── part_routes.py           # /parts
│   │   │   ├── reports_routes.py        # /reports
│   │   │   └── service_order_routes.py  # /service-orders
│   │   ├── schemas/                     # Schemas Pydantic (validação I/O)
│   │   │   ├── auth_schema.py
│   │   │   ├── customer_schema.py
│   │   │   ├── part_schema.py
│   │   │   └── service_order_schema.py
│   │   └── services/                    # Serviços (regras de negócio)
│   │       ├── auth_service.py
│   │       ├── customer_service.py
│   │       ├── part_service.py
│   │       └── service_order_service.py
│   │
│   ├── infra/                           # Camada de Infraestrutura
│   │   ├── database/                    # Configuração do banco
│   │   │   ├── base.py                  # Base declarativa do SQLAlchemy
│   │   │   └── session.py              # Engine e SessionLocal
│   │   ├── models/                      # Modelos ORM
│   │   │   ├── user_model.py
│   │   │   ├── password_recovery_model.py
│   │   │   ├── customer_model.py
│   │   │   ├── service_order_model.py   # OS com status, prioridade e técnico
│   │   │   ├── technician_model.py
│   │   │   ├── part_model.py
│   │   │   ├── order_part_model.py      # Relação N:N entre OS e peças
│   │   │   └── history_model.py         # Registro de eventos do sistema
│   │   ├── repositories/               # Repositórios (acesso a dados)
│   │   │   ├── user_repository.py
│   │   │   ├── customer_repository.py
│   │   │   ├── service_order_repository.py
│   │   │   ├── password_recovery_repository.py
│   │   │   ├── part_repository.py
│   │   │   ├── history_repository.py
│   │   │   └── reports_repository.py    # Queries de relatórios gerenciais
│   │   └── migrations/                  # Migrações Alembic
│   │       ├── env.py
│   │       └── versions/
│   │           ├── 0001_bootstrap_tables.py
│   │           ├── 0002_backfill_customers_contacts.py
│   │           ├── 0003_create_technicians_and_parts.py
│   │           ├── 0004_create_order_parts_and_history.py
│   │           └── 0005_add_priority_technician_so.py
│   │
│   └── shared/                          # Utilitários compartilhados
│       ├── exceptions.py                # Exceções HTTP customizadas
│       ├── responses.py                 # Envelope padrão de resposta
│       └── security.py                  # JWT, hash de senhas
│
├── tests/                               # Testes automatizados (Pytest)
│   ├── test_service_order.py            # Testes de regras de negócio de OS
│   ├── test_reports.py                  # Testes de cálculo de relatórios
│   └── test_stock.py                    # Testes de controle de estoque
│
├── scripts/                             # Scripts utilitários
│   ├── bootstrap_database.py
│   ├── create_admin.py
│   ├── seed_demo_data.py
│   └── ...
│
├── docs/                                # Documentação
│   └── Service_Order_API.postman_collection.json
│
├── alembic.ini                          # Configuração do Alembic
├── requirements.txt                     # Dependências Python
├── .env.example                         # Exemplo de variáveis de ambiente
├── .gitignore                           # Arquivos ignorados pelo Git
└── README.md                            # Este arquivo
```

---

## Equipe

| # | Responsabilidade | Entregas Principais |
|---|-----------------|-------------------|
| 1 | Documentação | README completo, Coleção da API (Postman), Swagger |
| 2 | Segurança e Rate Limiting | Autenticação JWT, perfis de acesso (RBAC), rate limiting |
| 3 | Banco de Dados e Infraestrutura | Repositório GitHub, 5 migrations (Alembic), seeds |
| 4 | Clientes e Integração Externa | CRUD de clientes, integração ViaCEP |
| 5 | Ordens de Serviço | CRUD de OS, controle de status/prioridade, atribuição de técnico, conclusão |
| 6 | Peças e Históricos | CRUD de peças, controle de estoque, uso de peças, histórico de movimentações |
| 7 | Relatórios e Testes | 4 endpoints de relatórios, testes automatizados com Pytest |
