import os, sys
from dotenv import load_dotenv
load_dotenv()
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.infra.database.session import SessionLocal
from app.infra.repositories.user_repository import UserRepository
from app.shared.security import create_access_token


def main():
    db = SessionLocal()
    try:
        repo = UserRepository(db)
        user = repo.find_by_email('admin@local.com')
        if not user:
            print('')
            return 1
        token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
        print(token)
        return 0
    finally:
        db.close()

if __name__ == '__main__':
    raise SystemExit(main())
