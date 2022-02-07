import pandas as pd
from cmcl.data.handle_cmcl_frame import FeatureAccessor

# import sqlite3
# 
# sql_string = '''SELECT * 
#                 FROM mannodi_agg'''
# conn = sqlite3.connect("/home/panos/MannodiGroup/data/perovskites.db")
# df = pd.read_sql(sql_string,
#                  conn,
#                  index_col='index')
# conn.close()

#test_df = df[["Formula", "PBE_bg_eV"]]

test_df = pd.DataFrame({'Formula': {1: 'MAGeBr3', 2: 'MAGeI3', 3: 'MASnCl3', 4: 'MASnBr3'},
                        'PBE_bg_eV': {1: 1.612, 2: 1.311, 3: 1.582, 4: 1.262}})

test_df.ft.comp()

# ideally the result of this call should first generate the comp table
# and then, every subsequent time simply indexes the array it's created
# the ft method is defined by the FeatureAccessor Class

# i think eventually this means the dataframes can be made to
# dynamically generate features even as more formula are added
