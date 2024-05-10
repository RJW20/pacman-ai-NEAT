from pacman_ai_neat.only_ghosts.player import Player
from pacman_ai_neat.only_ghosts.settings import simulation_settings
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
    prev_position = pacman.position
    stationary_count = 0
    MAX_SC = simulation_settings['max_stationary_count']
    while not pacman.dead:

        pacman.look(ghosts)
        move = pacman.think()
        ghosts.move()
        pacman.move(move)
        ghosts.check_collision()
        fitness += 1

        if pacman.position == prev_position:
            stationary_count += 1
            if stationary_count == MAX_SC:
                pacman.fitness = fitness
                return
        else:
            stationary_count = 0
            prev_position = pacman.position

    pacman.fitness = fitness
    return pacman