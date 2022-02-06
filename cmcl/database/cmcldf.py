import pandas as pd

class CmclFrame():
    """
    Convenience dataframe for easily getting ML training/target tables

    for certain Ml descriptors, when set does not exist, it will be created.

    Human descriptors:
    Formula = CmclFrame.human = CmclFrame["Formula", "Mixing"[, "Supercell"]]

    basic chemical descriptors:
    composition_tbl = CmclFrame.compositions = CmclFrame[compositions]
    prop_tbl = CmclFrame.properties = CmclFrame[properties]

    pymatgen descriptors:
    matminer_tbl = CmclFrame.dscribe = CmclFrame[describe]

    MEGnet descriptors:
    meg_tbl = CmclFrame.megnet = CmclFrame[megnet]
    """

