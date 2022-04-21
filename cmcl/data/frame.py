import logging
logfmt = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S", format=logfmt)

import pandas as pd

#feature computers
from cmcl.features._extract_constituents import CompositionTable

#metadata handling
from cmcl.data.index import ColumnGrouper
#Frame transformer might be movable to cmcl.data.index

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
