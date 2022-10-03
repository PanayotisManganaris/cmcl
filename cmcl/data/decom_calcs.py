import numpy as np
import pandas as pd
import copy
import os

from typing import Union, Any

# reference energies of constituent phases
AX_ref_HSE = pd.read_excel(os.path.expanduser('~/src/cmcl/cmcl/db/ref_data.xlsx'),
                           sheet_name='AX_HSE', engine='openpyxl')
AX_ref_PBE = pd.read_excel(os.path.expanduser('~/src/cmcl/cmcl/db/ref_data.xlsx'),
                           sheet_name='AX_PBE', engine='openpyxl')
BX2_ref_HSE = pd.read_excel(os.path.expanduser('~/src/cmcl/cmcl/db/ref_data.xlsx'),
                            sheet_name='BX2_HSE', engine='openpyxl')
BX2_ref_PBE = pd.read_excel(os.path.expanduser('~/src/cmcl/cmcl/db/ref_data.xlsx'),
                            sheet_name='BX2_PBE', engine='openpyxl')
AX_ref_HSE_dict = AX_ref_HSE.set_index('sys')['HSE_ref'].to_dict()
AX_ref_PBE_dict = AX_ref_PBE.set_index('sys')['PBE_ref'].to_dict()
BX2_ref_HSE_dict = BX2_ref_HSE.set_index('sys')['HSE_ref'].to_dict()
BX2_ref_PBE_dict = BX2_ref_PBE.set_index('sys')['PBE_ref'].to_dict()
ref_HSE_dict = AX_ref_HSE_dict
ref_HSE_dict.update(BX2_ref_HSE_dict)
ref_PBE_dict = AX_ref_PBE_dict
ref_PBE_dict.update(BX2_ref_PBE_dict)

# analyze mixing 
def element_exist_list(frac_mix:Union[list,np.ndarray]):
    """
    args:
    composition vector in implicit order

    returns:
    tuple of
    0. list counting alements involved at each site
    1. list of elements
    2. list of ammounts of each element
    """
    # element_exits is the index of element, not fraction
    element_exist = np.nonzero(frac_mix)[0]
    element_space = A_element + B_element + X_element
    formula = [element_space[x] for x in element_exist] #constituents
    element_frac = [frac_mix[x] for x in element_exist] #constituent fractions
    # collect elements for each site
    # [element number in A site,element number in B site,element number in X site]
    element_mixed_num = [0, 0, 0]
    for elem_num in range(len(element_exist)):
        if element_exist[elem_num] <= 4: #TODO: access element keys
            element_mixed_num[0] += 1
        elif 5 <= element_exist[elem_num] <= 10:
            element_mixed_num[1] += 1
        elif element_exist[elem_num] >= 11:
            element_mixed_num[2] += 1
    return element_mixed_num, formula, element_frac


def mixing_ana(frac_vec_input):
    frac_mix = np.array(copy.deepcopy(frac_vec_input))
    element_mixed_num, formula, element_frac = element_exist_list(frac_mix)
    # find mixing, only consider pure, amix, bmix and xmix
    # only 1 site is mixed
    if element_mixed_num == [1, 1, 1]:
        mixing = 'Pure'
    elif element_mixed_num[1:] == [1, 1] and element_mixed_num[0] != 1:
        mixing = 'Amix'
    elif element_mixed_num[0:2] == [1, 1] and element_mixed_num[2] != 1:
        mixing = 'Xmix'
    else:
        mixing = 'Bmix'
    return element_mixed_num, mixing, formula, element_frac


# decomposed phase extract
def decomp_phase_ext(element_input, formula_input, mix, element_frac):
    element_tem = copy.deepcopy(element_input)
    formula = copy.deepcopy(formula_input)
    if mix == 'Pure':
        decomp_phase = [formula[0] + formula[2], formula[1] + formula[2] + '2']
        decomp_phase_frac = [1, 1]
    elif mix == 'Amix':
        A_num = element_tem[0]
        A_decomp = [formula[x] + formula[-1] for x in range(A_num)]
        decomp_phase = A_decomp + [formula[-2] + formula[-1] + '2']
        n_element = len(element_frac)
        decomp_phase_frac = element_frac[0:n_element - 1]
    elif mix == 'Bmix':
        B_num = element_tem[1]
        B_decomp = [formula[x + 1] + formula[-1] + '2' for x in range(B_num)]
        decomp_phase = [formula[0] + formula[-1]] + B_decomp
        n_element = len(element_frac)
        decomp_phase_frac = element_frac[0:n_element - 1]
    elif mix == 'Xmix':
        X_num = element_tem[2]
        A_decomp = [formula[0] + formula[-2 + x] for x in range(X_num)]
        B_decomp = [formula[1] + formula[-2 + x] + '2' for x in range(X_num)]
        decomp_phase = A_decomp + B_decomp
        decomp_phase_frac = [x / 3 for x in element_frac[2:]] + [y / 3 for y in element_frac[2:]]
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


# decomposition calculation function
def decomp_calc(frac, TOTEN, functional='HSE'):
    """
    Decomposition Energy Calculator
    input: element fraction vector
    element space:
    - A:
    - B:
    - X: Cl, Br, I

    output: decomposition energy value, mixing entropy included
    """
    if functional == 'HSE':
        element, mix, fomula, element_frac = mixing_ana(frac)
        # print(element, mix, fomula)
        decomp_phase, decomp_phase_frac = decomp_phase_ext(element,
                                                           fomula,
                                                           mix,
                                                           element_frac)
        print(decomp_phase)
        phase_ref_energy = []
        # use decom_phase to search ref energy in dictionary
        for i in decomp_phase:
            phase_ref_energy.append(ref_HSE_dict[i])
        print(decomp_phase_frac)
        print(phase_ref_energy)
        mixing_entropy = entropy_calcs(decomp_phase_frac)
        print(mixing_entropy)
        decomp_energy = TOTEN - np.dot(np.array(decomp_phase_frac),
                                       np.array(phase_ref_energy)) + mixing_entropy
    elif functional == 'PBE':
        element, mix, fomula, element_frac = mixing_ana(frac)
        # print(element, mix, fomula)
        decomp_phase, decomp_phase_frac = decomp_phase_ext(element,
                                                           fomula,
                                                           mix,
                                                           element_frac)
        print(decomp_phase)
        phase_ref_energy = []
        # use decom_phase to search ref energy in dictionary
        for i in decomp_phase:
            phase_ref_energy.append(ref_PBE_dict[i])
        print(decomp_phase_frac)
        print(phase_ref_energy)
        mixing_entropy = entropy_calcs(decomp_phase_frac)
        print(mixing_entropy)
        decomp_energy = TOTEN - np.dot(np.array(decomp_phase_frac),
                                       np.array(phase_ref_energy)) + mixing_entropy
    return decomp_energy


# define list for element space
A_element = ['K', 'Rb', 'Cs', 'MA', 'FA']
B_element = ['Ca', 'Sr', 'Ba', 'Ge', 'Sn', 'Pb']
X_element = ['Cl', 'Br', 'I']

if __name__ == '__main__':
    # test sample K|Sn|I
    # test_sample = [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 3]
    # test_TOTEN = -133.780
    # test sample KRbMA|Pb|I
    # test_sample = [0.125, 0.125, 0, 0.75, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3]
    # test_TOTEN = -333.01
    # test_sample K|CaGe|I
    # test_sample = [1, 0, 0, 0, 0, 0.125, 0, 0, 0.875, 0, 0, 0, 0, 3]
    # test_TOTEN = -135.745
    # test sample Rb|Ge|BrCl
    # test_sample = [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 2.625, 0.375, 0]
    # test_TOTEN = -138.21702919

    # test_element, test_mix, test_fomula, test_decomp_phase_frac = mixing_ana(test_sample)
    # print(test_element, test_mix, test_fomula)
    # test_decomp_phase = decomp_phase_ext(test_element, test_fomula, test_mix)
    # print(test_decomp_phase)
    #
    # test_decomp = decomp_calc(test_sample, test_TOTEN, functional='PBE')
    # print(test_decomp)

    import sys
    import os
    sys.path.append(os.path.expanduser('~/src/cmcl'))
    import sqlite3
    import cmcl

    decomp_result = []
    mannodi_pbe_q = """SELECT *
                       FROM mannodi_pbe"""
    with sqlite3.connect(os.path.expanduser("~/src/cmcl/cmcl/db/perovskites.db")) as conn:
        mannodi_pbe = pd.read_sql(mannodi_pbe_q, conn, index_col="index")
    comp = mannodi_pbe.ft.comp()
    sample_list = comp.values[:10].tolist()

    for sample in sample_list:
        print(sample)
        test_decomp = decomp_calc(sample[0:14],
                                  sample[-1],
                                  functional='PBE')
        print(test_decomp)
        decomp_result.append(test_decomp)
    print(decomp_result)
    result_out = sample_input
    result_out['decomp'] = decomp_result
    print(result_out)
