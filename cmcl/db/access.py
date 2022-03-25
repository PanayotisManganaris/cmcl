"""Much credit to Immentel's Mendeleev library"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

perovsdb = "perovskites.db"

def get_cmcl_perovs_path():
    """Return the Mannodi Group Perovskites database path"""
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), perovsdb)

def get_engine(dbpath=None):
    """Return the db engine -- chooses perovskites database by default"""
    if not dbpath:
        dbpath = get_cmcl_perovs_path()
    return create_engine(f"sqlite:///{str(dbpath)}", echo=True)

def get_session(dbpath=None):
    """
    Return the database session connection.
    optionally specify path to a database
    or name a project database shipping with cmcl
    defaults to Mannodi Group Perovskites.db
    """
    engine = get_engine(dbpath=dbpath)
    DB_Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return DB_Session() #assign instance on call
