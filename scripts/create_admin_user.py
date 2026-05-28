import os, sys
from dotenv import load_dotenv
load_dotenv()
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.infra.database.session import SessionLocal
from app.infra.repositories.user_repository import UserRepository
from app.shared.security import hash_password


def main():
    db = SessionLocal()
    try:
        repo = UserRepository(db)
        email = "admin@local.com"
        if repo.find_by_email(email):
            print('Admin user already exists:', email)
            return 0
        repo.create(
            email=email,
            password=hash_password('Admin@123'),
            full_name='Admin Test',
            role='admin'
        )
        db.commit()
        print('Admin user created:', email)
        return 0
    finally:
        db.close()

if __name__ == '__main__':
    raise SystemExit(main())
