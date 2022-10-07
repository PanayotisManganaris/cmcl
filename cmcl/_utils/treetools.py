import numpy as np
from typing import Any

def controlled_flatten(itr_of_itrs:list, itr_to_flatten:list=list):
    """
    flatten iterable recursively
    preserve any iterable elements of types
    """
    if isinstance(itr_of_itrs, itr_to_flatten):
        for ele in itr_of_itrs:
            yield from controlled_flatten(ele)
    else:
        yield itr_of_itrs

def concat_key_values(flatlist):
    """
    create dictionary by combining repeated entries in flatlist into
    single keys. provides symbolic concatenation for unlike dtypes
    """
    collect_dict = {}
    for eltuple in flatlist:
        if eltuple[0] not in collect_dict.keys():
            collect_dict[eltuple[0]] = eltuple[1]
        else:
            if type(collect_dict[eltuple[0]]) != type(eltuple[1]):
                # make both strings and combine
                collect_dict[eltuple[0]] = str(collect_dict[eltuple[0]]) + "+" + str(eltuple[1])
            elif isinstance(collect_dict[eltuple[0]], str):
                # first already string
                collect_dict[eltuple[0]] = collect_dict[eltuple[0]] + "+" + str(eltuple[1])
            else:
                # numbers, lists, etc
                collect_dict[eltuple[0]] += eltuple[1]
    return collect_dict

# specifically intended for formula trees
def total_shorten(composition_tree:list[tuple]) -> list[list|tuple]:
    """
    calls helper to dynamically adapt mapping function

    returns short equivalent of the input tree
    """
    top_func = lambda ftuple: _total_shorten_helper(ftuple, 1)
    return list(map(top_func, composition_tree))

def _total_shorten_helper(ftuple:tuple[list|tuple, ...],
                          parent_multiple:Any) -> tuple[str, np.number|str]:
    """Takes a tuple and a multiplier. Returns the subformula of the tuple multiplied"""
    current_formula, current_multiple = ftuple
    ccheck = isinstance(current_multiple, (int, float, np.number))
    pcheck = isinstance(parent_multiple, (int, float, np.number))
    if ccheck and pcheck:
        num = current_multiple * parent_multiple
    else:
        num = "(" + str(parent_multiple) + ")" + "(" + str(current_multiple) + ")"

    if isinstance(current_formula, list):
        current_func = lambda ftuple: _total_shorten_helper(ftuple, num)

        child_formula = list(map(current_func, current_formula))
        return child_formula
    else:
        return (current_formula, num)
