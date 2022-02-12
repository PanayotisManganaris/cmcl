#debugging will occur and info level from now on...
#apparently some imports log themselves -- bogs down repl
#pandas is culprit?
import logging
logfmt = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S", format=logfmt)

# data handling
from sklearn.preprocessing import StandardScaler

# ML Model Specific Packages
from sklearn.ensemble import RandomForestRegressor

# model init 
from sklearn.model_selection import train_test_split

# model optimization
from sklearn.model_selection import GridSearchCV

#data tools
import numpy as np
import pandas as pd
import sqlite3

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
        self.X_train.assign(partition="train").set_index('partition', append=True, inplace=True)
        self.X_test.assign(partition="test").set_index('partition', append=True, inplace=True)
        self.Y_train.assign(partition="train").set_index('partition', append=True, inplace=True)
        self.Y_test.assign(partition="test").set_index('partition', append=True, inplace=True)

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
        elif r and r=="tmp" or r=="temporary":
            self.r = RandomForestRegressor()
            self._ret_r = False
            self._parametrize()
        else:
            self.r = RandomForestRegressor()
            self._ret_r = True
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
        yrp_i = self.X_train.index #whatever the original split order, the input decides
        yrp_c = self.Y_train.columns
        yrp = pd.DataFrame(list(Y_train_pred), index = yrp_i, columns = yrp_c)
        yrp = yrp.add_prefix("p_")
        return yrp

    def _test(self):
        Y_test_pred = self.r.predict(self.X_test)
        ysp_i = self.X_test.index
        ysp_c = self.Y_test.columns
        ysp = pd.DataFrame(list(Y_test_pred), index = ysp_i, columns = ysp_c)
        ysp = ysp.add_prefix("p_")
        return ysp
    
    def train_test_return(self):
        Y_trp = self._train()
        Y_tsp = self._test()
        X_tr = self.X_train
        X_ts = self.X_test
        self.X_stack = pd.concat([X_tr, X_ts], axis = 0)
        self.Y_stack = pd.concat([Y_trp, Y_tsp], axis = 0)
        if not self._ret_r:
            self.r = None # little cludgy?

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
#
#  ##  Calculate RMSE Values  ##
#  
#  Y_test_mse = sklearn.metrics.mean_squared_error(Y_pbe_test, Pred_pbe_test)
#  Y_train_mse = sklearn.metrics.mean_squared_error(Y_pbe_train, Pred_pbe_train)
#  print('rmse_test_matrix = ', np.sqrt(Y_test_mse))
#  print('rmse_train_matrix = ', np.sqrt(Y_train_mse))
#  print('      ')
