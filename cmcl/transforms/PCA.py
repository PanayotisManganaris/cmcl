from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

class PCA():
    """dataframe accessor PCA transformer"""
    def __init__(self):
        pass

# #preprocess -- mainly scale everything
# pdf_pse = pd.DataFrame(StandardScaler().fit_transform(perovs_df.iloc[:,61:67].dropna()),
#                        index = perovs_df.iloc[:,61:67].dropna().index, columns = perovs_df.iloc[:,61:67].columns)
# pse_label = pdf_pse.columns
# pse_label = pse_label.values
# pse_label
# 
# #train transformer
# pcaxis = PCA(n_components = min(pdf_pse.shape), svd_solver = 'full')
# 
# #name components
# PCs = ['pc_%i' % i for i in range(pcaxis.n_components)]
# 
# #create model
# pdf_pcmodel = pd.DataFrame(pcaxis.fit_transform(pdf_pse), index=pdf_pse.index, columns=PCs)
# 
# #plot scree
# scree = pcaxis.explained_variance_ratio_
# screefig = plt.figure(figsize = [15,5])
# plt.semilogy(PCs, scree, '*')
# plt.title('Proportion of Variance explained by Principal Components')
# plt.ylabel('Fraction of Variance')
# plt.show()
# 
# #plotting with matplotlib
# #%matplotlib inline
# #Call the function. Use only the 2 PCs at a time.
# fig, (ax1, ax2) = plt.subplots(2,1, figsize=(9,18))
# 
# fig.canvas.mpl_connect("motion_notify_event", hover) #not working yet...
# 
# plane01 = biplot([0,1], pdf_pcmodel, pcaxis.components_, dim_labels=pse_label, ax=ax1, N_labels=perovs_df.iloc[62])
# plane02 = biplot([0,2], pdf_pcmodel, pcaxis.components_, dim_labels=pse_label, ax=ax2)
# plt.show()
