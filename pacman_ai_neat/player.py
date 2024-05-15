from pacman_app import PacMan, PacDots, Fruit, Ghosts
from pacman_app.characters.ghosts.mode import Mode
from pacman_app.map.direction import Direction, Vector
from neat import BasePlayer


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
    
    def in_bounds(self, tile: tuple[int,int]) -> bool:
        """Return True if the given tile is in the PacMaze."""

        if tile[0] < 2 or tile[0] > 27 or tile[1] < 4 or tile[1] > 32:
            return False
        
        return True

    def look(self, pacdots: PacDots, fruit: Fruit, ghosts: Ghosts) -> None:
        """Set PacMan's vision.
        
        Can see the below in the 4 cardinal directions (in the order from self.perspective):
        - whether it can move in the direction (4 one-hot values)
        - whether there is a PacDot (4 one-hot values)
        - whether the fruit is in the direction if available (4 one-hot values)
        - whether there is an active ghost (4 one-hot values)
        - whether there is a frightened ghost (4 one-hot values)
        """

        self.vision = []

        # Can move
        directions = self.perspective
        for direction in directions:
            self.vision.append(int(self.can_move_in_direction(direction)))

        # Others
        pacdot_vision = []
        fruit_vision = []
        a_ghost_vision = []
        f_ghost_vision = []
        a_ghost_positions = set(ghost.position.tile_pos for ghost in ghosts if not ghost.inactive and not ghost.mode == Mode.RETURN_TO_HOME)
        f_ghost_positions = set(ghost.position.tile_pos for ghost in ghosts if ghost.frightened)
        for direction in directions:

            dot_found = False
            fruit_found = False
            ghost_found = False
            next_tile = self.position.tile_x + direction.value.d_x, self.position.tile_y + direction.value.d_y
            while self.in_bounds(next_tile) and not all([dot_found, fruit_found, ghost_found]):

                # Dots
                if not dot_found and next_tile in pacdots.dots:
                    dot_found = True
                
                # Fruit
                if not fruit_found and next_tile == fruit.position.tile_pos:
                    fruit_found = True
                
                # Ghosts
                if not ghost_found:
                    if next_tile in a_ghost_positions:
                        ghost_found = True
                        a_ghost_vision.append(1)
                        f_ghost_vision.append(0)
                    elif next_tile in f_ghost_positions:
                        ghost_found = True
                        a_ghost_vision.append(0)
                        f_ghost_vision.append(1)

                next_tile = next_tile[0] + direction.value.d_x, next_tile[1] + direction.value.d_y

            pacdot_vision.append(int(dot_found))
            fruit_vision.append(int(fruit_found))

        self.vision.extend(pacdot_vision + fruit_vision + a_ghost_vision + f_ghost_vision)

    def think(self) -> Direction:
        """Feed the input into the Genome and return the output as a valid move."""

        choices = self.genome.propagate(self.vision)
        choice = max(enumerate(choices), key = lambda choice: choice[1])[0]
        return self.perspective[choice]