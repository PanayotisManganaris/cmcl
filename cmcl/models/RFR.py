#debugging will occur and info level from now on...
#apparently some imports log themselves -- bogs down repl
#pandas is culprit?
import logging
logfmt = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S", format=logfmt)

import pandas as pd

# model init 
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

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
    def __init__(self, X, Y, r=None, t=0.8, **kwargs):
        """
        instantiate regressor object and data for specific regression

        initially regressor is instantiated with some defaults
        """
        self.r = r
        self.t = t
        for k,v in kwargs.items():
            setattr(self, k, v)
            
        self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(X, Y, train_size=self.t)
        self.X_train = self.X_train.assign(partition="train").set_index('partition', append=True)
        self.X_test = self.X_test.assign(partition="test").set_index('partition', append=True)
        self.Y_train = self.Y_train.assign(partition="train").set_index('partition', append=True)
        self.Y_test = self.Y_test.assign(partition="test").set_index('partition', append=True)

        #if optimize:
        #    #do a type of RFR optimization -- define later as wrapper around gridsearch?
        #    self.r = RandomForestRegressor(n_estimators=ntrees, max_features=max_features)
        #else:
        #    #need a good way of choosing defaults automatically...
        
        if self.r and isinstance(self.r, RandomForestRegressor):
            # RFR could be a subclass of the general "regression" object
            # parametrization is specific, the rest is general...
            self._ret_r = True
            self._parametrize()
        elif self.r and self.r=="tmp" or self.r=="temporary":
            self.r = RandomForestRegressor()
            self._ret_r = False
            self._parametrize()
        else:
            self.r = RandomForestRegressor()
            self._ret_r = True
            self._parametrize()

    def _parametrize(self):
        """
        pass or set-default configuration parameters to sklearn random
        forest regressor
        """
        self.r.set_params(**{'bootstrap': getattr(self, "bootstrap", True),
                             'ccp_alpha': getattr(self, "ccp_alpha", 0.0),
                             'criterion': getattr(self, "criterion", 'squared_error'),
                             'max_depth': getattr(self, "max_depth", None),
                             'max_features': getattr(self, "max_features", None),
                             'max_leaf_nodes': getattr(self, "max_leaf_nodes", None),
                             'max_samples': getattr(self, "max_samples", None),
                             'min_impurity_decrease': getattr(self, "min_impurity_decrease", 0.0),
                             'min_samples_leaf': getattr(self, "min_samples_leaf", 1),
                             'min_samples_split': getattr(self, "min_samples_split", 2),
                             'min_weight_fraction_leaf': getattr(self, "min_weight_fraction_leaf", 0.0),
                             'n_estimators': getattr(self, "n_estimators", 100),
                             'n_jobs': getattr(self, "n_jobs", None),
                             'oob_score': getattr(self, "oob_score", False),
                             'random_state': getattr(self, "random_states", None),
                             'verbose': getattr(self, "verbose", 0),
                             'warm_start': getattr(self, "warm_start", False)})
        
    def _train(self):
        if self.Y_train.values.shape[1] == 1:
            self.r.fit(self.X_train, self.Y_train.values.ravel())
        else:
            self.r.fit(self.X_train, self.Y_train)
        Y_train_pred = self.r.predict(self.X_train)
        yrp_i = self.X_train.index #whatever the original split order, the input decides
        yrp_c = self.Y_train.columns
        yrp = pd.DataFrame(Y_train_pred, index = yrp_i, columns = yrp_c)
        yrp = yrp.add_suffix("_p")
        return yrp

    def _test(self):
        Y_test_pred = self.r.predict(self.X_test)
        ysp_i = self.X_test.index
        ysp_c = self.Y_test.columns
        ysp = pd.DataFrame(Y_test_pred, index = ysp_i, columns = ysp_c)
        ysp = ysp.add_suffix("_p")
        return ysp
    
    def train_test_return(self):
        Y_trp = self._train()
        Y_tsp = self._test()
        X_tr = self.X_train
        X_ts = self.X_test
        self.X_stack = pd.concat([X_tr, X_ts], axis = 0)
        self.Y_stack = pd.concat([Y_trp, Y_tsp], axis = 0)
        if not self._ret_r:
            self.r = None
