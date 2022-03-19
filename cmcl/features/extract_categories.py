import logging
logfmt = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S", format=logfmt)

import pandas as pd
import numpy as np

class DummyTable():
    def __init__(self, df):
        self._validate(df)
        self.df = df
        self._original = df.columns.values

    @staticmethod
    def _validate(df):
        """
        id cols with lists inside or dicts inside
        warn
        """
        for nncol_name in df.select_dtypes(include=["object"]).columns:
            el_not_str = mannodi_df["PBE_bgType"].apply(lambda x: not (x is None or isinstance(x, (str, np.NaN, pd.NA))))
            log = f"""Records contain non-numeric, non-string, non-NoneType, dtypes
            {df.loc[el_not_str, nncol_name]}"""
            if el_not_str.any():
                logging.critical(log)
                raise ValueError("data is not suitable for one-hot encoding. see log")

    def _conditional_casefold(entry):
        if isinstance(entry, str):
            return entry.casefold()
        else:
            return entry

    def make(self):
        """
        one-hot-encode categorical variables in given df. (Not
        including Formula column).
        
        Convenience for using catagorical variables in models.

        wishlist: control prefixing dummy cols
        """
        normidx = list(map(self._conditional_casefold, df.columns))
        validx = ["Formula".casefold() not in label for label in normidx]
        #make in one swoop
        self.df = pd.get_dummies(self.df.loc[:, validx])
        #get indices
        updated = self.df.columns.values
        is_not_original_content = np.vectorize(lambda x: x not in self._original)
        ohe_cols_idx = is_not_original_content(updated)
        ohe_cols = updated[ohe_cols_idx]
        return self.df[ohe_cols]
