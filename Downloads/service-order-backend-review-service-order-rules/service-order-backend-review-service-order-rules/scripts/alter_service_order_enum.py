from app.infra.database.session import engine
from sqlalchemy import text

SQL = """
ALTER TABLE service_orders
MODIFY COLUMN status ENUM('PENDING','IN_PROGRESS','COMPLETED','CANCELLED') NULL DEFAULT 'PENDING';
"""


def main():
    with engine.begin() as conn:
        print("Altering service_orders.status column to uppercase enum and default PENDING...")
        conn.execute(text(SQL))
        print("Done.")


if __name__ == '__main__':
    main()
