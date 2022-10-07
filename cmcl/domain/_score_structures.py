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
