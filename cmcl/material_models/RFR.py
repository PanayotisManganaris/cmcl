# data handling
from cmcl.data.handle_cmcl_frame import FeatureAccessor

from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import normalize
from sklearn.pipeline import Pipeline

# model checking
from sklearn.model_selection import cross_validate
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold

# ML Model Specific Packages
from sklearn import linear_model
from sklearn.ensemble import RandomForestRegressor

# model optimization
from sklearn.model_selection import GridSearchCV

#import keras
from keras.models import Sequential
from keras.layers import Dropout
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor

#data tools
import numpy as np
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt


class 


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


