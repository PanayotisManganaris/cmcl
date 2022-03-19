import logging
logfmt = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S", format=logfmt)

import pandas as pd
import numpy as np
#access feature computers
from cmcl.features.extract_constituents import CompositionTable

#access transformers
from cmcl.features.extract_categories import DummyTable
from cmcl.data.index import ColumnGrouper

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
        #working original
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
        if self._ohedf is None or regen:
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
            self._compdf = feature.get()
        return self._compdf
    
    def mtmr(self):
        """get array of dscribe inorganic crystal properties"""
        print("matminer Not Implemented")

    def meg(self):
        """get array of MEGnet properties"""
        print("megnet Not Implemented")

@pd.api.extensions.register_dataframe_accessor("collect")
class CollectionAccessor():
    """
    convenience for imposing user-defined collections on columns

    collections are returned in the form of a pandas MultiIndex on the
    column labels

    define your own groups as a dictionary of form:
    segment_dict={"group1": ["col1", "coln"], "group2": ["col2"]}

    one column can be placed in multiple groups, but the MultiIndex
    will be nested

    then: CmclFrame.collect.by(segment_dict)

    presets include:
    - pervoskite site grouping (collect.abx)
    
    data categorizers are MultiIndex aware and will return categories
    for every grouping level

    Some Featurizers are MultiIndex aware and support returning
    features aggregated by groupings
    """
    def __init__(self, df):
        self._validate(df)
        #working original
        self._df = df
        
    @staticmethod
    def _validate(df):
        """
        verify df contains at least one series of measurements
        """
        pass
        
    def by(self, segments):
        collector = ColumnGrouper(self._df, segments)        
        return collector.get_groups()

    def abx(self):
        """
        default ColumnGrouper. groups Perovskite composition tables by
        constituent site.
        """
        segments = {"A":["MA", "FA", "Cs", "Rb", "K"],
                    "B":["Pb", "Sn", "Ge", "Ba", "Sr", "Ca", "Be", "Mg", "Si", "V", "Cr", "Mn", "Fe", "Ni", "Zn", "Pd", "Cd", "Hg"],
                    "X":["I", "Br", "Cl"]}
        return self.by(segments)

@pd.api.extensions.register_dataframe_accessor("cat")
class CategoryAccessor():
    """
    validate by summation. Check to see each row sums to a certain quantity

    aggregations are MultiIndex Aware
    """
    if not segment_sums:
        segment_sums = [1, 3, 8, 24]
    mixlog = categorizer.sum_groups()
    colgroups = categorizer.get_groups()
    #produce categorical variable
    mixing = mixlog.apply(lambda row: self._transcribe_mix(row), axis=1)
    mixing.name="mixing"
    #check groupsum
    vallog = list(self._check_groups(colgroups, segment_sums))
    retlist = [mixing]
    for series in vallog:
        retlist.append(series)
    return pd.DataFrame(retlist).T
    """
    also logs the validity of each individual group according to the
    summation of it's columns belonging to a list of permissible site
    fractions.
    """
    
@pd.api.extensions.register_dataframe_accessor("tf")
class TransformAccessor():
    """
    Conveniently define and retrieve transforms of tables

    when transform does not exist, it will be created.
    
    example:
    X.tf.pca()

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
