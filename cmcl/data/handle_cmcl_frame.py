import pandas as pd
from cmcl.features.extract_constituents import CompositionTable

@pd.api.extensions.register_dataframe_accessor("ft")
class FeatureAccessor():
    """
    Conveniently and robustly define and retrieve training/target tables

    when table does not exist, it will be created.

    wishlist:
    - keep track of accessor objects in db for working with
    stored tables. store cols lists as df._metadata?
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
        print("Not Implemented")

    def meg(self):
        """get array of MEGnet properties"""
        print("Not Implemented")
        
