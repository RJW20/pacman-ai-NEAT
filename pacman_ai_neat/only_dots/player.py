from pacman_app import PacMan, PacDots
from pacman_app.map import Direction
from neat import BasePlayer


def in_bounds(tile: tuple[int,int]) -> bool:
    """Return True if the given tile is in the PacMaze."""

    if tile[0] < 2 or tile[0] > 27:
        return False
    
    if tile[1] < 4 or tile[1] > 32:
        return False
    
    return True


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

        # Move in 4 cardinal directions
        directions = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
        for direction in directions:
            self.vision.append(int(self.can_move_in_direction(direction)))

        # Pacdot in 4 directions
        for direction in directions:
            next_tile = self.position.tile_x + direction.value.d_x, self.position.tile_y + direction.value.d_y
            found = False
            while in_bounds(next_tile):
                if next_tile in pacdots.dots:
                    self.vision.append(1)
                    found = True
                    break
                else:
                    next_tile = next_tile[0] + direction.value.d_x, next_tile[1] + direction.value.d_y

            if not found:
                self.vision.append(0)

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