import logging
logfmt = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S", format=logfmt)

import pandas as pd
import numpy as np

class DummyTable():
    def __init__(self, df):
        self._validate(df)
        self.df = df
        self._original = df.columns.values

    @staticmethod
    def _validate(df):
        """
        id cols with lists inside or dicts inside
        warn
        """
        for nncol_name in df.select_dtypes(include=["object"]).columns:
            el_not_str = mannodi_df["PBE_bgType"].apply(lambda x: not (x is None or isinstance(x, (str, np.NaN, pd.NA))))
            log = f"""Records contain non-numeric, non-string, non-NoneType, dtypes
            {df.loc[el_not_str, nncol_name]}"""
            if el_not_str.any():
                logging.critical(log)
                raise ValueError("data is not suitable for one-hot encoding. see log")

    def _conditional_casefold(entry):
        if isinstance(entry, str):
            return entry.casefold()
        else:
            return entry

    def make(self):
        """
        one-hot-encode categorical variables in given df. (Not
        including Formula column).
        
        Convenience for using catagorical variables in models.

        wishlist: control prefixing dummy cols
        """
        normidx = list(map(self._conditional_casefold, df.columns))
        validx = ["Formula".casefold() not in label for label in normidx]
        #make in one swoop
        self.df = pd.get_dummies(self.df.loc[:, validx])
        #get indices
        updated = self.df.columns.values
        is_not_original_content = np.vectorize(lambda x: x not in self._original)
        ohe_cols_idx = is_not_original_content(updated)
        ohe_cols = updated[ohe_cols_idx]
        return self.df[ohe_cols]

class LabelGrouper():
   """
   groups values in a dataframe by operating on userdefined groups of labels

   equipped to return either a membership summary OR the groupings themselves.

   instantiate using an unpacked dictionary of lists

   {"category1": ["label1", "label2"],
    "category2": ["label3", "label4"]}

   or pass categories as kwargs to the constructor

   Note, the table to be classified does not need to contain all the labels that define a category
   allowing dictionaries to be reused across tables
   """
   def __init__(self, df, **segments):
      self._df = df
      self.segments = {}
      for k, v in segments.items(): #not sure if this is necessary in this case.... kwargs are dict'ed invisibly?
         self.segments[k] = v
      #ensure preserved orders
      self.items = self.segments.items()
      
   def _present_index(self, segment):
      idx = []
      for label in segment:
         if label and label in self._df:
            idx.append(label)
      return idx
   
   def _count_members(self):
      #currently fixed to column groupings
      #eventually try inferring axis from label's presence in index/columns
      if not self._df.isnull().values.any():
          print(f"WARNING: dataframe contains no null values! LabelGrouper.sum_groups() may not perform as expected.")
      self.segment_count = pd.DataFrame([], columns=[item[0] for item in self.items])
      for col, segment in enumerate([item[1] for item in self.items]):
         idx = self._present_index(segment)
         self.segment_count.iloc[:, col] = self._df[idx].notna().sum(axis=1)

   def _save_groups(self):
      for col, segment in enumerate([item[1] for item in self.items]):
         idx = self._present_index(segment)
         yield self._df[idx]

   def sum_groups(self):
      """
      returns segment_count -- a row-wise count of non-NaN values per group
      """
      self._count_members()
      return self.segment_count

   def get_groups(self):
      """
      returns the groups themselves as a tuple
      """
      return tuple(self._save_groups())
