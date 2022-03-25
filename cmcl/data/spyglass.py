#cmcl's "high-level plotting api"
#immature, future versions of this concept will be implemented in a standalone library
#for more versatility and improved pandas integration

import logging
logfmt = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S", format=logfmt)

import pandas as pd
import matplotlib.pyplot as plt
import mplcursors

class PariPlot():
    """
    a plot object specifically for assessing the acuity of regressions.
    This should be accessed through the pandas plotting api.

    spyglass.PariPlot(df, scatter, **kwargs) or
    df.plot(backend="spyglass.PariPlot") or set global option or
    df.plot.parity()

    provides methods to:
     - generate and return a curated plot template
     - display plot using mplcursors interactively with qtcanvas, etc
    """
    def __init__(self):
        pass

    def makeplot():
        pass

    def live():
        """setup mpl connection for the data and axes"""
        pass

def biplot(components, PCs,
           transform_matrix,
           dim_labels=None,
           N_labels=[],
           ax=None,
           cbar_kw={},
           cbarlabel="",
           **kwargs):
    """
    modify or create and return axis containing cross-section of pca space as
    scatter plot with projection of orignal dimensions onto the plane of major
    variance

    Parameters:
    ----------    
    components
    2-length list of integers from 0 to D-1. Selects 2 components to be scatter
    plotted against each other.
    PCs
    D-colummn DataFrame where each column is a principal component.
    transform_matrix
    DxD array of component weights summarizing the contribution of each dimension to
    each PC. Meant for use with PCA by sklearn.Decomposition.PCA.components_
    dim_labels
    D-length list of dimension labels corresponding the axes of the original
    data-space transformed in the PCA.
    N_labels
    Either:
    1. N-length pandas Series of unique labels to individually annotate each datapoint 
       Optionally, use cbar* args to control continuous coloration. String labels will be
       white.
    2. N-length list of nonunique labels to be annotate clusters of datapoints
       use with cbar* args to control descrete coloration
    3. None. Datapoints will be white and noninteractive


    Utility Args:
    -------------
    ax
    A `matplotlib.axes.Axes` instance on which the principal coordinates are scattered.
    If not provided, use current axes or create a new one.  Optional.
    cbar_kw
    A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
    The label for the colorbar.  Optional.
    ,**kwargs
    All other arguments are forwarded to `scatter`.

    transform_matrix is necssary for quantifying the contribution of each dimension
    to the principal components being plotted
    """
    if not ax:
        ax = plt.gca()
    #Number of dimensions to biplot
    n = transform_matrix.shape[0]
    #plot the plane of major variance
    xs = PCs.iloc[:,components[0]]
    ys = PCs.iloc[:,components[1]]
    scalex = 1.0/(xs.max() - xs.min())
    scaley = 1.0/(ys.max() - ys.min())
    N_labels = np.array(N_labels)
    unique = np.unique(N_labels)
    #wip:
    if (N_labels.size > unique.size) & (unique.size > 1): #color and annotate coords by discrete scale, disp scale
        #TODO if discrete scale consists of unique strings color discrete strings uniquely + label
        scatterplane = ax.scatter(xs * scalex, ys * scaley, c = N_labels, **kwargs)
        cbar = ax.figure.colorbar(scatterplane, ax=ax, **cbar_kw)
        cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")
        for key, value in np.arange(5):
            annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="w"),
                                arrowprops=dict(arrowstyle="->"))
            annot.set_visible(False)
    elif (N_labels.size == unique.size) & (unique.size > 1): #color and annotate coords by continuous scale, disp scale
        #TODO if continuous scale consists of unique strings label without color
        #if numbers, make and apply colorscale as well as label
        scatterplane = ax.scatter(xs * scalex, ys * scaley, c = N_labels, **kwargs)
        cbar = ax.figure.colorbar(scatterplane, ax=ax, **cbar_kw)
        cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")
        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)
    elif N_labels.size == 0: #quick view, no scale
        scatterplane = ax.scatter(xs * scalex, ys * scaley, c = "white", **kwargs)
    else:
        raise ValueError("N_labels badly argued. see biplot docstring")
    #plot and label projection of original dimensions on plane
    slice1 = transform_matrix[components[0]]
    slice2 = transform_matrix[components[1]]
    proj_slice_transposed = np.stack([slice1, slice2], axis=1)
    xs_weight = proj_slice_transposed[:,0]
    ys_weight = proj_slice_transposed[:,1]
    for i in range(n):
        ax.arrow(0, 0, xs_weight[i], ys_weight[i], color = 'r', alpha = 0.5)
        if dim_labels is None:
            ax.text(xs_weight[i] * 1.2, ys_weight[i] * 1.2, "Var"+str(i+1), color = 'g', ha = 'center', va = 'center')
        else:
            ax.text(xs_weight[i] * 1.2, ys_weight[i] * 1.2, dim_labels[i], color = 'g', ha = 'center', va = 'center')
    ax.set_xlabel("PC{}".format(components[0]))
    ax.set_ylabel("PC{}".format(components[1]))
    ax.grid()

    return ax
    
fig, ( [ax1, ax2], [ax3, ax4] ) = plt.subplots( nrows=2, ncols=2, figsize=(8,8) )
fig.text(0.5, 0.03, 'DFT Calculation', ha='center', fontsize=32)
fig.text(0.02, 0.5, 'ML Prediction', va='center', rotation='vertical', fontsize=32)
plt.subplots_adjust(left=0.14, bottom=0.14, right=0.97, top=0.92, wspace=0.30, hspace=0.40)
plt.rc('font', family='Arial narrow')

a = [-175,0,125]
b = [-175,0,125]
ax1.plot(b, a, c='k', ls='-')
ax1.xaxis.set_tick_params(labelsize=20)
ax1.yaxis.set_tick_params(labelsize=20)
ax1.scatter(Prop_train_temp[:], Pred_train_temp[:], c='orangered', marker='s', s=60, edgecolors='dimgrey', alpha=0.9, label='Training')
ax1.scatter(Prop_test_temp[:], Pred_test_temp[:], c='lawngreen', marker='s', s=60, edgecolors='dimgrey', alpha=0.9, label='Test')
te = '%.2f' % rmse_test_latt
tr = '%.2f' % rmse_train_latt
ax1.text(5.96, 5.48, 'Test_rmse = ' + te + ' $\AA$', c='navy', fontsize=16)
ax1.text(5.93, 5.28, 'Train_rmse = ' + tr + ' $\AA$', c='navy', fontsize=16)
ax1.set_ylim([5.1, 7.1])
ax1.set_xlim([5.1, 7.1])
ax1.set_xticks([5.5, 6.0, 6.5, 7.0])
ax1.set_yticks([5.5, 6.0, 6.5, 7.0])
ax1.set_title('Lattice Constant ($\AA$)', c='k', fontsize=20, pad=12)
ax1.legend(loc='upper left',ncol=1, frameon=True, prop={'family':'Arial narrow','size':12})

ax2.plot(b, a, c='k', ls='-')
ax2.xaxis.set_tick_params(labelsize=20)
ax2.yaxis.set_tick_params(labelsize=20)
ax2.scatter(Prop_train_temp[:], Pred_train_temp[:], c='orangered', marker='s', s=60, edgecolors='dimgrey', alpha=0.9, label='Training')
ax2.scatter(Prop_test_temp[:], Pred_test_temp[:], c='lawngreen', marker='s', s=60, edgecolors='dimgrey', alpha=0.9, label='Test')
te = '%.2f' % rmse_test_decomp
tr = '%.2f' % rmse_train_decomp
ax2.text(0.58, -0.65, 'Test_rmse = ' + te + ' eV', c='navy', fontsize=16)
ax2.text(0.45, -1.19, 'Train_rmse = ' + tr + ' eV', c='navy', fontsize=16)
ax2.set_ylim([-1.7, 3.8])
ax2.set_xlim([-1.7, 3.8])
ax2.set_xticks([-1.0, 0.0, 1.0, 2.0, 3.0])
ax2.set_yticks([-1.0, 0.0, 1.0, 2.0, 3.0])
ax2.set_title('Decomposition Energy (eV)', c='k', fontsize=20, pad=12)
#ax2.legend(loc='upper left',ncol=1, frameon=True, prop={'family':'Arial narrow','size':12})

ax3.plot(b, a, c='k', ls='-')
ax3.xaxis.set_tick_params(labelsize=20)
ax3.yaxis.set_tick_params(labelsize=20)
ax3.scatter(Prop_train_temp[:], Pred_train_temp[:], c='orangered', marker='s', s=60, edgecolors='dimgrey', alpha=0.9, label='Training')
ax3.scatter(Prop_test_temp[:], Pred_test_temp[:], c='lawngreen', marker='s', s=60, edgecolors='dimgrey', alpha=0.9, label='Test')
te = '%.2f' % rmse_test_gap
tr = '%.2f' % rmse_train_gap
ax3.text(2.50, 1.10, 'Test_rmse = ' + te + ' eV', c='navy', fontsize=16)
ax3.text(2.36, 0.52, 'Train_rmse = ' + tr + ' eV', c='navy', fontsize=16)
ax3.set_ylim([0.0, 6.0])
ax3.set_xlim([0.0, 6.0])
ax3.set_xticks([1, 2, 3, 4, 5])
ax3.set_yticks([1, 2, 3, 4, 5])
ax3.set_title('Band Gap (eV)', c='k', fontsize=20, pad=12)
#ax3.legend(loc='upper left',ncol=1, frameon=True, prop={'family':'Arial narrow','size':12})

ax4.plot(b, a, c='k', ls='-')
ax4.xaxis.set_tick_params(labelsize=20)
ax4.yaxis.set_tick_params(labelsize=20)
ax4.scatter(Prop_train_temp[:], Pred_train_temp[:], c='orangered', marker='s', s=60, edgecolors='dimgrey', alpha=0.9, label='Training')
ax4.scatter(Prop_test_temp[:], Pred_test_temp[:], c='lawngreen', marker='s', s=60, edgecolors='dimgrey', alpha=0.9, label='Test')
te = '%.2f' % rmse_test_fom
tr = '%.2f' % rmse_train_fom
ax4.text(4.33, 3.15, 'Test_rmse = ' + te, c='navy', fontsize=16)
ax4.text(4.23, 2.8, 'Train_rmse = ' + tr, c='navy', fontsize=16)
ax4.set_ylim([2.5, 6.2])
ax4.set_xlim([2.5, 6.2])
ax4.set_xticks([3, 4, 5, 6])
ax4.set_yticks([3, 4, 5, 6])
ax4.set_title('Figure of Merit (log$_{10}$)', c='k', fontsize=20, pad=12)
#ax4.legend(loc='upper left',ncol=1, frameon=True, prop={'family':'Arial narrow','size':12})

#plt.show()
#plt.savefig('plot_PBE_RFR_models.pdf', dpi=450)
