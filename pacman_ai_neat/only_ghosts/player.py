from pacman_app import PacMan, Ghosts
from pacman_app.map import Direction, Position
from neat import BasePlayer

def position_to_float(position: Position) -> list[float]:
    """Return a Character's Position as normalised values to use in a Genome."""

    return [position.true_x / 29, (position.true_y - 4) / 28]


class Player(PacMan, BasePlayer):

    def __init__(self, *player_args: dict) -> None:
        super().__init__()
        self.vision: list[float]

    def look(self, ghosts: Ghosts) -> None:
        """Set PacMan's vision.
        
        Can see: own position (2 values), whether it can move in any of the 4 cardinal directions 
        (4 one-hot values), ghosts' positions (2x4 values).
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