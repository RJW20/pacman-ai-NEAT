import pygame

from pacman_app.game import Game
from pacman_app.background import Background
from pacman_app import PacDots, Ghosts
from pacman_app.sprites import SpriteSheet, BlinkySprite, PinkySprite, InkySprite, ClydeSprite, FruitSprite
from pacman_app.sprites.letters import Letters
from pacman_app.sprites.numbers import Numbers
from pacman_app.pixels import to_pixels

from pacman_ai_neat.playback_player import PlaybackPlayer


class CardinalVision(Game):
    """Area for testing PacMan's cardinal vision."""

    def __init__(self) -> None:

        # Pygame set up
        width = 616
        self.tile_size = width // 28
        screen_size = (self.tile_size * 30, self.tile_size * 36)
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("Cardinal Vision")
        self.clock = pygame.time.Clock()

        # Background set up
        self.bg = Background(self.tile_size)

        # Letter/number set up
        spritesheet = SpriteSheet(self.tile_size)
        self.letters = Letters(spritesheet)
        self.numbers = Numbers(spritesheet)

        # Fruit set up
        self.fruit = FruitSprite(spritesheet)

        # Character set up
        self.pacman = PlaybackPlayer({'spritesheet': spritesheet})
        self.pacdots = PacDots()
        blinky = BlinkySprite(self.pacman, spritesheet)
        pinky = PinkySprite(self.pacman, spritesheet)
        inky = InkySprite(self.pacman, spritesheet)
        clyde = ClydeSprite(self.pacman, spritesheet)
        self.ghosts = Ghosts(self.pacman, blinky, pinky, inky, clyde)

        self.pacman.initialise()
        self.ghosts.initialise()

    def update_screen(self) -> None:
        """Draw the current frame to the screen."""

        # Wipe the last frame
        self.bg.draw(self.screen)

        # Draw dots first so characters drawn oven them
        for dot in self.pacdots.dots:
            dot_position = to_pixels(dot, self.tile_size)
            pygame.draw.circle(self.screen, 'pink', dot_position, self.tile_size*0.2)

        for dot in self.pacdots.power_dots:
            dot_position = to_pixels(dot, self.tile_size)
            pygame.draw.circle(self.screen, 'pink', dot_position, self.tile_size*0.35)

        # Draw fruit
        if self.fruit.available:
            self.fruit.draw(self.screen)

        # Ghosts next
        for ghost in self.ghosts:
            if not ghost.inactive:
                ghost.draw(self.screen, self.tile_size)

        # Draw PacMan's ordinal vision
        start = to_pixels(self.pacman.position.tile_pos, self.tile_size)
        for i, direction in enumerate(self.pacman.perspective):
            end = to_pixels((
                self.pacman.position.tile_x + 5 * direction.value.d_x,
                self.pacman.position.tile_y + 5 * direction.value.d_y
                ), self.tile_size
            )
            sight = self.pacman.vision[i]
            color = (255 * (1 + min(sight,0)), 255 * (1 - max(sight, 0)), 0)
            pygame.draw.line(self.screen, color, start, end, 2)

        # Finally PacMan
        self.pacman.draw(self.screen, self.tile_size)

        # Write up-to-date score
        self.letters.draw_score(self.screen)
        self.numbers.draw_score(self.screen, self.pacman.score)

        # Update the screen
        pygame.display.flip()

    def run(self) -> None:
        """Run the main game loop."""

        pacman_move = self.pacman.direction

        while not self.pacman.dead:
            pacman_move = self.check_move(pacman_move)
            self.advance(pacman_move)
            self.pacman.look(self.pacdots, self.fruit, self.ghosts)
            self.update_screen()

            self.clock.tick(60)


if __name__ == '__main__':

    game = CardinalVision()
    game.run()