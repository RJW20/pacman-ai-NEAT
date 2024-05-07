from .player import Player
from pacman_app import Ghosts


def simulate(pacman: Player) -> Player:
    """Run PacMan in the game with only ghosts.
    
    Assigns a fitness that is simply the number of frames PacMan lives for.
    """

    ghosts = Ghosts(pacman)
    pacman.initialise()
    ghosts.initialise()

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