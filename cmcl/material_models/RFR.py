#debugging will occur and info level from now on...
#apparently some imports log themselves -- bogs down repl
#pandas is culprit?
import logging
logfmt = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S", format=logfmt)

# data handling
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import normalize
from sklearn.pipeline import Pipeline

# ML Model Specific Packages
from sklearn.ensemble import RandomForestRegressor

# model init 
from sklearn.model_selection import train_test_split

# model validation
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_validate
from sklearn.model_selection import cross_val_score


# model optimization
from sklearn.model_selection import GridSearchCV

#data tools
import numpy as np
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

class RFR():
    """
    A Random Forest Regression object consisting of a regressor trained on
    given Xy or XY dataframes according to test/train split t.

    optionally instantiate using a predefined regressor, including one
    trained on another dataset.

    scikit learn's RFR implementation provides dynamical coverage of
    both single and multi output regressions

    regression results are dataframes with the necessary indexing
    information to select the train/test subset, however it was
    generated.
    """
    def __init__(self, X, Y, t=0.20, r=None):
        """
        instantiate regressor object and data for specific regression

        initially regressor is instantiated with some defaults
        """
        # make it an option to pass a list of splits
        # and get a dataframe that is condusive to learning curve plotting        
        self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(X, Y, test_size=t)
        #if optimize:
        #    #do a type of RFR optimization -- define later as wrapper around gridsearch?
        #    self.r = RandomForestRegressor(n_estimators=ntrees, max_features=max_features)
        #else:
        #    #need a good way of choosing defaults automatically...
        #    self.r = RandomForestRegressor(n_estimators=ntrees, max_features=max_features)
        if r and isinstance(r, RandomForestRegressor):
            # in future, RFR could be a subclass of the general "regression" object
            # parametrization is specific, the rest is general...
            self.r = r
        else:
            self.r = RandomForestRegressor()
            self._parametrize()

    def _parametrize(self):
        #use this to do optimization/scalability studies
        self.r.set_params(**{'bootstrap': True,
                             'ccp_alpha': 0.0,
                             'criterion': 'squared_error',
                             'max_depth': None,
                             'max_features': 'sqrt',
                             'max_leaf_nodes': None,
                             'max_samples': None,
                             'min_impurity_decrease': 0.0,
                             'min_samples_leaf': 1,
                             'min_samples_split': 2,
                             'min_weight_fraction_leaf': 0.0,
                             'n_estimators': 100,
                             'n_jobs': None,
                             'oob_score': False,
                             'random_state': None,
                             'verbose': 0,
                             'warm_start': False})

    def _train(self):
        self.r.fit(self.X_train, self.Y_train)
        Y_train_pred = self.r.predict(self.X_train)
        yrp_i = self.Y_train.index.to_list()
        yrp_c = self.Y_train.columns
        tpls = list(zip(*[["train" for i in yrp_i], yrp_i]))
        yrp_mi = pd.MultiIndex.from_tuples(tpls)
        return pd.DataFrame(list(Y_train_pred), index = yrp_mi, columns = yrp_c)
    #consider explicitly defining a categoricalindex?

    def _test(self):
        Y_test_pred = self.r.predict(self.X_test)
        ysp_i = self.Y_test.index.to_list()
        ysp_c = self.Y_train.columns
        tpls = list(zip(*[["test" for i in ysp_i], ysp_i]))
        ysp_mi = pd.MultiIndex.from_tuples(tpls)
        return pd.DataFrame(list(Y_test_pred), index = ysp_mi, columns = ysp_c)
    
    def train_test_return(self):
        Y_trp = self._train()
        Y_tsp = self._test()
        xr_i = self.X_train.index.to_list()
        xs_i = self.X_test.index.to_list()
        rtpls = list(zip(*[["train" for i in xr_i], xr_i]))
        stpls = list(zip(*[["test" for i in xs_i], xs_i]))
        xr_mi = pd.MultiIndex.from_tuples(rtpls)
        xs_mi = pd.MultiIndex.from_tuples(stpls)
        X_tr = self.X_train
        X_ts = self.X_test
        X_tr.index = xr_mi
        X_ts.index = xs_mi
        self.X_stack = pd.concat([X_tr, X_ts], axis = 0)
        self.Y_stack = pd.concat([Y_trp, Y_tsp], axis = 0)

#  ##  Define Random Forest Hyperparameter Space  ##
#  #param_grid = {
#  #"n_estimators": [100, 200],
#  #"max_features": [10, 30, m],
#  #"min_samples_leaf": [10, 20],
#  #"max_depth": [10, 20, 40],
#  #"min_samples_split": [2, 5, 10]
#  #}
#  param_grid = { "n_estimators": [100]}
#  
#  ###  Train Model For Lattice Constant  ###
#  rfr_prop = GridSearchCV(RandomForestRegressor(), param_grid=param_grid, cv=5)
#  rfr_comp = GridSearchCV(RandomForestRegressor(), param_grid=param_grid, cv=5)
#  #rfr_prop.fit(X_prop_train, Y_pbe_train)
#  rfr_comp.fit(X_comp_train, Y_pbe_train) #doesn't work due to NaNs
#  Pred_pbe_prop_train = rfr_prop.predict(X_prop_train)
#  Pred_pbe_prop_test  = rfr_prop.predict(X_prop_test)
#  
#  ##  Calculate RMSE Values  ##
#  
#  Y_test_mse = sklearn.metrics.mean_squared_error(Y_pbe_test, Pred_pbe_test)
#  Y_train_mse = sklearn.metrics.mean_squared_error(Y_pbe_train, Pred_pbe_train)
#  print('rmse_test_matrix = ', np.sqrt(Y_test_mse))
#  print('rmse_train_matrix = ', np.sqrt(Y_train_mse))
#  print('      ')
#  
#  
#  
