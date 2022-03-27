"""PandasColumnTransformer source originally by Everest Law https://github.com/openerror"""
from itertools import chain
from typing import *

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer

class FrameTransformer(BaseEstimator, TransformerMixin):
    """
    A wrapper around sklearn.column.ColumnTransformer facilitating the use of
    Scikit-Learn Transformers with all the benefits of pandas data frames in indexing
    and relational queries.
    
    example:
    df = FrameTransformer(StandardScaler()).fit_transform(df)
    """
    def __init__(self, transformers, **kwargs):
        """
        Initialize by creating ColumnTransformer object
        Args:
            transformers (list of length-3 tuples): (name, Transformer, target columns)
            kwargs: keyword arguments for sklearn.compose.ColumnTransformer

        in each tuple, "name" can be anything, but any choice of ["remainder",
        "default", "rem", "def", "drop", "pass", "exclude"] indicates that the
        columns specified in that section of the transformer pipeline should be
        treated by the ColumnTransformer's Transform-specific .remainder protocol
        """
        self.col_transformer = ColumnTransformer(transformers, **kwargs)
        self.transformed_col_names: List[str] = []

    def _get_col_names(self, X: pd.DataFrame):
        """
        Get names of transformed columns from a fitted self.col_transformer
        Args:
            X (pd.DataFrame): DataFrame to be fitted on
        Yields:
            Iterator[Iterable[str]]: column names corresponding to each transformer
        """
        for name, transformer, cols in self.col_transformer.transformers_:
            remainder_names = ["remainder", "default", "rem", "def", "drop", "pass", "exclude", "ignore"]
            if hasattr(transformer, "get_feature_names_out"):
                colnames = transformer.get_feature_names_out(cols)
                yield colnames
            elif name in remainder_names and self.col_transformer.remainder=="passthrough":
                yield X.columns[cols].tolist()
            elif name in remainder_names and self.col_transformer.remainder=="drop":
                continue
            else:
                yield cols        

    def fit(self, X: pd.DataFrame, y: Any=None):
        """
        Fit ColumnTransformer, and obtain names of transformed columns in advance
        Args:
            X (pd.DataFrame): DataFrame to fit the transformer to
            y (Index or MultiIndex object, optional): Compliance with fit API. Defaults to None. 
        """
        assert isinstance(X, pd.DataFrame)
        self.col_transformer = self.col_transformer.fit(X, y)
        self.transformed_col_names = list(chain.from_iterable(self._get_col_names(X)))
        return self


    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform a new DataFrame using fitted self.col_transformer
        Args:
            X (pd.DataFrame): DataFrame to be transformed
        Returns:
            pd.DataFrame: DataFrame transformed by self.col_transformer
        """
        assert isinstance(X, pd.DataFrame)
        try: #literally just here to catch manifold.TSNE
            transformed_X = self.col_transformer.transform(X)
        except TypeError:
            transformed_X = self.col_transformer.fit_transform(X)
        if isinstance(transformed_X, np.ndarray):
            return pd.DataFrame(transformed_X, index=X.index, 
            columns=self.transformed_col_names)
        else:
            return pd.DataFrame.sparse.from_spmatrix(
                transformed_X, index=X.index,
                columns=self.transformed_col_names
            )
