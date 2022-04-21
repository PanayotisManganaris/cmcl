import logging
logfmt = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S", format=logfmt)

from functools import partial
import pandas as pd

class Categories():
    """
    Container class holding tools for simplifying the generation of
    categorical columns based on the values of data frames.
    
    Ideal for producing scatter plot labels.
    """
    @staticmethod
    def logif(df, condition, default=None, catstring="_&_"):
        """
        produce a series of categorical strings based on the numerical
        contents of a dataframe, its column names, and some condition
        described as a function returning True. Optionally provide a
        default label for records not meeting condition in any column.

        example:
        df.pipe(Categories.logif, condition=lambda x: x>1, default="pure")
        """
        def _logif(row, catstring):
            stringlist=[]
            for entry, label in zip(row, df.columns):
                if condition(entry):
                    stringlist.append(label)
            if not stringlist:
                stringlist.append(str(default))
            catstring = catstring.join(stringlist)
            return catstring
        _logif = partial(_logif, catstring=catstring)
        catseries = df.apply(_logif, axis=1)
        return catseries
