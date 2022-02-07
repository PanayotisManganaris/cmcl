import matplotlib.pyplot as plt

#  ML Parity Plots ##
fig, ( [ax1, ax2], [ax3, ax4] ) = plt.subplots( nrows=2, ncols=2, figsize=(8,8) )
fig.text(0.5, 0.03, 'DFT Calculation', ha='center', fontsize=32)
fig.text(0.02, 0.5, 'ML Prediction', va='center', rotation='vertical', fontsize=32)
plt.subplots_adjust(left=0.14, bottom=0.14, right=0.97, top=0.92, wspace=0.30, hspace=0.40)
plt.rc('font', family='Arial narrow')

Prop_train_temp = copy.deepcopy(Prop_train_latt_fl)
Pred_train_temp = copy.deepcopy(Pred_train_latt_fl)
Prop_test_temp  = copy.deepcopy(Prop_test_latt_fl)
Pred_test_temp  = copy.deepcopy(Pred_test_latt_fl)
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

Prop_train_temp = copy.deepcopy(Prop_train_decomp_fl)
Pred_train_temp = copy.deepcopy(Pred_train_decomp_fl)
Prop_test_temp  = copy.deepcopy(Prop_test_decomp_fl)
Pred_test_temp  = copy.deepcopy(Pred_test_decomp_fl)
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

Prop_train_temp = copy.deepcopy(Prop_train_gap_fl)
Pred_train_temp = copy.deepcopy(Pred_train_gap_fl)
Prop_test_temp  = copy.deepcopy(Prop_test_gap_fl)
Pred_test_temp  = copy.deepcopy(Pred_test_gap_fl)
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

Prop_train_temp = copy.deepcopy(Prop_train_fom_fl)
Pred_train_temp = copy.deepcopy(Pred_train_fom_fl)
Prop_test_temp  = copy.deepcopy(Prop_test_fom_fl)
Pred_test_temp  = copy.deepcopy(Pred_test_fom_fl)
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

plt.show()
#plt.savefig('plot_PBE_RFR_models.pdf', dpi=450)
