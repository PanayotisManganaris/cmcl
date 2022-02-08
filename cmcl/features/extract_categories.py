# might be prudent to make a new accessor for these catagorizers
# as most will work only on results of various featurizers

class SiteCat():
   """
   generate categorical columns based on site populations
   """
   def __init__(self):


def categorize_mix(df):
   """
   Take a perovskites dataframe's composition matrix, and generate a new Mixing column
   """
   A_cols = []
   B_cols = []
   X_cols = []
   for label in perovskite_site_members.values:
       if label[0] and label[0] in df:
           A_cols.append(label[0])
       if label[1] and label[1] in df:          
           B_cols.append(label[1])
       if label[2] and label[2] in df:
           X_cols.append(label[2])
   A_site_occup = df[A_cols]
   B_site_occup = df[B_cols]
   X_site_occup = df[X_cols]
   #if status is not exactly 1 in each row, append to mixtring and set row Mixing to mixstring
   A_site_stat = A_site_occup.notna().sum(axis=1)
   B_site_stat = B_site_occup.notna().sum(axis=1)
   X_site_stat = X_site_occup.notna().sum(axis=1)
   mixlog = pd.concat([A_site_stat, B_site_stat, X_site_stat], axis=1)

   def mixreader(row):
      mixstring = " & "
      stringlist=[]
      if row[0] != 1:
         stringlist.append("A")
      if row[1] != 1:
         stringlist.append("B")
      if row[2] != 1:
         stringlist.append("X")
      if stringlist:
         stringlist[-1] = stringlist[-1] + "-site"
      if not stringlist:
         stringlist.append("Pure")
      mixstring = mixstring.join(stringlist)
      return mixstring

   df.Mixing = mixlog.apply(lambda row: mixreader(row), axis=1)
     
