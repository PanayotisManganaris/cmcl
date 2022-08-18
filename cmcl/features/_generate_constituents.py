""" tools for extending composition vectors systematically """

import numpy as np
import pandas as pd
from itertools import permutations

def partitions(t:int, s:int):
    """
    generate all partitions for a total t of size s

    partition vectors are padded with zeros as needed

    TODO: handle s == 1 better than with a branch, 
    """
    if s == 1:
        yield (t,)
    else:
        for i in range(0, t//2+1):
            for p in partitions(t-i, s-1):
                yield (i,)+p

def compositions(t:int,s:int)->np.array:
    """ generate all compositions for a total t of size s """
    a = np.array(list(map(list,[permutations(tpl) for tpl in partitions(t,s)])))
    a = np.unique(a.reshape(-1, a.shape[-1]), axis=0)
    return a

def make_possible_compositions(constituents:list, unit_total:int, supercell_size:int):
    """ generate all possible composition vectors for a given list of candidate constituents """
    t = unit_total*supercell_size
    l = len(constituents)
    a = (supercell_size**-1)*compositions(t, l)
    return pd.DataFrame(a, columns=constituents)

