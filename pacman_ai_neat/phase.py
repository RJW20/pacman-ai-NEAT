from enum import Enum
from typing import Callable

from pacman_ai_neat.simulator import only_dots, dots_and_blinky, dots_and_ghosts, full_game
from pacman_ai_neat.player import Player


class Phase(Enum):
    """Phases of training.

    The simulator functions corresponds to the correct simlator function for the phase.
    """

    ONLY_DOTS = 1, only_dots
    DOTS_AND_BLINKY = 2, dots_and_blinky
    DOTS_AND_GHOSTS = 3, dots_and_ghosts
    FULL_GAME = 4, full_game

    def __new__(cls, *args, **kwargs) -> object:
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj
    
    def __init__(self, value: int, simulator_function: Callable[[Player], Player]) -> None:
        self._simulator_function_ = simulator_function

    @property
    def simulator_function(self) -> Callable[[Player], Player]:
        return self._simulator_function_ 