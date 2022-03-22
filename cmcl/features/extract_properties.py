import pandas as pd

from mendeleev import element
from cmcl.data.handlers import constituents

class LookupTable():
    """
    Base class for tables populated from Databases

    handles 
    """
    def lookup(el_name):
        el = element(el_name)
        el.ion_rad
        return 

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
    group
    val  
    ox_st

    For every molecule:
    stopgap: all but group, val, ox_st

    
    """
    
