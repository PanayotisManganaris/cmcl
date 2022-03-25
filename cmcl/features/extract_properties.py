import pandas as pd

from mendeleev import element

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
