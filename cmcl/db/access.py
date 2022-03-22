"""this file based heavily on Immentel's Mendeleev library"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

perovsdb = "perovskites.db"

def get_cmcl_perovs_path():
    """Return the Mannodi Group Perovskites database path"""
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), perovsdb)

def get_engine(dbpath=None):
    """Return the db engine -- could be made to take a switch for choosing datasets"""
    if not dbpath:
        dbpath = get_cmcl_perovs_path()
    return create_engine(f"sqlite:///{str(dbpath)}", echo=False)

def get_session(dbpath=None):
    """Return the database session connection."""
    engine = get_engine(dbpath=dbpath)
    db_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return db_session()
