# apply model trained on one dataset to other datasets
# in this case, bgm's Rbgm regressor is applied to bga

# data utilities
import pandas as pd
from cmcl.data.frame import FeatureAccessor
from cmcl.data.frame import SummaryAccessor
from cmcl.data.frame import TransformAccessor
from cmcl.data.frame import ModelAccessor

import sqlite3
from cmcl.data.utils import *

# analysis tools
#from cmcl.data.spyglass import PairPlot
from sklearn.metrics import mean_squared_error
import math
import matplotlib.pyplot as plt

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

almora_df = almora_df[["Formula", "bg_eV", "PCE%", "Voc_mV", "Jsc_mA/cm2", "FF%"]]

#generate features
mcomp = mannodi_df.ft.comp().fillna(0)
acomp = almora_df.ft.comp()

#create model and results using computational data
bgm = mannodi_df.PBE_bg_eV.to_frame()
bgmp, Rmcomp, Rbgm = bgm.model.RFR(mcomp)

#drop non-numeric X AND Y from consideration
boolindex=acomp.applymap(lambda x: isinstance(x, str)).any(axis=1)
acomp = acomp[~boolindex].fillna(0)
bga = almora_df.bg_eV.to_frame()[~boolindex]

#apply previous model to experimental data
bgap, Racomp, Rbgm = bga.model.RFR(acomp, r=Rbgm)

#prepare for comparisons
bgmp_vs = pd.merge(bgmp, bgm, left_on='index', right_on='index')
bgmp_vs.index = bgmp.index
bgmp_vs = pvse(bgmp_vs) #cmcl utility orders target/prediction columns correctly

bgap_vs = pd.merge(bgap, bga, left_on='index', right_on='index')
bgap_vs.index = bgap.index
bgap_vs = pvse(bgap_vs)

#make comparisons
print(f"native prediction rmse: {math.sqrt(mean_squared_error(bgmp_vs.iloc[0], bgmp_vs.iloc[1]))}")
print(f"reapplied prediction rmse: {math.sqrt(mean_squared_error(bgap_vs.iloc[0], bgap_vs.iloc[1]))}")

#ax1 = bgap_vs.plot.scatter(x="bg_eV", y="p_bg_eV")
#ax1.axline((0,0), slope = 1)
#ax2 = bgmp_vs.plot.scatter(x="PBE_bg_eV", y="p_PBE_bg_eV")
#ax2.axline((0,0), slope = 1)
#plt.rcParams['axes.labelsize'] = 35
#plt.show()
