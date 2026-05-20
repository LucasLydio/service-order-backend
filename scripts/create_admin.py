import os
import sys

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.infra.database.session import SessionLocal  # noqa: E402
from app.infra.repositories.user_repository import UserRepository  # noqa: E402
from app.shared.security import hash_password  # noqa: E402


def main() -> int:
    admin_name = os.getenv("ADMIN_NAME", "Admin")
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        print("Missing ADMIN_EMAIL or ADMIN_PASSWORD in .env")
        return 1

    db = SessionLocal()
    try:
        repo = UserRepository(db)
        existing = repo.find_by_email(admin_email)
        if existing:
            print("Admin user already exists for the configured ADMIN_EMAIL")
            return 0

        repo.create(
            email=admin_email,
            password=hash_password(admin_password),
            full_name=admin_name,
            role="admin",
        )
        print("Admin user created successfully")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
