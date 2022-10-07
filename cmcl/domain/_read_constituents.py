import pandas as pd
import re
from .._utils import controlled_flatten, concat_key_values, total_shorten
import numpy as np
from unidecode import unidecode

ptable ="""H                                                                   He 
           Li  Be                                          B   C   N   O   F   Ne 
           Na  Mg                                          Al  Si  P   S   Cl  Ar 
           K   Ca  Sc  Ti  V   Cr  Mn  Fe  Co  Ni  Cu  Zn  Ga  Ge  As  Se  Br  Kr 
           Rb  Sr  Y   Zr  Nb  Mo  Tc  Ru  Rh  Pd  Ag  Cd  In  Sn  Sb  Te  I   Xe 
           Cs  Ba  La  Hf  Ta  W   Re  Os  Ir  Pt  Au  Hg  Tl  Pb  Bi  Po  At  Rn 
           Fr  Ra  Ac  Rf  Db  Sg  Bh  Hs  Mt  Ds  Rg  Cn  Nh  Fl  Mc  Lv  Ts  Og 
                       Ce  Pr  Nd  Pm  Sm  Eu  Gd  Tb  Dy  Ho  Er  Tm  Yb  Lu     
                       Th  Pa  U   Np  Pu  Am  Cm  Bk  Cf  Es  Fm  Md  No  Lr    """

molecules = "FA|MA|AM"

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
    Instantiate with an arbitrary chemical formula string

    Convert formula grammar into a useful tree

    Accepted Grammar:
    formula = (formula_element[_{]?valid_num[}]?)+
    formula_element = element | lparen formula rparen
    element = ptable symbol str | molecules symbol str
    valid_num = REAL | symbolic str

    return tree by calling parse_new_formula

    parse_new_formula calls the preceding methods, iterating the index
    progressively according to the matching grammar component
    """
    def __init__(self, alloy:str):
        alloy = "".join(list(map(unidecode, alloy)))
        self.alloy = re.sub(r"[\_\{\}]", "", alloy)
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
            return pd.to_numeric(number or 1, errors="ignore")

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

    def parse_new_formula(self):
        result = []
        e = self.parse_formula_element()
        while e:
            num = self.parse_num()
            result.append((e, num))
            e = self.parse_formula_element()
        return result

#TODO: Molecule Translator and Molecule De-convolution

def process_formula(entry):
    """
    args:
    arbitrary formula string

    returns:
    dict of element:portions
    """
    composition_tree = FormulaParser(entry).parse_new_formula()
    shorter_tree = total_shorten(composition_tree)
    formula_zip = controlled_flatten(shorter_tree, list)
    formula_dict = concat_key_values(formula_zip)
    return formula_dict

class CompositionTable():
    """
    starting with only series of Formula strings, obtain dataframe
    of formulas' constituent quantities

    Create Dataframe of Compositions and pass to FeatureAccessor for future reference.
    """
    def __init__(self, df):
        self.compdf = pd.DataFrame(df, columns=[])
        self._validate(df)

    def _validate(self, df):
        """
        make sure Formula "column" exists and (wishlist) Formula strings are of
        the expected form
        """
        if "Formula" in df or "formula" in df:
            try:
                self.Formula = df.Formula
            except AttributeError:
                self.Formula = df.formula
        elif "Formula" in df.index.names or "formula" in df.index.names:
            try:
                self.Formula = df.index.get_level_values("Formula").to_series()
            except AttributeError:
                self.Formula = df.index.get_level_values("formula").to_series()
        else:
            raise AttributeError("No 'Formula' column label or Index level recognized.")

    def make(self):
        # normalize string encoding!
        compdict_s = self.Formula.apply(process_formula)
        compdf = pd.DataFrame(compdict_s.to_list())
        comp_s_dict = compdf.to_dict()
        comp_dict = {}
        for k,v in comp_s_dict.items():
            comp_dict[k] = list(v.values())
        return comp_dict

    def get(self):
        comp_dict = self.make()
        self.compdf = self.compdf.assign(**comp_dict)
        #comp_cols = self.get()
        return self.compdf
