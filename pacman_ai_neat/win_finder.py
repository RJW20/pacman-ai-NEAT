import random
from pathlib import Path

from neat.genome import Genome
from pacman_app import PacDots, Fruit, Ghosts, Blinky, Pinky, Inky, Clyde
from pacman_ai_neat.player import Player


class WinFinder:
    """Class that repeats the full game of PacMan with the best saved Genome with 
    different random seeds until a win is found.
    
    Prints the seeds and the number of PacDots eaten.
    """

    def __init__(self) -> None:
                
        self.pacman = Player({})
        self.pacman.genome = Genome.load(Path('playback/full_game/19/0/0.pickle'))

        # Ghosts set up
        blinky = Blinky(self.pacman)
        pinky = Pinky(self.pacman)
        inky = Inky(self.pacman)
        clyde = Clyde(self.pacman)
        self.ghosts = Ghosts(self.pacman, blinky, pinky, inky, clyde)
        self.ghosts.initialise()

        # PacDot set up
        self.pacdots = PacDots()

        # Fruit set up
        self.fruit = Fruit()

    def initialise_ghosts(self) -> None:
        """Initialise the Ghosts and ensure that they are referencing current self.pacman."""

        for ghost in self.ghosts:
            ghost.pacman = self.pacman
        self.ghosts.pacman = self.pacman
        self.ghosts.initialise()

    def new_episode(self) -> None:
        """Prepare a new episode for all game entities."""

        self.pacman.initialise()
        self.initialise_ghosts()
        self.pacdots = PacDots()
        self.fruit.available = False

    def advance_pacman(self) -> None:
        """Advance PacMan one frame."""

        self.pacman.look(self.pacdots, self.fruit, self.ghosts)
        move = self.pacman.think()
        self.pacman.move(move)

    def advance_ghosts(self) -> None:
        """Advance the Ghosts one frame."""

        self.ghosts.move()
        self.ghosts.check_collision()

    def check_dots(self) -> bool:
        """Return True if PacMan has just eaten a PacDot.
        
        Automatically updates PacMan's attributes.
        """

        if self.pacdots.check_if_eaten(self.pacman):
            self.pacman.score += 10
            self.pacman.move_next = False
            return True
        
        return False
        
    def check_power_dots(self) -> bool:
        """Return True if PacMan has just eaten a PowerDot.
        
        Automatically updates PacMan's attributes and sets the Ghosts to frightened.
        """

        if self.pacdots.check_if_powered(self.pacman):
            self.pacman.score += 50
            self.pacman.move_next = False
            self.ghosts.frightened = True
            return True
        
        return False
    
    def check_fruit(self) -> None:
        """Check if PacMan has just eaten the Fruit.
        
        Automatically updates PacMan's attributes.
        """

        if not self.fruit.available:
            return
        
        if self.pacman.collided_with(self.fruit):
            self.pacman.score += 100
            self.fruit.available = False
        elif self.fruit.available_countdown == 0:
            self.fruit.available = False

        self.fruit.available_countdown -= 1
    
    def dot_ghost_release_threshold(self) -> None:
        """Check if enough PacDots have been eaten to release a Ghost."""

        if self.pacdots.remaining == 214:
            self.ghosts.inky.inactive = False
        elif self.pacdots.remaining == 184:
            self.ghosts.clyde.inactive = False

    def dot_elroy_threshold(self) -> None:
        """Check if enough PacDots have been eaten to set Blinky's elroy mode."""

        if self.pacdots.remaining == self.ghosts.blinky.elroy_first_threshold:
            self.ghosts.blinky.elroy = 1
        elif self.pacdots.remaining == self.ghosts.blinky.elroy_second_threshold:
            self.ghosts.blinky.elroy = 2

    def dot_fruit_threshold(self) -> None:
        """Check if enough PacDots have been eaten to make the Fruit available."""

        if self.pacdots.remaining == self.fruit.first_threshold:
            self.fruit.available = True
        elif self.pacdots.remaining == self.fruit.second_threshold:
            self.fruit.available = True

    def advance(self) -> None:
        """Advance to the next frame."""

        self.advance_pacman()
        self.advance_ghosts()
        self.check_dots()
        self.check_power_dots()
        self.check_fruit()
        self.dot_ghost_release_threshold()
        self.dot_elroy_threshold()
        self.dot_fruit_threshold()

    def run_game(self) -> None:
        """Simulate the game until PacMan dies."""

        while not self.pacman.dead:
            self.advance()

    def find_seed(self) -> None:
        """Iterate through games with different random seeds until a win occurs."""

        seed = 0
        dots_eaten = 0
        best = 0
        while dots_eaten < 244:
            random.seed(seed)
            self.new_episode()
            self.run_game()
            dots_eaten = 244 - len(self.pacdots.dots | self.pacdots.power_dots)
            if dots_eaten > best:
                best = dots_eaten
                print(f'{seed = }, dots eaten = {best}')
            seed += 1


if __name__ == '__main__':
    wf = WinFinder()
    wf.find_seed()