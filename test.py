import pandas as pd
from cmcl.data.handle_cmcl_frame import FeatureAccessor
from cmcl.features.extract_constituents import CompositionTable

import sqlite3

sql_string = '''SELECT * 
                FROM mannodi_agg'''
conn = sqlite3.connect("/home/panos/MannodiGroup/data/perovskites.db")
df = pd.read_sql(sql_string,
                 conn,
                 index_col='index')
conn.close()

test_df = df[["Formula", "PBE_bg_eV"]]

# test_df = pd.DataFrame({'Formula': {1: 'MAGeBr3', 2: 'MAGeI3', 3: 'MASnCl3', 4: 'MASnBr3'},
#                         'PBE_bg_eV': {1: 1.612, 2: 1.311, 3: 1.582, 4: 1.262}})

comp_matrix = test_df.ft.comp()
print(comp_matrix)