import pandas as pd
import sqlite3
import os

class DataRetriever():
    """
    provide tables from database

    ideally could also be used to fill gaps in CmclFrame
    automatically
    """
    def __init__(self, filename: str, tblname: str):
        self._conn = sqlite3.connect(os.expanduser(filename))
        self._tbl = tblname

    def read(self):
        sql_string = f"""SELECT *
                         FROM {self._tbl}"""
        df = pd.read_sql((tblname,
                          self._conn, 
                          index_col='index')
        self._conn.close()

                         
class DataStasher():
    """
    provide tables from database

    ideally could also be used to fill gaps in CmclFrame
    automatically
    """
    def __init__(self, filename: str, tblname: str, df):
        self._conn = sqlite3.connect(os.expanduser(filename))
        self._tbl = tblname

    def read(self):
        df = pd.read_sql((self._tbl,
                          self._conn, 
                          if_exists='replace')
        self._conn.close()
