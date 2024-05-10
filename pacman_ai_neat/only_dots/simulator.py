from pacman_ai_neat.only_ghosts.player import Player
from pacman_ai_neat.only_ghosts.settings import simulation_settings
from pacman_app import PacDots


def simulate(pacman: Player) -> Player:
    """Run PacMan in the game with only ghosts.
    
    Assigns a fitness that is simply the number of frames PacMan lives for.
    """


    pacman.initialise()
    pacdots = PacDots()

    lifespan = 0
    prev_tile = pacman.position.tile_pos
    stationary_count = 0
    MAX_SC = simulation_settings['max_stationary_count']
    while not pacman.dead:

        pacman.look(pacdots)
        move = pacman.think()
        pacman.move(move)
        if pacdots.check_if_eaten(pacman):
            pacman.score += 10
            pacman.move_next = False
        lifespan += 1

        if pacman.position.tile_pos == prev_tile:
            stationary_count += 1
            if stationary_count == MAX_SC:
                break
        else:
            stationary_count = 0
            prev_tile = pacman.position.tile_pos

    pacman.fitness = pacman.score * 100 / lifespan
    return pacman