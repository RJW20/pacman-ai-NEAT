from functools import partial

from pacman_app import PacMan, PacDots, Fruit, Ghosts
from pacman_app.characters.ghosts.mode import Mode
from pacman_app.map import MAP, Tile
from pacman_app.map.direction import Direction, Vector
from neat import BasePlayer


class Player(PacMan, BasePlayer):

    def __init__(self, *player_args: dict) -> None:
        super().__init__()
        self.vision: list[float]
    
    def in_bounds(self, tile: tuple[int,int]) -> bool:
        """Return True if the given tile is in the PacMaze."""

        if tile[0] < 2 or tile[0] > 27 or tile[1] < 4 or tile[1] > 32:
            return False
        
        return True
    
    def look_at_tile(
        self,
        tile: tuple[int,int],
        pacdot_pos: set[tuple[int,int]],
        fruit_pos: tuple[int,int] | None,
        active_ghost_pos: set[tuple[int,int]],
        frightened_ghost_pos: set[tuple[int,int]]
    ) -> float:
        """Return the value of the given tile.
        
        Tile values are:
        - path = 0
        - frightened Ghost = 0.1
        - Fruit = 0.2
        - PacDot/PowerDots = 0.4
        - walls = 0.75
        - active Ghost = 1
        """

        if not self.in_bounds(tile):
            return 0.75
        
        if tile in pacdot_pos:
            return 0.4
        
        if fruit_pos and tile in fruit_pos:
            return 0.2
        
        if tile in active_ghost_pos:
            return 1
        
        if tile in frightened_ghost_pos:
            return 0.1
        
        if MAP[tile] == Tile.WALL:
            return 0.75
        else:
            return 0


    def look(self, pacdots: PacDots, fruit: Fruit, ghosts: Ghosts) -> None:
        """Set PacMan's vision.
        
        Can see an 11x11 grid centered on PacMan. Tile values are:
        Tile values are:
        - path = 0
        - frightened Ghost = 0.1
        - Fruit = 0.2
        - PacDot/PowerDots = 0.4
        - walls = 0.75
        - active Ghost = 1
        """

        # Prepare the things we're looking at
        pacdot_pos = pacdots.dots | pacdots.power_dots
        fruit_pos = fruit.position.tile_pos if fruit.available else None
        active_ghost_pos = set(ghost.position.tile_pos for ghost in ghosts if not ghost.inactive and not ghost.mode == Mode.RETURN_TO_HOME)
        frightened_ghost_pos = set(ghost.position.tile_pos for ghost in ghosts if ghost.frightened)

        # Prepare the list of tiles to look at
        pacman_x = self.position.tile_x
        pacman_y = self.position.tile_y
        match(self.direction):

            case Direction.UP:
                tiles = [(x,y) for y in range(pacman_y - 5, pacman_y + 6) for x in range(pacman_x - 5, pacman_x + 6) if not (x, y) == (pacman_x, pacman_y)]

            case Direction.RIGHT:
                tiles = [(x,y) for x in range(pacman_x + 5, pacman_x - 6, -1) for y in range(pacman_y - 5, pacman_y + 6) if not (x, y) == (pacman_x, pacman_y)]

            case Direction.DOWN:
                tiles = [(x,y) for y in range(pacman_y + 5, pacman_y - 6, -1) for x in range(pacman_x + 5, pacman_x - 6, -1) if not (x, y) == (pacman_x, pacman_y)]

            case Direction.LEFT:
                tiles = [(x,y) for x in range(pacman_x - 5, pacman_x + 6) for y in range(pacman_y + 5, pacman_y - 6, -1) if not (x, y) == (pacman_x, pacman_y)]


        self.vision =list(map(
            partial(
                self.look_at_tile,
                pacdot_pos=pacdot_pos,
                fruit_pos=fruit_pos,
                active_ghost_pos=active_ghost_pos,
                frightened_ghost_pos=frightened_ghost_pos
            ),
            tiles
        ))

    @property
    def perspective(self) -> list[Direction]:
        """Return a list containing the Directions corresponding to PacMan's forward, right, 
        back and left."""

        directions = [self.direction]
        for _ in range(3):
            directions.append(Direction(Vector(-directions[-1].value.d_y, directions[-1].value.d_x)))
        return directions

    def think(self) -> Direction:
        """Feed the input into the Genome and return the output as a valid move."""

        choices = self.genome.propagate(self.vision)
        choice = max(enumerate(choices), key = lambda choice: choice[1])[0]
        return self.perspective[choice]