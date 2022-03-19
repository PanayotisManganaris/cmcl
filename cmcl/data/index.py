"""extending pandas indexing with convenient multi-index generation
and support for data validation by grouping"""

import pandas as pd
import numpy as np

class ColumnGrouper():
    """
    Group column labels into a multi-index in a convenient way

    For some reason pd.MultiIndex doesn't already provide an easy way
    to just define a multiindex from dictionary {groups: [columns]} 

    this fills that hole. Additionally, it is also equipped to return
    either a membership summary OR the groupings themselves.

    The membership summary can be used for custom group validations.

    instantiate using an unpacked dictionary of lists

    {"category1": ["label1", "label2"],
    "category2": ["label3", "label4"]}

    Note, the table to be multiindexed by column does not need to contain all the labels that define a category
    allowing dictionaries to be reused across tables

    if the same thing needs to be done for row labels, just transpose
    the dataframe
    """
    def __init__(self, df, segments):
        self.df = df
        self.segments = segments
        
    def _lookup(self, label):
        for k,l in self.segments.items():
            if label in l:
                return k
        return "undef"

    def get_groups(self, name_tuple=None):
        """
        returns the dataframe with a MultiIndex
        """
        ordered_group_keys = list(map(self._lookup, self.df.columns))
        mi = pd.MultiIndex.from_arrays([ordered_group_keys, self.df.columns],
                                       names=name_tuple)
        mi_ordered, _ = mi.sortlevel(level=0)
        self.df = self.df.reindex(mi_ordered.get_level_values(1), axis=1, copy=False)
        self.df.columns=mi_ordered
        return self.df

class GroupChecker():
    """
    works with a column-grouped dataframe to ensure each group meets a
    set of custom conditions
    """
    def _count_members(self):
        if not self.df.isnull().values.any():
            print(f"WARNING: dataframe contains no null values! LabelGrouper.sum_groups() may not perform as expected.")
            self.segment_count = pd.DataFrame([], columns=[item[0] for item in self.items])
        for col, segment in enumerate([item[1] for item in self.items]):
            idx = self._present_index(segment)
            self.segment_count.iloc[:, col] = self.df[idx].notna().sum(axis=1)

    def sum_groups(self):
        """
        returns segment_count -- a row-wise count of non-NaN values per group
        """
        self._count_members()
        return self.segment_count
