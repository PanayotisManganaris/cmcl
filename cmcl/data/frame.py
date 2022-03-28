import logging
logfmt = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S", format=logfmt)

import pandas as pd
import numpy as np

#feature computers
from cmcl.features.extract_constituents import CompositionTable

#scikit accessor implementation
import json
import re
from sklearn.compose import make_column_transformer
from sklearn.compose import make_column_selector
#metadata handling
from cmcl.data.index import ColumnGrouper
#Frame transformer might be movable to cmcl.data.index
from cmcl.compatsk._FrameTransformer import FrameTransformer

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

@pd.api.extensions.register_dataframe_accessor("sk")
class SciKitAccessor():
    """
    Define and retrieve transforms of tables. When transform does not
    exist, it will be created.
    
    - df.sk.transform() method supports generic Scikit-Learn compliant
      contextual transforms to a dataframe
    
    - df.sk.model() method supports applying SciKit-Learn compliant estimators

    example:
    X = X.tf.pipe(StandardScaler().fit_transform)
    Xpca = X.tf.pca()

    In this way, transforms stay fully contextualized by the dataframe
    indices
    """
    def __init__(self, df):
        """
        sklearn transformers are very careful about the types they work on.
        object columns should definitely contain strings.
        numeric columns should definitely contain numbers or NaN

        DataFrame column labels absolutely must be strings
        Column names are preserved for restructuring
        """
        self._df = pd.concat(
            [df.select_dtypes(exclude=object).apply(pd.to_numeric, errors="coerce"),
             df.select_dtypes(include=object).applymap(lambda x: str(x))],
             axis=1
        )
        self._col_names = df.columns.names
        self._df = self._serialize_columns(self._df)
    
    @staticmethod
    def _serialize_columns(df: pd.DataFrame):
        """ensure pandas columns are always a series of strings, even if MultiIndexed"""
        new_col_labels = []
        for label in df.columns:
            new_col_labels.append(json.dumps(label))
        df.columns=new_col_labels
        return df

    @staticmethod
    def _gen_transform_tuple(num_transformer=None, obj_transformer=None):
        """generate a 1or2 tuple of 2-tuples"""
        if num_transformer and obj_transformer:        
            ct_list = [(num_transformer,
                        make_column_selector(dtype_include=np.number)),
                       (obj_transformer,
                        make_column_selector(dtype_include=object))]
        elif num_transformer:
            ct_list = [(num_transformer,
                        make_column_selector(dtype_include=np.number))]
        elif obj_transformer:
            ct_list = [(obj_transformer,
                        make_column_selector(dtype_include=object))]
        else:
            raise ValueError("Specify at least one compliant transformer")
        return ct_list

    @staticmethod
    def _deserialize_columns(df: pd.DataFrame):
        """
        reconstruct tuple from earlier json.dumps prefixing
        the highest level label names as needed
        """
        def prefix_last_label(prefix_label):
            if prefix_label[0] == "[":
                return prefix_label
            else:
                ll = re.split("__", prefix_label)
                sll = list(re.split(",", ll[-1]))
                lll = sll[-1]
                lll = lll.insert(1, ll[:-1]+"__")
                last = "".join(lll)
                sll[-1] = last
                return "".join(sll)
        final_col_labels = []
        for dump_label in df.columns:
            ready_label = prefix_last_label(dump_label)
            final_col_labels.append(tuple(json.loads(ready_label)))
        df.columns = pd.MultiIndex.from_tuples(final_col_labels)
        return df

    def _fit(self, num_transformer, obj_transformer):
        ct = make_column_transformer(*self._gen_transform_tuple(num_transformer,
                                                                obj_transformer))
        # it'd be nice to shorten the generated names here
        transformer = FrameTransformer(ct.transformers)
        self.FT = transformer.fit(self._df)
        for ttpl in self.FT.transformers.transformers:
            yield ttpl[1]

    def fit(self, num_transformer=None, obj_transformer=None):
        """
        Pass transformers to apply to numeric (arg1) and non numeric
        (arg2) columns of DataFrame

        Valid estimators include FeatureUnions and Pipelines ending in
        a transformer and any custom sklearn compliant estimators

        not sure if it will work with transformers that expect to work
        with methods of DataFrames (test df.dt?)
        
        It returns a tuple of transformers used by the underlying
        ColumnTransformers which can be used as any fitted estimator.

        example:
        df.sk.fit(make_union(StandardScaler(), MinMaxScaler()), OneHotEncoder())

        Note:
        it's still a column_transformer underneath so transductive
        estimators will raise TypeError: transform method not implemented
        """
        transgen = self._fit(num_transformer=num_transformer,
                             obj_transformer=obj_transformer)
        return tuple(transgen) #eh, pretty convenient but could be cleaner
        
    def transform(self, FT):
        """
        takes a FrameTransformer fit on another dataframe

        Assumes FrameTransformer has been fit previously.
        """
        #ideally check that the damned thing's been fit
        df = FT.transform(self._df)
        df = self._deserialize_columns(df)
        df.columns.names = self._col_names
        return df

    def fit_transform(self, num_transformer=None, obj_transformer=None):
        self.fit(num_transformer=num_transformer,
                 obj_transformer=obj_transformer)
        return self.transform(self.FT)

    def target(self, y):
        """
        supply a target dataframe to the accessor in order to perform
        supervised transformations
        """
        pass

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
