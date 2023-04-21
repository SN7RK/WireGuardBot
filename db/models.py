import os

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

db_file_path = os.getenv("DATABASE_FILE")
engine = create_engine(db_file_path, echo=False)
session = sessionmaker(bind=engine)
Base = declarative_base()


class Interface(Base):
    __tablename__ = 'Interface'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    address = sa.Column(sa.Text, nullable=False)
    port = sa.Column(sa.Integer, nullable=False)
    private = sa.Column(sa.Text, nullable=False)
    post_up = sa.Column(sa.Text, nullable=False)
    post_down = sa.Column(sa.Text, nullable=False)


class Peer(Base):
    __tablename__ = 'Peer'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    tlg = sa.Column(sa.Integer, nullable=False)
    name = sa.Column(sa.Text, nullable=False)
    public = sa.Column(sa.Text, nullable=False)
    shared = sa.Column(sa.Text, nullable=False)
    ips = sa.Column(sa.Text, nullable=False)


class Clients(Base):
    __tablename__ = 'Clients'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    tlg = sa.Column(sa.Integer, nullable=False)
    name = sa.Column(sa.Text, nullable=False)
    private = sa.Column(sa.Text, nullable=False)
    address = sa.Column(sa.Text, nullable=False)
    dns = sa.Column(sa.Text, nullable=False)
    public = sa.Column(sa.Text, nullable=False)
    shared = sa.Column(sa.Text, nullable=False)
    endpoint = sa.Column(sa.Text, nullable=False)
    ips = sa.Column(sa.Text, nullable=False)


class Users(Base):
    __tablename__ = "Users"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    tlg = sa.Column(sa.Integer, nullable=False, unique=True)
    name = sa.Column(sa.Text, nullable=False)


Base.metadata.create_all(engine)
