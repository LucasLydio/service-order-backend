from app.infra.database.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    rows = conn.execute(text("SELECT id, customer_id, status FROM service_orders")).fetchall()
    for r in rows:
        print(r)
