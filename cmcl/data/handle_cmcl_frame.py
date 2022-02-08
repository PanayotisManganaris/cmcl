import logging
logfmt = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S", format=logfmt)

import pandas as pd
import numpy as np
from cmcl.features.extract_constituents import CompositionTable
from cmcl.features.extract_dummies import DummyTable

@pd.api.extensions.register_dataframe_accessor("ft")
class FeatureAccessor():
    """
    Conveniently and robustly define and retrieve training/target tables

    when table does not exist, it will be created.

    wishlist:
    - keep track of accessor objects in db for working with
    stored tables. store cols lists as df._metadata? or a textdoc changelog?
    - if no targets exist, flag modelers to notify user.

    Human descriptors:
    human = CmclFrame.ft.human = CmclFrame["Formula", "Mixing"[, "Supercell"]]

    basic chemical descriptors:
    composition_tbl = CmclFrame.compositions = CmclFrame[compositions]
    prop_tbl = CmclFrame.ft.properties

    pymatgen descriptors:
    matminer_tbl = CmclFrame.ft.dscribe

    MEGnet descriptors:
    meg_tbl = CmclFrame.megnet
    """

    def __init__(self, df):
        self._validate(df)
        #getting original
        self._df = df
        #getting dummies 
        self._ohe_mod_df = None
        self._ohe_cols = None
        #getting physical comp features
        self._comp_mod_df = None
        self._comp_cols = None
        
    @staticmethod
    def _validate(df):
        """
        verify df contains
        a series of Formula
        at least one series of measurements
        """
        if df.columns.values.shape[0] < 2:
            pass #warn user no ml can be done on current data
        else:
            pass
        if "Formula" not in df.columns:
            if "formula" in df.columns:
                df.rename(columns = {"formula":"Formula"})
            else:
                raise AttributeError("No Formula Column Named")

    def base(self):
        return self._df
        
    def _make_ohe(self):
        extender = DummyTable(self._df)
        self._ohe_cols = extender.make_and_get()
        self._ohe_mod_df = extender.df

    def _get_ohe(self):
        return self._ohe_mod_df[self._ohe_cols]

    def ohe(self):
        if self._ohe_cols is None:
            self._make_ohe()
        return self._get_ohe()

    def _make_comp(self):
        """get array of formula's constituent quantities"""
        extender = CompositionTable(self._df)
        self._comp_cols = extender.make_and_get()
        self._comp_mod_df = extender.df

    def _get_comp(self):
        return self._comp_mod_df[self._comp_cols]

    def comp(self):
        """
        once called, the resulting training set is static?
        note to self: maybe calling the accessor on new records added to the dataframe resets it...
        """
        if self._comp_cols is None:
            self._make_comp()
        return self._get_comp()

    
    
    def mtmr(self):
        """get array of dscribe inorganic crystal properties"""
        print("matminer Not Implemented")

    def meg(self):
        """get array of MEGnet properties"""
        print("megnet Not Implemented")
