from pacman_ai_neat.player import Player
from pacman_ai_neat.settings import simulation_settings
from pacman_app import PacDots, Fruit, Ghosts, Blinky, Pinky, Inky, Clyde


def simulate(pacman: Player) -> Player:
    """Run PacMan in the game with PacDots, PowerDots and Ghosts.
    
    Runs until PacMan dies, goes too long without eating a dot or stays still for too long.
    Assigns a fitness that is a the multiplication of the square of the score and time taken
    to achieve it.
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

    # Run a loop until PacMan eats all Dots or takes too long to do so
    lifespan = 0
    famine_count = 0
    stationary_count = 0
    MAX_FAMINE_COUNT = simulation_settings['max_famine_count']
    MAX_STATIONARY_COUNT = simulation_settings['max_stationary_count']
    prev_tile = pacman.position.tile_pos
    while not pacman.dead and famine_count < MAX_FAMINE_COUNT and stationary_count < MAX_STATIONARY_COUNT:

        pacman.look(pacdots, fruit, ghosts)
        move = pacman.think()
        pacman.move(move)
        lifespan += 1

        # Update Ghosts
        ghosts.move()
        ghosts.check_collision()

        # Update score/famine_count
        dots_changed = False
        if pacdots.check_if_eaten(pacman):
            dots_changed = True
            pacman.score += 10
            pacman.move_next = False
            famine_count = 0
        elif pacdots.check_if_powered(pacman):
            dots_changed = True
            pacman.score += 50
            pacman.move_next = False
            ghosts.frightened = True
        else:
            famine_count += 1

        # Check for PacDot checkpoints
        if dots_changed:
            if pacdots.remaining == 214:
                ghosts.inky.inactive = False
            elif pacdots.remaining == 184:
                ghosts.clyde.inactive = False
            elif pacdots.remaining == ghosts.blinky.elroy_first_threshold:
                ghosts.blinky.elroy = 1
            elif pacdots.remaining == ghosts.blinky.elroy_second_threshold:
                ghosts.blinky.elroy = 2
            elif pacdots.remaining == fruit.first_threshold:
                fruit.available = True
            elif pacdots.remaining == fruit.second_threshold:
                fruit.available = True

        # Update fruit
        if fruit.available:
            if pacman.collided_with(fruit):
                pacman.score += 100
                fruit.available = False
            elif fruit.available_countdown == 0:
                fruit.available = False
            fruit.available_countdown -= 1

        # Update stationary_count
        if pacman.position.tile_pos == prev_tile:
            stationary_count += 1
        else:
            stationary_count = 0

    # Alter lifespans to be true lifespan
    if famine_count == MAX_FAMINE_COUNT:
        lifespan -= MAX_FAMINE_COUNT
    elif stationary_count == MAX_STATIONARY_COUNT:
        lifespan -= MAX_STATIONARY_COUNT

    pacman.fitness = (pacman.score // 10) ** 2 * (lifespan // 1000)
    return pacman