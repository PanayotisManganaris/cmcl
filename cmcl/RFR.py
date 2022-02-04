#import os
#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import sklearn
from sklearn import linear_model
from sklearn.model_selection import cross_validate
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold

##  ML Model Specific Packages  ##
from sklearn.linear_model import Lasso
from sklearn.linear_model import ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import DotProduct, WhiteKernel
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C, ExpSineSquared
from sklearn.gaussian_process.kernels import Matern, RationalQuadratic
from sklearn.kernel_ridge import KernelRidge
from sklearn.model_selection import GridSearchCV
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import WhiteKernel, ExpSineSquared
import tensorflow.keras as keras
#import keras
from keras.models import Sequential
from keras.layers import Dropout
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

#data tools
import pandas as pd
import sqlite3

import numpy as np

import copy 
import random

#plot tools
import matplotlib.pyplot as plt

#from mlpy import KernelRidge
from sklearn.preprocessing import normalize

##  Load Dataset  ##
sql_string = '''SELECT * 
                FROM mannodi_agg'''
conn = sqlite3.connect("/home/panos/MannodiGroup/data/perovskites.db")
df = pd.read_sql(sql_string,
                 conn,
                 index_col='index')
conn.close()

### create data arrays from dataframe ###
test_len = np.vectorize(len)
comp_cols = df.columns.values[test_len(df.columns.values) <= 2].tolist()
PBE_content = np.vectorize(lambda x: x.__contains__(("PBE")))
SLME_content = np.vectorize(lambda x: x.__contains__(("SLME")))
FOM_content = np.vectorize(lambda x: x.__contains__(("FOM")))
HSE_content = np.vectorize(lambda x: x.__contains__(("HSE")))
PBE_cols = df.columns.values[PBE_content(df.columns.values)].tolist()
SLME_cols = df.columns.values[PBE_content(df.columns.values)].tolist()
PV_FOM_cols = df.columns.values[PBE_content(df.columns.values)].tolist()
HSE_cols = df.columns.values[PBE_content(df.columns.values)].tolist()
Xprop_content = np.vectorize(lambda x: x.__contains__("X_"))
Xprop_cols = df.columns.values[Xprop_content(df.columns.values)].tolist()
Bprop_content = np.vectorize(lambda x: x.__contains__("B_"))
Bprop_cols = df.columns.values[Bprop_content(df.columns.values)].tolist()
Aprop_content = np.vectorize(lambda x: x.__contains__("A_"))
Aprop_cols = df.columns.values[Aprop_content(df.columns.values)].tolist()


X_comp = df[comp_cols]
X_prop = df[[*Aprop_cols, *Bprop_cols, *Xprop_cols]]
Y_PBE = df[[*PBE_cols, *PV_FOM_cols, *SLME_cols]]
Y_HSE = df[HSE_cols]

###  Training-Test Split  ###

t = 0.20

X_comp_train, X_comp_test, Y_pbe_train, Y_pbe_test = train_test_split(X_comp, Y_PBE, test_size=t)

X_comp_train, X_comp_test, Y_hse_train, Y_hse_test = train_test_split(X_comp, Y_HSE, test_size=t)

X_prop_train, X_prop_test, Y_pbe_train, Y_pbe_test = train_test_split(X_prop, Y_PBE, test_size=t)

X_prop_train, X_prop_test, Y_hse_train, Y_hse_test = train_test_split(X_prop, Y_HSE, test_size=t)

##  Define Random Forest Hyperparameter Space  ##
#param_grid = {
#"n_estimators": [100, 200],
#"max_features": [10, 30, m],
#"min_samples_leaf": [10, 20],
#"max_depth": [10, 20, 40],
#"min_samples_split": [2, 5, 10]
#}
param_grid = { "n_estimators": [100]}

###  Train Model For Lattice Constant  ###
rfr_prop = GridSearchCV(RandomForestRegressor(), param_grid=param_grid, cv=5)
rfr_comp = GridSearchCV(RandomForestRegressor(), param_grid=param_grid, cv=5)
#rfr_prop.fit(X_prop_train, Y_pbe_train)
rfr_comp.fit(X_comp_train, Y_pbe_train) #doesn't work due to NaNs
Pred_pbe_prop_train = rfr_prop.predict(X_prop_train)
Pred_pbe_prop_test  = rfr_prop.predict(X_prop_test)

##  Calculate RMSE Values  ##

Y_test_mse = sklearn.metrics.mean_squared_error(Y_pbe_test, Pred_pbe_test)
Y_train_mse = sklearn.metrics.mean_squared_error(Y_pbe_train, Pred_pbe_train)
print('rmse_test_matrix = ', np.sqrt(Y_test_mse))
print('rmse_train_matrix = ', np.sqrt(Y_train_mse))
print('      ')

#  ML Parity Plots ##

fig, ( [ax1, ax2], [ax3, ax4] ) = plt.subplots( nrows=2, ncols=2, figsize=(8,8) )
fig.text(0.5, 0.03, 'DFT Calculation', ha='center', fontsize=32)
fig.text(0.02, 0.5, 'ML Prediction', va='center', rotation='vertical', fontsize=32)
plt.subplots_adjust(left=0.14, bottom=0.14, right=0.97, top=0.92, wspace=0.30, hspace=0.40)
plt.rc('font', family='Arial narrow')

Prop_train_temp = copy.deepcopy(Prop_train_latt_fl)
Pred_train_temp = copy.deepcopy(Pred_train_latt_fl)
Prop_test_temp  = copy.deepcopy(Prop_test_latt_fl)
Pred_test_temp  = copy.deepcopy(Pred_test_latt_fl)
a = [-175,0,125]
b = [-175,0,125]
ax1.plot(b, a, c='k', ls='-')
ax1.xaxis.set_tick_params(labelsize=20)
ax1.yaxis.set_tick_params(labelsize=20)
ax1.scatter(Prop_train_temp[:], Pred_train_temp[:], c='orangered', marker='s', s=60, edgecolors='dimgrey', alpha=0.9, label='Training')
ax1.scatter(Prop_test_temp[:], Pred_test_temp[:], c='lawngreen', marker='s', s=60, edgecolors='dimgrey', alpha=0.9, label='Test')
te = '%.2f' % rmse_test_latt
tr = '%.2f' % rmse_train_latt
ax1.text(5.96, 5.48, 'Test_rmse = ' + te + ' $\AA$', c='navy', fontsize=16)
ax1.text(5.93, 5.28, 'Train_rmse = ' + tr + ' $\AA$', c='navy', fontsize=16)
ax1.set_ylim([5.1, 7.1])
ax1.set_xlim([5.1, 7.1])
ax1.set_xticks([5.5, 6.0, 6.5, 7.0])
ax1.set_yticks([5.5, 6.0, 6.5, 7.0])
ax1.set_title('Lattice Constant ($\AA$)', c='k', fontsize=20, pad=12)
ax1.legend(loc='upper left',ncol=1, frameon=True, prop={'family':'Arial narrow','size':12})

Prop_train_temp = copy.deepcopy(Prop_train_decomp_fl)
Pred_train_temp = copy.deepcopy(Pred_train_decomp_fl)
Prop_test_temp  = copy.deepcopy(Prop_test_decomp_fl)
Pred_test_temp  = copy.deepcopy(Pred_test_decomp_fl)
ax2.plot(b, a, c='k', ls='-')
ax2.xaxis.set_tick_params(labelsize=20)
ax2.yaxis.set_tick_params(labelsize=20)
ax2.scatter(Prop_train_temp[:], Pred_train_temp[:], c='orangered', marker='s', s=60, edgecolors='dimgrey', alpha=0.9, label='Training')
ax2.scatter(Prop_test_temp[:], Pred_test_temp[:], c='lawngreen', marker='s', s=60, edgecolors='dimgrey', alpha=0.9, label='Test')
te = '%.2f' % rmse_test_decomp
tr = '%.2f' % rmse_train_decomp
ax2.text(0.58, -0.65, 'Test_rmse = ' + te + ' eV', c='navy', fontsize=16)
ax2.text(0.45, -1.19, 'Train_rmse = ' + tr + ' eV', c='navy', fontsize=16)
ax2.set_ylim([-1.7, 3.8])
ax2.set_xlim([-1.7, 3.8])
ax2.set_xticks([-1.0, 0.0, 1.0, 2.0, 3.0])
ax2.set_yticks([-1.0, 0.0, 1.0, 2.0, 3.0])
ax2.set_title('Decomposition Energy (eV)', c='k', fontsize=20, pad=12)
#ax2.legend(loc='upper left',ncol=1, frameon=True, prop={'family':'Arial narrow','size':12})

Prop_train_temp = copy.deepcopy(Prop_train_gap_fl)
Pred_train_temp = copy.deepcopy(Pred_train_gap_fl)
Prop_test_temp  = copy.deepcopy(Prop_test_gap_fl)
Pred_test_temp  = copy.deepcopy(Pred_test_gap_fl)
ax3.plot(b, a, c='k', ls='-')
ax3.xaxis.set_tick_params(labelsize=20)
ax3.yaxis.set_tick_params(labelsize=20)
ax3.scatter(Prop_train_temp[:], Pred_train_temp[:], c='orangered', marker='s', s=60, edgecolors='dimgrey', alpha=0.9, label='Training')
ax3.scatter(Prop_test_temp[:], Pred_test_temp[:], c='lawngreen', marker='s', s=60, edgecolors='dimgrey', alpha=0.9, label='Test')
te = '%.2f' % rmse_test_gap
tr = '%.2f' % rmse_train_gap
ax3.text(2.50, 1.10, 'Test_rmse = ' + te + ' eV', c='navy', fontsize=16)
ax3.text(2.36, 0.52, 'Train_rmse = ' + tr + ' eV', c='navy', fontsize=16)
ax3.set_ylim([0.0, 6.0])
ax3.set_xlim([0.0, 6.0])
ax3.set_xticks([1, 2, 3, 4, 5])
ax3.set_yticks([1, 2, 3, 4, 5])
ax3.set_title('Band Gap (eV)', c='k', fontsize=20, pad=12)
#ax3.legend(loc='upper left',ncol=1, frameon=True, prop={'family':'Arial narrow','size':12})

Prop_train_temp = copy.deepcopy(Prop_train_fom_fl)
Pred_train_temp = copy.deepcopy(Pred_train_fom_fl)
Prop_test_temp  = copy.deepcopy(Prop_test_fom_fl)
Pred_test_temp  = copy.deepcopy(Pred_test_fom_fl)
ax4.plot(b, a, c='k', ls='-')
ax4.xaxis.set_tick_params(labelsize=20)
ax4.yaxis.set_tick_params(labelsize=20)
ax4.scatter(Prop_train_temp[:], Pred_train_temp[:], c='orangered', marker='s', s=60, edgecolors='dimgrey', alpha=0.9, label='Training')
ax4.scatter(Prop_test_temp[:], Pred_test_temp[:], c='lawngreen', marker='s', s=60, edgecolors='dimgrey', alpha=0.9, label='Test')
te = '%.2f' % rmse_test_fom
tr = '%.2f' % rmse_train_fom
ax4.text(4.33, 3.15, 'Test_rmse = ' + te, c='navy', fontsize=16)
ax4.text(4.23, 2.8, 'Train_rmse = ' + tr, c='navy', fontsize=16)
ax4.set_ylim([2.5, 6.2])
ax4.set_xlim([2.5, 6.2])
ax4.set_xticks([3, 4, 5, 6])
ax4.set_yticks([3, 4, 5, 6])
ax4.set_title('Figure of Merit (log$_{10}$)', c='k', fontsize=20, pad=12)
#ax4.legend(loc='upper left',ncol=1, frameon=True, prop={'family':'Arial narrow','size':12})

plt.show()
#plt.savefig('plot_PBE_RFR_models.pdf', dpi=450)
