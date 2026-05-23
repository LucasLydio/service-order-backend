from app.infra.database.session import SessionLocal
from app.infra.repositories.customer_repository import CustomerRepository


def main():
    db = SessionLocal()
    repo = CustomerRepository(db)
    try:
        sample = {
            'id': 'c4d5c9ca-0ef1-4cb7-ad54-1ddc17490696',
            'nome': 'Cliente Teste',
            'cpf': '12345678901',
            'telefone': '11911112222',
            'email': 'cliente.teste@local.com',
            'endereco': 'Rua Teste, 123'
        }
        existing = repo.find_by_cpf(sample['cpf'])
        if existing:
            print('Customer already exists:', existing.id)
            return 0
        customer = repo.create(**sample)
        print('Created customer:', customer.id)
        return 0
    finally:
        db.close()


if __name__ == '__main__':
    raise SystemExit(main())
