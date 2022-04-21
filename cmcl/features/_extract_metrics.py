import pandas as pd
import numpy as np

from mendeleev import element
######################
#Jiaqi's Cubicity Calculator works directly with CONTCARS
from ase.io import read

class Calculator():
    @staticmethod
    def cubicity():
        # pre-define all lists and titles
        prop_lattice = []
        columns_out = ["a", "b", "c", "alpha", "beta", "gamma", "cub_b", "cub_c", "cub_alpha", "cub_beta", "cub_gamma"]

        for i in range(550):
            # input structure
            input_name = './strut_CONT_550/' + str(i + 1) + ".vasp"
            file_input = read(input_name, format='vasp')
            lattice_test = file_input.cell.cellpar()
        
            # calculate cubicity of each structure
            cub_b = (abs(lattice_test[0] - lattice_test[1])) / lattice_test[0]
            cub_c = (abs(lattice_test[0] - lattice_test[2])) / lattice_test[0]
            cub_alpha = (abs(lattice_test[3] - 90)) / 90
            cub_beta = (abs(lattice_test[4] - 90)) / 90
            cub_gamma = (abs(lattice_test[5] - 90)) / 90
            # assemble properties needed
            cubicity_test = np.array([cub_b, cub_c, cub_alpha, cub_beta, cub_gamma])
            # print(cubicity_test)
            lattice_test = np.append(lattice_test, cubicity_test)
        
            prop_lattice.append(lattice_test)
        
            # print(type(lattice_test[1]))
        
        # output lattice properties to excels for further process
        df = pd.DataFrame(prop_lattice, columns=columns_out)
        with pd.ExcelWriter("test.xlsx") as writer:
            df.to_excel(writer)
############

class MRGTable():
    """
    For every element:
    ion_rad
    BP
    MP
    dens
    at_wt
    EA
    IE
    hof
    hov
    En
    at_num
    period

    #not
    group
    val  
    ox_st

    in future cmcl will constitute only intermediary database which
    expands molecule name into constituent elements. From there, only
    mendeleev databases will be used.

    Legacy cmcl properties lookup will be preserved until I can insist
    on cutting the fat.
    """
    
    def __init__(self, mdf):
        pass
