from pacman_app import PacMan, PacDots
from pacman_app.map import Direction
from neat import BasePlayer


class Player(PacMan, BasePlayer):

    def __init__(self, *player_args: dict) -> None:
        super().__init__()
        self.vision: list[float]

    def look(self, pacdots: PacDots) -> None:
        """Set PacMan's vision.
        
        Can see: Whether it can move in any of the 4 cardinal directions (4 one-hot values), 
        and whether there is food in any of the cardinal directions (4 one-hot values).
        """
        self.vision = []
        
        # Own position
        self.vision.extend(position_to_float(self.position))

        # 4 cardinal directions
        directions = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
        for direction in directions:
            self.vision.append(int(self.can_move_in_direction(direction)))

        # Ghosts' positions
        for ghost in ghosts:
            self.vision.extend(position_to_float(ghost.position))


    def think(self) -> Direction:
        """Feed the input into the Genome and return the output as a valid move."""

        choices = self.genome.propagate(self.vision)
        choice = max(enumerate(choices), key = lambda choice: choice[1])[0]

        match(choice):
            case 0:
                return Direction.UP
            case 1:
                return Direction.RIGHT
            case 2:
                return Direction.DOWN
            case 3:
                return Direction.LEFT