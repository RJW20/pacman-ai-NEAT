from pacman_app import PacMan, PacDots, Fruit, Ghosts
from pacman_app.characters.ghosts.mode import Mode
from pacman_app.map import MAP, Tile
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
    
    def look_in_direction(
        self,
        direction: Direction,
        pacdot_pos: set[tuple[int,int]],
        fruit_pos: tuple[int,int] | None,
        active_ghost_pos: set[tuple[int,int]],
        frightened_ghost_pos: set[tuple[int,int]]
    ) -> float:
        """Look 5 tiles in the given direction and return a value corresponding to what is seen.

        If the first tile is wall returns 1.
        If there is nothing (possibly before a wall) returns 0.5.
        If there is a PacDot before any walls returns 0.2.
        If there is the Fruit before any walls return 0.1 (looks like better PacDot).
        If there is an active Ghost before any walls returns 1 so it looks like a wall to PacMan.
        If there is a frightened Ghost before any walls returns 0 (looks like even better PacDot).
        """

        if not self.can_move_in_direction(direction):
            return 1

        tiles = [(self.position.tile_x + i*direction.value.d_x, self.position.tile_y + i*direction.value.d_y) for i in range(1,6)]
        value = 0.5
        for tile in tiles:

            # If out of bounds then its only been path (only happens in tunnel)
            if not self.in_bounds(tile):
                return 0.5
            
            # If its wall then we can make a decision
            if MAP[tile] == Tile.WALL:
                return value
            
            # If its an active ghost we want to treat it like we can't move that way
            if tile in active_ghost_pos:
                return 1
            
            # If its a frightend ghost update/overwrite the value
            if tile in frightened_ghost_pos:
                value = 0

            # If its a PacDot then update the value (but only if we haven't seen something better)
            if tile in pacdot_pos:
                value = min(0.2, value)

            # If its a Fruit then update the value (but only if we haven't seen something better)
            if fruit_pos and tile == fruit_pos:
                value = min(0.1, value)

        return value

    def look(self, pacdots: PacDots, fruit: Fruit, ghosts: Ghosts) -> None:
        """Set PacMan's vision.
        
        Can see the below for 5 squares in the 4 cardinal directions (in the order from self.perspective):
        - whether it can move in the direction (value = 0.5)
        - whether there is a wall in the direction (value = 1)
        - whether there is a PacDot (value = 0.2)
        - whether there is the Fruit (value = 0.1)
        - whether there is an active ghost (value = 1)
        - whether there is a frightened ghost (value = 0)
        """

        self.vision = []

        # Prepare the things we're looking at
        pacdot_pos = pacdots.dots | pacdots.power_dots
        if len(pacdot_pos) == 0:
            print('Finished!', flush=True)
        fruit_pos = fruit.position.tile_pos if fruit.available else None
        active_ghost_pos = set(ghost.position.tile_pos for ghost in ghosts if not ghost.inactive and not ghost.mode == Mode.RETURN_TO_HOME)
        frightened_ghost_pos = set(ghost.position.tile_pos for ghost in ghosts if ghost.frightened)

        # Look in all the directions
        directions = self.perspective
        for direction in directions:
            self.vision.append(self.look_in_direction(
                direction=direction,
                pacdot_pos=pacdot_pos,
                fruit_pos=fruit_pos,
                active_ghost_pos=active_ghost_pos,
                frightened_ghost_pos=frightened_ghost_pos,
            ))

    def think(self) -> Direction:
        """Feed the input into the Genome and return the output as a valid move."""

        choices = self.genome.propagate(self.vision)
        choice = max(enumerate(choices), key = lambda choice: choice[1])[0]
        return self.perspective[choice]