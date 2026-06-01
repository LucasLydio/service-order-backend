from sqlalchemy import text
from app.infra.database.session import engine


def main():
    with engine.begin() as conn:
        print("Updating service_orders.status to UPPERCASE where needed...")
        conn.execute(text("UPDATE service_orders SET status = UPPER(status) WHERE status <> UPPER(status)"))
        print("Done.")


if __name__ == "__main__":
    main()
