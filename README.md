# Service Order Management System

A FastAPI backend for managing technical assistance service orders.

## Features

- User authentication with JWT
- Password recovery with email validation
- Customer management
- Service order management
- Rate limiting
- Clean layered architecture

## Prerequisites

- Python 3.10+
- MySQL 8.0+

## Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and update the MySQL credentials
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create the database
   - The project uses MySQL 8.0+ with the `mysql+pymysql://` SQLAlchemy URL format.
6. Run migrations:
   ```bash
   alembic revision --autogenerate -m "create initial tables"
   alembic upgrade head
   ```
   If you don't want to autogenerate a new revision, you can run `alembic upgrade head` using the existing migration(s).

   Note: this project uses UUIDs (stored as `CHAR(36)`) for primary/foreign keys. If you previously created tables with integer IDs, the simplest path is to recreate the database and run `alembic upgrade head` again.
7. Create an admin user:
   ```bash
   python scripts/create_admin.py
   ```
8. If you want to create the initial demo data in one step, run:
   ```bash
   python scripts/bootstrap_database.py
   ```
9. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## Project Structure

- `app/main.py` - FastAPI application entry point
- `app/core/config.py` - Configuration management
- `app/http/` - HTTP layer (controllers, routes, schemas, services)
- `app/infra/` - Infrastructure layer (database, models, repositories)
- `app/shared/` - Shared utilities (exceptions, responses, security)
- `tests/` - Test suite

## Roles (RBAC)

- `admin` -> full access
- `manager` -> customer and service order management except admin-only delete actions
- `client` -> limited authenticated access
