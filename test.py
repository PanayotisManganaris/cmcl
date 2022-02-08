import pandas as pd
from cmcl.data.handle_cmcl_frame import FeatureAccessor

import sqlite3

##  Load Dataset  ##
# point to your local copy of the db (updated on box) for now
# eventually will gather data from vasp runs
# or from csv files at root
sql_string = '''SELECT * 
                FROM mannodi_agg'''
conn = sqlite3.connect("/home/panos/MannodiGroup/data/perovskites.db")
df = pd.read_sql(sql_string,
                 conn,
                 index_col='index')
conn.close()

def main():
    bdf = df[["Formula", "sim_cell", "PBE_LC", "PBE_bgType", "PBE_bg_eV", "PBE_dbg_eV", "PBE_FormE_eV", "PBE_DecoE_eV", "dielc", "PV_FOM", "SLME_5um", "SLME_100um", "HSE_LC", "HSE_bgType", "HSE_bg_eV", "HSE_dbg_eV", "HSE_FormE_eV", "HSE_DecoE_eV"]]
    comp = bdf.ft.comp()
    
    return comp, 

if __name__ == '__main__':
    comp_df = main()
    print(comp_df)
