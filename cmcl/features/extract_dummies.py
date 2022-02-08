import pandas as pd
import numpy as np

class DummyTable():
    def __init__(self, df):
        self._validate(df)
        self.df = df
        self._cols_before_update = df.columns.values

    @staticmethod
    def _validate(df):
        """
        id cols with lists inside or dicts inside
        warn
        """
        for nncol_name in df.select_dtypes(include=["object"]).columns:
            el_not_str = df[nncol_name].apply(lambda x: not isinstance(x, str))
            log = f"""These records contain non-numeric, non-string dtypes:
            {df.loc[el_not_str, nncol_name].index}"""
            if el_not_str.any():
                logging.critical(log)
                raise ValueError("data is not suitable for one-hot encoding. see log")
            

    def make_and_get(self):
        """
        one-hot-encode categorical variables. Not including Formula, so it can be used on base input easily.
        can't imagine why you'd want to ohe formula strings
        """
        #make in one swoop
        self.df = pd.get_dummies(self.df.loc[:, self.df.columns != "Formula"])
        #get indices
        original = self._cols_before_update
        updated = self.df.columns.values
        is_not_original_content = np.vectorize(lambda x: x not in original)
        ohe_cols_idx = is_not_original_content(updated)
        ohe_cols = updated[ohe_cols_idx]
        return ohe_cols
