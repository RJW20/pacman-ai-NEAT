from enum import Enum


class Phase(Enum):
    """Phases of training.
    
    The boolean values in the list correspond to including PacDots, Fruit, Ghosts and 
    PowerDots respectively.
    """

    ONLY_DOTS = [True, False, False, False]
    