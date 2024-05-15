from enum import Enum
from typing import Callable

from pacman_ai_neat.simulator import only_dots
from pacman_ai_neat.player import Player


class Phase(Enum):
    """Phases of training.
    
    The boolean values in the list correspond to including PacDots, Fruit, Ghosts and 
    PowerDots respectively.
    """

    ONLY_DOTS = [True, False, False, False], only_dots

    def __new__(cls, *args, **kwargs) -> object:
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj
    
    def __init__(self, inclusions: list[bool], simulator_function: Callable[[Player], Player]) -> None:
        self._simulator_function_ = simulator_function

    @property
    def simulator_function(self) -> Callable[[Player], Player]:
        return self._simulator_function_ 