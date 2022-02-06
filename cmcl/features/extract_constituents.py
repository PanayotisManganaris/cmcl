import pandas as pd
import re
import numpy as np

ptable ="""H                                                                   He 
           Li  Be                                          B   C   N   O   F   Ne 
           Na  Mg                                          Al  Si  P   S   Cl  Ar 
           K   Ca  Sc  Ti  V   Cr  Mn  Fe  Co  Ni  Cu  Zn  Ga  Ge  As  Se  Br  Kr 
           Rb  Sr  Y   Zr  Nb  Mo  Tc  Ru  Rh  Pd  Ag  Cd  In  Sn  Sb  Te  I   Xe 
           Cs  Ba  La  Hf  Ta  W   Re  Os  Ir  Pt  Au  Hg  Tl  Pb  Bi  Po  At  Rn 
           Fr  Ra  Ac  Rf  Db  Sg  Bh  Hs  Mt  Ds  Rg  Cn  Nh  Fl  Mc  Lv  Ts  Og 
                       Ce  Pr  Nd  Pm  Sm  Eu  Gd  Tb  Dy  Ho  Er  Tm  Yb  Lu     
                       Th  Pa  U   Np  Pu  Am  Cm  Bk  Cf  Es  Fm  Md  No  Lr    """

molecules = "FA|MA"

#warning: lets numbers of conjugate form slip by even if symbols dont match
#also lets sym0* through -- which is probably ok
#doesn't allow plain . to pass
valid_nums = r"([1-9]-[xyz])|([xyz])|(\d*\.?\d+)|(\d*)"
# reorder the ptable so short syms come last
orelsyms = '|'.join(sorted(ptable.split(), key=len)[::-1])
orsyms = molecules + "|" +  orelsyms

num_seg = re.compile(f"({valid_nums})")
formula_el = re.compile(f"({orsyms})")
formula_seg = re.compile(f"({orsyms})({valid_nums})")
formula_seq = re.compile(f"(({orsyms})({valid_nums}))+")

class FormulaParser():
    """
    Converts a variety of chemical formula conventions into a useful datastructure

    Accepted Grammar:
    formula = (formula_element valid_num)+
    formula_element = element | lparen formula rparen
    valid_num = REAL | symbolic

    each method is applied in sequence, progressively mutating the index
    """
    def __init__(self, alloy):
        self.alloy = alloy
        self.index = 0
        self.lparen = re.compile(r"\(")
        self.rparen = re.compile(r"\)")

    def parse_lparen(self):
        if self.lparen.match(self.alloy, self.index):
            self.index += 1
            return True
        else:
            return None

    def parse_rparen(self):
        if self.rparen.match(self.alloy, self.index):
            self.index += 1

    def parse_num(self):
        match = num_seg.match(self.alloy, self.index)
        if match:
            self.index = match.end()
            number = self.alloy[match.span()[0]:match.span()[1]]
            return pd.to_numeric(number or 1.0, errors="ignore")

    def parse_new_formula(self):
        result = []

        while e := self.parse_formula_element():
            num = self.parse_num()
            result.append((e, num))
        return result

    def parse_formula_element(self):
        e = self.parse_element()

        if e:
            return e
        else:
            if self.parse_lparen():
                f = self.parse_new_formula()
                self.parse_rparen()
                return f
            else:
                return None

    def parse_element(self):
        match = formula_el.match(self.alloy, self.index)

        if match:
            self.index = match.end()
            e = self.alloy[match.span()[0]:match.span()[1]]
            return e
        else:
            return None

def total_shorten(composition_tree):
    """calls helper to dynamically adapt mapping function"""
    top_func = lambda ftuple: total_shorten_helper(ftuple, 1)
    return list(map(top_func, composition_tree))


def total_shorten_helper(ftuple, multiplier):
    """Takes a tuple and a multipler. Returns the subformula of the tuple multipled"""
    subformula = ftuple[0]
    if isinstance(ftuple[1], (float, int, np.float64, np.int64)) and isinstance(multiplier, (float, int, np.float64, np.int64)):
        num = ftuple[1] * multiplier
    else:
        num = "(" + str(multiplier) + ")" + "(" + str(ftuple[1]) + ")"

    if isinstance(subformula, list):
        current_func = lambda ftuple: total_shorten_helper(ftuple, num)

        new_subformula = list(map(current_func, subformula))
        return new_subformula
    else:
        return (subformula, num)

def flatten_list(list_of_lists, flat_list=None):
    """generally flatten lists recursively"""
    if not type(flat_list) == list:
        flat_list = []
    for item in list_of_lists:
        if type(item) == list:
            flatten_list(item, flat_list)
        else:
            flat_list.append(item)
    return flat_list

def compile_nums(flatlist):
    """create dictionary by combining key values for repeated keys. provides symbolic concatination for unlike dtypes"""
    collect_dict = {}
    for eltuple in flatlist:
        if eltuple[0] not in collect_dict.keys():
            collect_dict[eltuple[0]] = eltuple[1]
        else:
            if type(collect_dict[eltuple[0]]) != type(eltuple[1]):
                collect_dict[eltuple[0]] = str(collect_dict[eltuple[0]]) + "+" + str(eltuple[1])
            elif isinstance(collect_dict[eltuple[0]], str):
                collect_dict[eltuple[0]] = collect_dict[eltuple[0]] + "+" + str(eltuple[1])
            else:
                collect_dict[eltuple[0]] += eltuple[1]
    return collect_dict

def process_formula(entry):
    """apply to formula series to obtain series of dicts for construction"""
    composition_tree = FormulaParser(entry).parse_new_formula()
    shorter_tree = total_shorten(composition_tree)
    formula_zip = flatten_list(shorter_tree)
    formula_dict = compile_nums(formula_zip)
    return formula_dict

class CompTable():
    """
    starting with only series of Formula strings, obtain dataframe
    of formulas' constituent quantities
    """
    
    
