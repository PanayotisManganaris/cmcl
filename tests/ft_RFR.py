import pandas as pd
from cmcl.data.frame import FeatureAccessor
from cmcl.data.frame import SummaryAccessor
from cmcl.data.frame import TransformAccessor
from cmcl.data.frame import ModelAccessor

import sqlite3

import matplotlib.pyplot as plt

#from cmcl.data.spyglass import PairPlot
from sklearn.metrics import mean_squared_error

#load data
conn = sqlite3.connect("/home/panos/MannodiGroup/data/perovskites.db")

sql_string = '''SELECT * 
                FROM mannodi_agg'''
mannodi_df = pd.read_sql(sql_string,
                         conn,
                         index_col='index')

sql_string = '''SELECT * 
                FROM almora_agg'''
almora_df = pd.read_sql(sql_string,
                        conn,
                        index_col='index')
conn.close()

mannodi_df = mannodi_df[["Formula", "sim_cell", "PBE_LC", "PBE_bgType", "PBE_bg_eV", "PBE_dbg_eV", "PBE_FormE_eV", "PBE_DecoE_eV", "dielc", "PV_FOM", "SLME_5um", "SLME_100um", "HSE_LC", "HSE_bgType", "HSE_bg_eV", "HSE_dbg_eV", "HSE_FormE_eV", "HSE_DecoE_eV"]]

mcomp = mannodi_df.ft.comp().fillna(0)

bgm = mannodi_df.PBE_bg_eV.to_frame()
bgmp, Rcomp, Rbgm = bgm.model.RFR(mcomp)
bgmp_vs = pd.merge(bgmp, bgm, left_on='index', right_on='index')
bgmp_vs.index = bgmp.index

