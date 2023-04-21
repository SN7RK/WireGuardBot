import os
import subprocess
import ipaddress
from db.models import engine, Users, Clients, Peer, Interface
from sqlalchemy.orm import Session
from utils.generate import generate_server
from dotenv import load_dotenv

load_dotenv()


def add_user(_tlg, _name):
    with Session(bind=engine) as session:
        new_user = Users(
            tlg=_tlg,
            name=_name
        )
        session.add(new_user)
        session.commit()


def add_client(_tlg, _name, _private, _address, _dns, _public, _shared, _endpoint, _ips):
    with Session(bind=engine) as session:
        new_client = Clients(
            tlg=_tlg,
            name=_name,
            private=_private,
            address=_address,
            dns=_dns,
            public=_public,
            shared=_shared,
            endpoint=_endpoint,
            ips=_ips
        )
        session.add(new_client)
        session.commit()


def add_peer(_tlg, _name, _public, _shared, _ips):
    with Session(bind=engine) as session:
        new_peer = Peer(
            tlg=_tlg,
            name=_name,
            public=_public,
            shared=_shared,
            ips=_ips
        )
        session.add(new_peer)
        session.commit()


def add_interface(_address, _port, _private, _post_up, _post_down):
    with Session(bind=engine) as session:
        new_interface = Interface(
            address=_address,
            port=_port,
            private=_private,
            post_up=_post_up,
            post_down=_post_down
        )
        session.add(new_interface)
        session.commit()


def create_client(tlg_id, tlg_name):
    def get_pub_key(private_key):
        cmd = f"/bin/echo '{private_key}' | wg pubkey"
        pub_key = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[
            0].decode('utf-8').rstrip()
        return pub_key

    def get_private_key():
        cmd = f"wg genkey"
        private_key = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[
            0].decode('utf-8').rstrip()
        return private_key

    def keys_pair():
        private_key = get_private_key()
        pub_key = get_pub_key(private_key)
        sha_key = get_private_key()
        return {'private_key': private_key, 'pub_key': pub_key, "shared": sha_key}

    with Session(bind=engine) as session:
        i = session.query(Interface).filter_by(id=1).first()

    with Session(bind=engine) as session:
        p = session.query(Peer).order_by(Peer.id.desc()).first()

    ips = p.ips.split(',')
    ipv4_interface = ipaddress.IPv4Interface(ips[0]) + 1
    ipv6_interface = ipaddress.IPv6Interface(ips[1]) + 1

    client_public = get_pub_key(private_key=i.private)
    keys = keys_pair()
    # all
    a_tlg = tlg_id
    a_name = tlg_name
    # client
    c_private = keys['private_key']
    c_address = f"{ipv4_interface},{ipv6_interface}"
    c_dns = i.address.split("/")[0]
    c_public = client_public
    c_shared = keys['shared']
    c_endpoint = f"{os.getenv('IP')}:{i.port}"
    c_ips = "0.0.0.0/0,::/0"
    # peer
    p_public = keys['pub_key']
    p_shared = c_shared
    p_ips = c_address

    add_client(a_tlg, a_name, c_private, c_address, c_dns, c_public, c_shared, c_endpoint, c_ips)
    add_peer(a_tlg, a_name, p_public, p_shared, p_ips)

    generate_server()
