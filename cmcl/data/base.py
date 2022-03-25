import pandas as pd
import sqlite3
import os

from cmcl.db.access import get_session

# this whole thing probably needs to be tossed.  I'm still not sure
# how I'll give users an option to write their tables to a database

# clearly it should follow the spirit of sqlalchemy if that is what
# cmcl's own access is based on

# collab-scale database sharing is mostly figured out....

class UserDatabase():
    """
    creates and accesses user's own database. use storage accessor to
    read from it, write to it.

    cmcl's own database is kept in the package site under cmcl.data.db
    """
    def __init__():
        pass

class DataRetriever():
    """
    get tables from database
    """
    def __init__(self, filename: str, tblname: str):
        self._conn = sqlite3.connect(os.expanduser(filename))
        self._tbl = tblname

    def read(self):
        sql_string = f"""SELECT *
                         FROM {self._tbl}"""
        df = pd.read_sql(tblname,
                         self._conn, 
                         index_col='index')
        self._conn.close()

class DataStasher():
    """
    put table into database
    """
    def __init__(self, filename: str, tblname: str, df):
        self._conn = sqlite3.connect(os.expanduser(filename))
        self._tbl = tblname

    def read(self):
        df = pd.read_sql(self._tbl,
                         self._conn, 
                         if_exists='replace')
        self._conn.close()
