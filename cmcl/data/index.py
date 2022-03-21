import pandas as pd

class ColumnGrouper():
    """
    Group column labels into a multi-index in a convenient way

    pd.MultiIndex doesn't already provide an easy way to just define a
    MultiIndex from dictionary {groups: [columns]} likely for good
    reason.

    This fills that hole because imposing structure on dimensions is
    still useful anyway.
    
    instantiate using an unpacked dictionary of lists

    {"category1": ["label1", "label2"],
    "category2": ["label3", "label4"]}

    Note, the table to be MultiIndexed need not either
    1. contain All the labels that define the column groups
    2. contain ONLY labels within a column group

    further, a column label need not be exclusive to one group.

    However, ColumnGrouper stops short of fully exposing reindexing
    functionality. Groups cannot be used to add columns to a data
    frame.

    if the same thing need be done for row labels, just transpose the
    dataframe
    """
    def __init__(self, df, segments, dontdrop=True):
        self.df = df
        self.segments = segments
        self.dontdrop = dontdrop
        
    def _lookup(self, label):
        anygroup = []
        for k,l in self.segments.items():
            anygroup += l
            if label in l:
                yield (k, label)
        if label not in anygroup and self.dontdrop:
            yield ("undef", label)

    def get_groups(self, name_tuple=None):
        """
        returns the dataframe with a MultiIndex
        """
        column_tuples = []
        for column_tuplator in map(self._lookup, self.df.columns):
            column_tuples += list(column_tuplator)
        mi = pd.MultiIndex.from_tuples(column_tuples,
                                       names=name_tuple)
        mi_ordered, _ = mi.sortlevel(level=0)
        self.df = self.df.reindex(mi_ordered.get_level_values(1), axis=1, copy=False)
        self.df.columns=mi_ordered
        return self.df
