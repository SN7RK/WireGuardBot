import os
from typing import Type, Any

from sqlalchemy.orm import Session
from db.models import engine, Clients, Peer, Interface, Users
import subprocess
from dotenv import load_dotenv

load_dotenv()

ADMIN_IDS = [int(id_) for id_ in os.getenv("ADMIN_IDS").split(",")]


def generate_server():
    try:
        with Session(bind=engine) as session:
            i = session.query(Interface).filter_by(id=1).first()
            text = f"[Interface]\n" \
                   f"Address = {i.address}\n" \
                   f"ListenPort = {i.port}\n" \
                   f"PrivateKey = {i.private}\n" \
                   f"PostUp = {i.post_up}\n" \
                   f"PostDown = {i.post_down}\n\n"

        with Session(bind=engine) as session:
            peers = session.query(Peer).all()
            for p in peers:
                text += f"### Client {p.name} - {p.tlg}\n" \
                        f"[Peer]\n" \
                        f"PublicKey = {p.public}\n" \
                        f"PresharedKey = {p.shared}\n" \
                        f"AllowedIPs = {p.ips}\n\n"

            filename = os.path.join(os.getenv("SERVER_CONF_DIR"), f"wg0.conf")
            with open(filename, "w") as file:
                file.write(text)

            # restart_system()
    except Exception as e:
        print(f"An error occurred while generating server configuration: {e}")


def generate_client(tlg, name):
    try:
        with Session(bind=engine) as db:
            clients = db.query(Clients).filter_by(tlg=tlg, name=name).all()
            for c in clients:
                text = f"[Interface]\n" \
                       f"PrivateKey = {c.private}\n" \
                       f"Address = {c.address}\n" \
                       f"DNS = {c.dns}\n" \
                       f"\n" \
                       f"[Peer]\n" \
                       f"PublicKey = {c.public}\n" \
                       f"PresharedKey = {c.shared}\n" \
                       f"Endpoint = {c.endpoint}\n" \
                       f"AllowedIPs = {c.ips}\n"
        return text
    except Exception as e:
        print(f"An error occurred while generating client configuration: {e}")
        return ""


def restart_system():
    try:
        wg_quick_restart = subprocess.run(['systemctl', 'restart', 'wg-quick@wg0.service'], capture_output=True)
        unbound_restart = subprocess.run(['systemctl', 'restart', 'unbound.service'], capture_output=True)
        wg_dashboard_restart = subprocess.run(['systemctl', 'restart', 'wg-dashboard.service'], capture_output=True)

        if wg_quick_restart.returncode != 0:
            print(f"An error occurred while restarting wg-quick@wg0.service: {wg_quick_restart.stderr.decode('utf-8')}")
        if unbound_restart.returncode != 0:
            print(f"An error occurred while restarting unbound.service: {unbound_restart.stderr.decode('utf-8')}")
        if wg_dashboard_restart.returncode != 0:
            print(f"An error occurred while restarting wg-dashboard.service: "
                  f"{wg_dashboard_restart.stderr.decode('utf-8')}")

    except Exception as e:
        print(f"An error occurred while restarting system services: {e}")


def check_client_profile(tlg_id: int, client_name: str) -> bool:
    try:
        with Session(bind=engine) as db:
            clients = db.query(Clients).filter_by(tlg=tlg_id, name=client_name).all()
            return len(clients) >= 1
    except Exception as e:
        print(f"An error occurred while checking client profile: {e}")
        return False


def get_clients_profile_by_id(tlg_id: int) -> list[Type[Clients]] | list[Any]:
    try:
        with Session(bind=engine) as db:
            return db.query(Clients).filter_by(tlg=tlg_id).all()
    except Exception as e:
        print(f"An error occurred while getting client profile by ID: {e}")
        return []


def get_client_profile_by_name(client_name: str) -> Type[Clients] | None:
    try:
        with Session(bind=engine) as db:
            return db.query(Clients).filter_by(name=client_name).first()
    except Exception as e:
        print(f"An error occurred while getting client profile by name: {e}")
        return None


def get_user_by_id(tlg_id: int) -> Type[Users] | None:
    try:
        with Session(bind=engine) as db:
            return db.query(Users).filter_by(tlg=tlg_id).first()
    except Exception as e:
        print(f"An error occurred while getting user by ID: {e}")
        return None


def is_admin(tlg_id: int) -> bool:
    return tlg_id in ADMIN_IDS


def admin_list():
    return os.getenv("ADMIN_IDS").split(",")
