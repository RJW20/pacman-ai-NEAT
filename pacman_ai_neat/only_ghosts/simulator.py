from .player import Player
from pacman_app import Ghosts, Blinky, Pinky, Inky, Clyde


def simulate(pacman: Player) -> Player:
    """Run PacMan in the game with only ghosts.
    
    Assigns a fitness that is simply the number of frames PacMan lives for.
    """

    blinky = Blinky(pacman)
    pinky = Pinky(pacman)
    inky = Inky(pacman)
    clyde = Clyde(pacman)
    ghosts = Ghosts(pacman, blinky, pinky, inky, clyde)
    pacman.initialise()
    ghosts.initialise()
    ghosts.inky.inactive = False
    ghosts.clyde.inactive = False

    fitness = 0
    while not pacman.dead:

        pacman.look(ghosts)
        move = pacman.think()
        ghosts.move()
        pacman.move(move)
        ghosts.check_collision()
        fitness += 1

    pacman.fitness = fitness
    return pacman