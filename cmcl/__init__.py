__version__ = '0.1.5'

from . import data
from .features import Categories, make_possible_compositions, process_formula, CompositionTable

__all__ = ["data",
           "Categories",
           "make_possible_compositions",
           "process_formula",
           "CompositionTable"]
