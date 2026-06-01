from app.infra.database.session import engine
from sqlalchemy import text

cid = 'c4d5c9ca-0ef1-4cb7-ad54-1ddc17490696'
with engine.connect() as conn:
    rows = conn.execute(text("SELECT id,status FROM service_orders WHERE customer_id = :cid"), {'cid': cid}).fetchall()
    print(rows)
