import logging
logfmt = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S", format=logfmt)

import pandas as pd
import numpy as np
#access feature computers
from cmcl.features.extract_constituents import CompositionTable

#access transformers
from cmcl.features.extract_categories import DummyTable
from cmcl.features.extract_categories import LabelGrouper

from cmcl.transforms.PCA import PCA

#access models
from cmcl.models.RFR import RFR

# feature accessors should saveable in some way for future use/reporting

# model accessors perhaps can be saved, but are often not.
# expensive models should be saved, though...

@pd.api.extensions.register_dataframe_accessor("ft")
class FeatureAccessor():
    """
    Conveniently and robustly define and retrieve feature tables

    when table does not exist, it will be created.

    basic chemical descriptors:
    composition_tbl = CmclFrame.ft.comp()
    prop_tbl = CmclFrame.ft.prop()
    
    pymatgen descriptors:
    matminer_tbl = CmclFrame.ft.mtmr()

    MEGnet descriptors:
    meg_tbl = CmclFrame.meg()
    """

    def __init__(self, df):
        self._validate(df)
        #getting original
        self._df = df
        #storing dummies 
        self._ohedf = None
        #storing physical comp features
        self._compdf = None
        
    @staticmethod
    def _validate(df):
        """
        verify df contains
        a series of Formula
        at least one series of measurements
        """
        # only general checks should be done here
        pass
        # if df.columns.values.shape[0] < 2:
        #     #warn user no ml can be done on current data

    def base(self):
        return self._df
        
    def ohe(self, regen=False):
        if self._ohe_cols is None or regen:
            feature = DummyTable(self._df)
            self._ohedf = feature.make()
        return self._ohedf

    def comp(self, regen=False):
        """
        Default call accesses or creates composition table.
        call with regen=True to regenerate existing composition table
        """
        if self._compdf is None or regen:
            feature = CompositionTable(self._df)
            self._compdf = feature.make()
        return self._compdf
    
    def mtmr(self):
        """get array of dscribe inorganic crystal properties"""
        print("matminer Not Implemented")

    def meg(self):
        """get array of MEGnet properties"""
        print("megnet Not Implemented")


@pd.api.extensions.register_dataframe_accessor("ABX")
class PerovskiteAccessor():
    """
    Conveniently and robustly define and retrieve categorical summaries of data

    when table does not exist, it will be created.

    these summary columns are all intended to work with X.ft.ohe()
    which can one-hot encode any one in a simple oneliner

    X.sm.mix().ft.ohe()

    Human descriptors:
    mixing_sites = CmclFrame.ft.comp().sm.mix

    continuous metric descretizations
    distribution_table = CmclFrame["metric"].sm.bin(nbins)
    """
    def __init__(self, df):
        self._validate(df)
        #getting original
        self._df = df
        #getting mix categories
        self._mix_mod_df = None
        self._mix_cols = None
        
    @staticmethod
    def _validate(df):
        """
        verify df contains at least one series of measurements
        """
        pass

    def base(self):
        return self._df
        
    def _mixreader(self, row):
      mixstring = " & "
      stringlist=[]
      if row[0] > 1:
          stringlist.append("A")
      elif row[0] < 1:
          stringlist.append("error")
      if row[1] > 1:
          stringlist.append("B")
      elif row[1] < 1:
          stringlist.append("error")
      if row[2] > 1:
          stringlist.append("X")
      elif row[2] < 1:
          stringlist.append("error")
      if stringlist:
          stringlist[-1] = stringlist[-1] + "-site"
      if not stringlist:
          stringlist.append("Pure")
      mixstring = mixstring.join(stringlist)
      return mixstring

    def mix(self):
        """
        provides default access to ColumnGrouper. categorizes
        perovskite's by site mixing when applied to a composition
        table.
        """
        segments = {"A":["MA", "FA", "Cs", "Rb", "K"],
                    "B":["Pb", "Sn", "Ge", "Ba", "Sr", "Ca", "Be", "Mg", "Si", "V", "Cr", "Mn", "Fe", "Ni", "Zn", "Pd", "Cd", "Hg"],
                    "X":["I", "Br", "Cl"]}
        extender = LabelGrouper(self._df, **segments)
        mixlog = extender.sum_groups()
        mixing = mixlog.apply(lambda row: self._mixreader(row), axis=1)
        mixing.name="mixing"
        return mixing
                
@pd.api.extensions.register_dataframe_accessor("tf")
class TransformAccessor():
    """
    Conveniently and robustly define and retrieve transforms of tables

    when transform does not exist, it will be created.

    these transforms can be applied to any X.ft.function()
    with a simple one-liner
    
    X.ft.comp().tf.pca()

    provides signal analysis transforms
    FFT, Hilbert, etc

    decompositions
    PCA, etc

    kernel transforms
    TSNE, UMAP, SISSO, etc
    """
    def __init__(self, df):
        self._validate(df)
        #getting original
        self._df = df
        #getting mix categories
        self._PCA_mod_df = None
        self._PCA_cols = None
        
    @staticmethod
    def _validate(df):
        """
        verify df contains numerical data of the float dtype
        """
        pass

    def base(self):
        return self._df
        
    def _make_pca(self):
        extender = PCATable(self._df)
        self._pca_cols = extender.make_and_get()
        self._pca_mod_df = extender.df

    def _get_pca(self):
        return self._pca_mod_df[self._pca_cols]
        
    def pca(self):
        #wishlist: make the score matrix recoverable for biplotting
        if self._pca_cols is None:
            self._make_pca()
        return self._get_pca()

@pd.api.extensions.register_dataframe_accessor("model")
class ModelAccessor():
    """
    Conveniently and robustly define and retrieve models of tables based on other tables

    An accessed table will have models created for it. models are
    stored with the accessor instance, predictions are not. 

    predictions and models can be obtained with a simple one-liner
    
    Y.model.RFR(X, optimize=True)

    provides
    RFR
    GRR
    NN
    """
    def __init__(self, Y):
        self._validate(Y)
        #getting original
        self._df = Y
        #existing models
        self._RFR = None
        
    @staticmethod
    def _validate(Y):
        """
        verify Y contains numerical data

        flag weather categorical or continuous?
        """
        pass
    
    def base(self):
        return self._df
    
    def _do_RFR(self, X, **kwargs): #extend args?
        modeler = RFR(X, self._df, **kwargs)
        modeler.train_test_return()
        self._RFR = modeler
    
    def RFR(self, X, **kwargs):
        """
        return a model of Y based on X, The form of X used,
        and optionally the model used to get Y.

        Both Y and X are returned with pandas multindex

        this can be used to access the train/test split for each
        dataframe conveniently using pandas tuple indexing, the pandas
        IndexSlice module, or the .xs (cross section) method.
        """
        if self._RFR is None:
            self._do_RFR(X, **kwargs)
        return self._RFR.Y_stack, self._RFR.X_stack, self._RFR.r
