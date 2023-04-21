from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from models import Clients, engine


uri = "sqlite:////home/den/deploy/WireGuardBot/db/wgdashboard.db"


def update_dash(shared_key, name, private_key):
    new_engine = create_engine(uri, echo=True)
    with Session(bind=new_engine) as session:
        wg = f"UPDATE wg0 SET private_key='{private_key}', name='{name}' WHERE preshared_key='{shared_key}';"
        print(wg)


with Session(bind=engine) as db:
    clients = db.query(Clients).all()
for c in clients:
    update_dash(c.shared, c.name, c.private)
