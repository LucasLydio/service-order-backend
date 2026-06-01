import os
import sys

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.infra.database.session import SessionLocal  # noqa: E402
from app.infra.repositories.customer_repository import CustomerRepository  # noqa: E402
from app.infra.repositories.user_repository import UserRepository  # noqa: E402
from app.infra.models.technician_model import Technician  # noqa: E402
from app.infra.models.part_model import Part  # noqa: E402
from app.shared.security import hash_password  # noqa: E402


def seed_users(user_repo: UserRepository) -> None:
    demo_users = [
        {"email": "admin.demo@local", "password": "Admin@123", "full_name": "Admin Demo", "role": "admin"},
        {"email": "tech.demo@local", "password": "Tech@123", "full_name": "Tecnico Demo", "role": "technician"},
        {"email": "client.demo@local", "password": "Client@123", "full_name": "Cliente Demo", "role": "client"},
        {"email": "support.demo@local", "password": "Support@123", "full_name": "Suporte Demo", "role": "manager"},
    ]

    for user_data in demo_users:
        if user_repo.find_by_email(user_data["email"]):
            continue

        user_repo.create(
            email=user_data["email"],
            password=hash_password(user_data["password"]),
            full_name=user_data["full_name"],
            role=user_data["role"],
        )


def seed_technicians(db) -> None:
    demo_technicians = [
        {
            "full_name": "Carlos Silva",
            "email": "carlos.silva@example.com",
            "phone": "11988880001",
            "specialty": "Refrigeração",
        },
        {
            "full_name": "Fernanda Costa",
            "email": "fernanda.costa@example.com",
            "phone": "11988880002",
            "specialty": "Eletrônica",
        },
        {
            "full_name": "Joao Pedro",
            "email": "joao.pedro@example.com",
            "phone": "11988880003",
            "specialty": "Informática",
        },
    ]

    for technician_data in demo_technicians:
        exists = db.query(Technician).filter(Technician.email == technician_data["email"]).first()
        if exists:
            continue

        db.add(Technician(**technician_data))


def seed_parts(db) -> None:
    demo_parts = [
        {
            "name": "Placa Fonte Universal",
            "sku": "PART-001",
            "description": "Fonte de reposição para múltiplos modelos.",
            "quantity": 15,
            "price": 129.90,
        },
        {
            "name": "Sensor de Temperatura",
            "sku": "PART-002",
            "description": "Sensor para diagnóstico e troca rápida.",
            "quantity": 40,
            "price": 24.50,
        },
        {
            "name": "Kit Parafusos M3",
            "sku": "PART-003",
            "description": "Kit com itens de fixação para bancada.",
            "quantity": 100,
            "price": 9.90,
        },
    ]

    for part_data in demo_parts:
        exists = db.query(Part).filter(Part.sku == part_data["sku"]).first()
        if exists:
            continue

        db.add(Part(**part_data))


def seed_customers(customer_repo: CustomerRepository) -> None:
    demo_customers = [
        {
            "nome": "Carlos da Fonseca Fagundes",
            "cpf": "12345678901",
            "telefone": "11990000001",
            "email": "carlos.fagundes@example.com",
            "endereco": "Rua das Laranjeiras, 120 - Centro",
        },
        {
            "nome": "Marina Almeida Rocha",
            "cpf": "12345678902",
            "telefone": "11990000002",
            "email": "marina.rocha@example.com",
            "endereco": "Avenida Brasil, 455 - Jardim América",
        },
        {
            "nome": "Joao Pedro Nascimento",
            "cpf": "12345678903",
            "telefone": "11990000003",
            "email": "joao.nascimento@example.com",
            "endereco": "Rua do Comércio, 78 - Vila Nova",
        },
        {
            "nome": "Fernanda Costa Lima",
            "cpf": "12345678904",
            "telefone": "11990000004",
            "email": "fernanda.lima@example.com",
            "endereco": "Travessa Belo Horizonte, 21 - Santa Clara",
        },
        {
            "nome": "Rafael Monteiro Souza",
            "cpf": "12345678905",
            "telefone": "11990000005",
            "email": "rafael.souza@example.com",
            "endereco": "Rua Aurora, 900 - Industrial",
        },
    ]

    for customer_data in demo_customers:
        if customer_repo.find_by_cpf(customer_data["cpf"]):
            continue
        customer_repo.create(**customer_data)


def main() -> int:
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        customer_repo = CustomerRepository(db)

        seed_users(user_repo)
        seed_technicians(db)
        seed_parts(db)
        seed_customers(customer_repo)

        db.commit()

        print("Demo data created successfully")
        print("Users: admin, technician, client, manager")
        print("Technicians: 3 sample records")
        print("Parts: 3 sample records")
        print("Customers: 5 sample records")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())