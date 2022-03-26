import logging
logfmt = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S", format=logfmt)

import pandas as pd
import numpy as np
#metadata handling
from cmcl.data.index import ColumnGrouper, ColumnHandler

#feature computers
from cmcl.features.extract_constituents import CompositionTable

#access models
from cmcl.models.RFR import RFR


# feature accessors should saveable in some way for future use/reporting

# model accessors perhaps can be saved, but are often not.
# expensive models should be saved, though...

@pd.api.extensions.register_dataframe_accessor("ft")
class FeatureAccessor():
    """
    Conveniently retrieve feature tables.
    when table does not exist, it will be created.

    basic chemical descriptors:
    composition_tbl = CmclFrame.ft.comp()
    prop_tbl = CmclFrame.ft.mrg()
    
    pymatgen descriptors:
    matminer_tbl = CmclFrame.ft.mtmr()

    MEGnet elemental embeddings:
    meg_tbl = CmclFrame.meg()
    """

    def __init__(self, df):
        self._validate(df)
        #working original
        self._df = df
        self._ohedf = None
        self._compdf = None
        self._mgrdf = None
        
    @staticmethod
    def _validate(df):
        """
        verify df contains
        a series of Formula (in index or body)
        at least one series of measurements
        """
        pass
        
    def base(self):
        return self._df
        
    def comp(self, regen=False):
        """
        Default call accesses or creates composition table.
        call with regen=True to regenerate existing composition table
        """
        if self._compdf is None or regen:
            feature = CompositionTable(self._df)
            self._compdf = feature.get()
        return self._compdf
    
    def mrg(self):
        """
        apply to a composition table.
        Get array of elemental properties currently being considered
        by Mannodi Research Group for every compound present as
        non-NaN/nonzero entry in composition table.
        """
        pass

    def mtmr(self):
        """as above, get array of dscribe inorganic crystal properties"""
        print("matminer Not Implemented")

    def meg(self):
        """as above, get array of MEGnet elemental embeddings"""
        print("megnet Not Implemented")

@pd.api.extensions.register_dataframe_accessor("tf")
class TransformAccessor():
    """
    Define and retrieve transforms of tables. When transform does not
    exist, it will be created.
    
    Supports generic Scikit-Learn contextual transforms using the
    df.tf.pipe() method. This simply inserts a thin wrapper between
    the df.pipe() method and functions that act on Dataframes,
    returning multidimensional arrays (like Scikit-Learn
    Transformers).

    example:
    X = X.tf.pipe(StandardScaler().fit_transform)
    Xpca = X.tf.pca()

    In this way, transforms stay fully contextualized by the dataframe
    indices
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
    Generate models of tables based on other tables
    
    automates the construction of a sklearn compliant pipeline. This includes:
    - pandas index manipulation such that results are appropriately labeled
    - 0.8train/0.2test split (default if not specified by the user)
    - labeling records with their respective partition
    - application of estimator
    
    An accessed table will have models created for it. models are
    stored with the accessor instance, predictions are not.

    Y.model.pipe(RandomForestRegressor.fit(X, Y).predict(X)))
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
        
    def by(self, segments, name_tuple=None, dontdrop=True):
        """
        set dontdrop to False to exclude any column not specified in
        segments from the new columns index

        optionally pass a two-tuple of names for 1. the groups and
        2. the members
        """
        collector = ColumnGrouper(self._df, segments, dontdrop)
        return collector.get_groups(name_tuple)

    def abx(self):
        """
        default ColumnGrouper. groups Perovskite composition tables by
        constituent site.
        """
        segments = {"A":["MA", "FA", "Cs", "Rb", "K"],
                    "B":["Pb", "Sn", "Ge", "Ba", "Sr", "Ca", "Be", "Mg", "Si", "V", "Cr", "Mn", "Fe", "Ni", "Zn", "Pd", "Cd", "Hg"],
                    "X":["I", "Br", "Cl"]}
        return self.by(segments, ("site","element"))
