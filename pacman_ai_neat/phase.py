from enum import Enum, auto
from typing import Callable

from pacman_ai_neat.simulator import only_dots, dots_and_ghosts, full_game
from pacman_ai_neat.player import Player


class Phase(Enum):
    """Phases of training.
    
    The boolean values in the list correspond to including PacDots, Fruit, Ghosts and 
    PowerDots respectively.
    The simulator functions corresponds to the correct simlator function for the phase.
    """

    ONLY_DOTS = only_dots
    DOTS_AND_GHOSTS = dots_and_ghosts
    FULL_GAME = full_game

    def __new__(cls, *args, **kwargs) -> object:
        obj = object.__new__(cls)
        obj._value_ = auto()
        return obj
    
    def __init__(self, simulator_function: Callable[[Player], Player]) -> None:
        self._simulator_function_ = simulator_function

    @property
    def simulator_function(self) -> Callable[[Player], Player]:
        return self._simulator_function_ 