from pacman_app import PacMan, PacDots
from pacman_app.map.direction import Direction, Vector
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

    @property
    def perspective(self) -> list[Direction]:
        """Return a list containing the Directions corresponding to PacMan's forward, right, 
        back and left."""

        directions = [self.direction]
        for _ in range(3):
            directions.append(Direction(Vector(-directions[-1].value.d_y, directions[-1].value.d_x)))
        return directions

    def look(self, pacdots: PacDots) -> None:
        """Set PacMan's vision.
        
        Can see: Whether it can move in any of the 4 cardinal directions (4 one-hot values), 
        and whether there is food in any of the cardinal directions (4 one-hot values).
        The 4 directions are always rotated to be from PacMan's perspective.
        """
        self.vision = []

        # Move in 4 cardinal directions
        directions = self.perspective
        for direction in directions:
            self.vision.append(int(self.can_move_in_direction(direction)))

        # Pacdot in 4 directions
        for direction in directions:

            dot_found = False
            next_tile = self.position.tile_x + direction.value.d_x, self.position.tile_y + direction.value.d_y
            while in_bounds(next_tile):
                if next_tile in pacdots.dots:
                    dot_found = True
                    break
                else:
                    next_tile = next_tile[0] + direction.value.d_x, next_tile[1] + direction.value.d_y

            self.vision.append(int(dot_found))

    def think(self) -> Direction:
        """Feed the input into the Genome and return the output as a valid move."""

        choices = self.genome.propagate(self.vision)
        choice = max(enumerate(choices), key = lambda choice: choice[1])[0]
        return self.perspective[choice]