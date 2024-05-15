from pacman_ai_neat.player import Player
from pacman_ai_neat.settings import simulation_settings
from pacman_app import PacDots, Fruit, Ghosts, Blinky, Pinky, Inky, Clyde


def only_dots(pacman: Player) -> Player:
    """Run PacMan in the game with only PacDots.
    
    Assigns a fitness that is a ratio between score and time taken to achieve it.
    """

    pacman.initialise()

    # Dots
    pacdots = PacDots()

    # Set up inactive Fruit
    fruit = Fruit()

    # Set up inactive ghosts
    blinky = Blinky(pacman)
    pinky = Pinky(pacman)
    inky = Inky(pacman)
    clyde = Clyde(pacman)
    ghosts = Ghosts(pacman, blinky, pinky, inky, clyde)
    ghosts.initialise()
    ghosts.blinky.inactive = False

    # Run a loop until PacMan eats all Dots or takes too long to do so
    lifespan = 0
    MAX_LIFESPAN = simulation_settings['max_lifespan']
    prev_tile = pacman.position.tile_pos
    stationary_count = 0
    MAX_SC = simulation_settings['max_stationary_count']
    while pacman.score < 2400 and lifespan < MAX_LIFESPAN:

        pacman.look(pacdots, fruit, ghosts)
        move = pacman.think()
        pacman.move(move)
        if pacdots.check_if_eaten(pacman):
            pacman.score += 10
            pacman.move_next = False
        lifespan += 1

        # Punish PacMan if just sitting still
        if pacman.position.tile_pos == prev_tile:
            stationary_count += 1
            if stationary_count == MAX_SC:
                lifespan = 10 * MAX_LIFESPAN
        else:
            stationary_count = 0
            prev_tile = pacman.position.tile_pos

    pacman.fitness = pacman.score * 1000 / lifespan
    return pacman