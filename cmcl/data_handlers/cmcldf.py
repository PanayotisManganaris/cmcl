import pandas as pd
from cmcl.features.extract_constituents import CompTable

@pd.api.extensions.register_dataframe_accessor("ft")
class FeatureAccessor():
    """
    Conveniently and robustly define and retrieve training/target tables

    for certain Ml descriptors, when set does not exist, it will be created.

    if no targets exist, flag modelers to notify user.

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
        self._df = df

    @staticmethod
    def _validate(given_df):
        """
        verify df contains
        a series of Formula
        at least one series of measurements
        """
        if given_df.columns.values.shape < 2:
            if "Formula" not in given_df.columns:
                if "formula" in given_df.columns:
                    given_df.rename(columns = {"formula":"Formula"})
                else:
                    raise AttributeError("No Formula Column Named")
        
    def comp(self):
        """get array of formula's constituent quantities"""

    def mtmr(self):
        """get array of dscribe inorganic crystal properties"""

    def meg(self):
        """get array of MEGnet properties"""
        

class DataProvider():
    """
    provide tables from database

    ideally could also be used to fill gaps in CmclFrame
    automatically
    """
