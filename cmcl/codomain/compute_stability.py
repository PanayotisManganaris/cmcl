import numpy as np
import pandas as pd
import copy
import os
from cmcl import formula2dict

from typing import Union, Any, Literal

# when adding reference pages, just put the functionals next to each other
# the rest should be automatic
sheets = ['AX_HSE', 'BX2_HSE', 'AX_PBE', 'BX2_PBE']
# reference energies of decomposition phases currently supplied as
# pairs of worksheets. Need a DB-focused solution.
# idea: secret methods generate reference info as needed with atomate+update mrg db
# secret methods update cmcl db from mrg db
# cmcl db is distributed with cmcl pkg
loaded_refs = pd.read_excel(os.path.expanduser('~/src/cmcl/cmcl/db/ref_data.xlsx'),
                            sheet_name=sheets,
                            engine='openpyxl',
                            usecols="A,C", index_col='sys')

# stick sheet dfs together
lktpl, _ = zip(*loaded_refs.items())
refdf_dict = {}
for ktpl in zip(*[iter(lktpl)] * 2):
    functional = ktpl[-1].split('_')[-1] # PBE, HSE, etc
    rfsgrp = [loaded_refs[k] for k in ktpl]
    refdf_dict[functional] = pd.concat(rfsgrp, axis=0)

# define list for element space
A_element = ['K', 'Rb', 'Cs', 'MA', 'FA']
B_element = ['Ca', 'Sr', 'Ba', 'Ge', 'Sn', 'Pb']
X_element = ['Cl', 'Br', 'I']

# use structure subclasses to perform decomposition pathway determination

#Temp
def element_exist_list(formula:str)->tuple[list,list,list]:
    """
    args:
    formula string
    returns:
    0. list counting elements involved at each site
    1. list of elements
    2. list of amounts of each element
    """
    fdict = formula2dict(formula)
    constituents, constituents_frac = zip(*fdict.items())

    reps_per_site = [0, 0, 0]
    reps_per_site[0] += sum(
        [1 for c in constituents if c in A_element]
    )
    reps_per_site[1] += sum(
        [1 for c in constituents if c in B_element]
    )
    reps_per_site[2] += sum(
        [1 for c in constituents if c in X_element]
    )
    return reps_per_site, constituents, constituents_frac

#Temp: 
def mixing_ana(reps_per_site:list[int])->str:
    """
    mix classifier
    args:
    3 element list counting number of unique constituents represented
    for the corresponding A,B, and X site
    returns:
    mix classification
    """
    if reps_per_site == [1, 1, 1]:
        mixing = 'Pure'
    #otherwise, looks for the first bigger number, might misclassify
    #multi-site alloys
    elif reps_per_site[1:] == [1, 1] and reps_per_site[0] >= 1:
        mixing = 'Amix'
    elif reps_per_site[0:2] == [1, 1] and reps_per_site[2] >= 1:
        mixing = 'Xmix'
    elif reps_per_site[0::2] == [1, 1] and reps_per_site[1] >= 1:
        mixing = 'Bmix'
    else:
        raise NotImplementedError("Only Cardinal Mixing Considered")
        
    return mixing

def decomp_phase_ext(element_tem, constituents, constituent_frac, mix):
    """
    identify possible decomposition outcomes
    args:
    outputs of mixing_ana
    return:
    tuple of
    0. decomposition phases list
    1. decomposition phases fraction
    """
    # I don't understand any of this -- Panos
    if mix == 'Pure':
        decomp_phase = [constituents[0] + constituents[2], constituents[1] + constituents[2] + '2']
        decomp_phase_frac = [1, 1]
    elif mix == 'Amix':
        A_num = element_tem[0]
        A_decomp = [constituents[x] + constituents[-1] for x in range(A_num)]
        decomp_phase = A_decomp + [constituents[-2] + constituents[-1] + '2']
        n_element = len(constituent_frac)
        decomp_phase_frac = constituent_frac[0:n_element - 1]
    elif mix == 'Bmix':
        B_num = element_tem[1]
        B_decomp = [constituents[x + 1] + constituents[-1] + '2' for x in range(B_num)]
        decomp_phase = [constituents[0] + constituents[-1]] + B_decomp
        n_element = len(constituent_frac)
        decomp_phase_frac = constituent_frac[0:n_element - 1]
    elif mix == 'Xmix':
        X_num = element_tem[2]
        A_decomp = [constituents[0] + constituents[-2 + x] for x in range(X_num)]
        B_decomp = [constituents[1] + constituents[-2 + x] + '2' for x in range(X_num)]
        decomp_phase = A_decomp + B_decomp
        decomp_phase_frac = [x / 3 for x in constituent_frac[2:]] + [y / 3 for y in constituent_frac[2:]]
    return decomp_phase, decomp_phase_frac

def entropy_calcs(decomp_frac:np.ndarray):
    """
    compute entropy of mixing from 
    k_B and T_ref can be set externally
    """
    k_B = 8.617e-5
    T_ref = 300
    mixing_entropy = k_B * T_ref * np.dot(decomp_frac,
                                          np.log(decomp_frac))
    return mixing_entropy

def compute_decomposition_energy(formula:str,
                                 TOTEN:float,
                                 functional:Literal['HSE','PBE']='HSE'):
    """
    For a given chemical structure's formula and a DFT relaxed
    reference energy obtained at a specified level of theory, compute
    weighted average of possible decomposition pathway energies

    equipped to handle decompositions in Perovskite element space
    - A: K, Rb, Cs, MA, FA
    - B: Ca, Sr, Ba, Ge, Sn, Pb
    - X: Cl, Br, I

    args
    frac: 14 dimensional composition vector in implicit order
    TOTEN: energy of dft relaxed structure

    returns
    decomposition energy value with included mixing entropy
    """
    refdf = refdf_dict[functional].iloc[:,-1]
    reps_per_site, consts, consts_frac = element_exist_list(formula)
    mix = mixing_ana(reps_per_site)
    decomp_phase, decomp_phase_frac = decomp_phase_ext(reps_per_site,
                                                       consts,
                                                       consts_frac,
                                                       mix)
    mixing_entropy = entropy_calcs(decomp_phase_frac)
    phase_ref_energies = refdf[decomp_phase].values
    return TOTEN - np.dot(np.array(decomp_phase_frac),
                          phase_ref_energies) + mixing_entropy

if __name__ == '__main__':
    import os
    import sqlite3

    d = {'Formula':['KSnI3',
                    'K0.125Rb0.125MA0.75Pb1I3',
                    'K1Ca0.125Ge0.875I3',
                    'RbGeBr2.625Cl0.375',
                    ],
         'TOTEN':[-133.780, -333.01, -135.745, -135.745],
         'Expected_DecoE_eV':[None, None, None, None]}
    calcdf = pd.DataFrame(d)

    # supposed to test against the main table, but I don't have TOTEN:

    # get main table
    # mannodi_pbe_q = """SELECT *
    #                    FROM mannodi_pbe"""
    # with sqlite3.connect(os.path.expanduser("~/src/cmcl/cmcl/db/perovskites.db")) as conn:
    #     mannodi_pbe = pd.read_sql(mannodi_pbe_q, conn, index_col="index").head(2)

    # calcdf = pd.concat([mannodi_pbe.Formula, mannodi_pbe.DecoE_eV], axis=1)

    calcdf['DecoE_eV_comp'] = calcdf.head(2).apply(
        lambda x: compute_decomposition_energy(x.Formula,
                                               x.TOTEN,
                                               functional='PBE'),
        axis=1
    )

    print(calcdf.filter(regex='DecoE'))
