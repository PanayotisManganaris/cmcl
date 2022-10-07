__version__ = '0.1.5'

from . import data
from .domain import Categories, make_possible_compositions, formula2dict, CompositionTable

__all__ = ["data",
           "Categories",
           "make_possible_compositions",
           "formula2dict",
           "CompositionTable"]
