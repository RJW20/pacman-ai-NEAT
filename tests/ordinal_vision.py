import pygame

from pacman_app.background import Background
from pacman_app import PacDots, Ghosts
from pacman_app.sprites import SpriteSheet, BlinkySprite, PinkySprite, InkySprite, ClydeSprite, FruitSprite
from pacman_app.sprites.letters import Letters
from pacman_app.sprites.numbers import Numbers
from pacman_app.map.direction import Direction, Vector
from pacman_app.pixels import to_pixels

from pacman_ai_neat.playback_player import PlaybackPlayer


class OrdinalVision:
    """Area for testing PacMan's ordinal vision."""

    def __init__(self) -> None:

        # Pygame set up
        width = 616
        self.tile_size = width // 28
        screen_size = (self.tile_size * 30, self.tile_size * 36)
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("Ordinal Vision")
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

    def check_move(self, move: Direction) -> Direction:
        """Check for new PacMan move."""

        for event in pygame.event.get():
            # Allow quitting
            if event.type == pygame.QUIT: 
                pygame.quit()
                exit()

            # Set move
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    move = Direction.UP
                elif event.key == pygame.K_RIGHT:
                    move =  Direction.RIGHT
                elif event.key == pygame.K_DOWN:
                    move =  Direction.DOWN
                elif event.key == pygame.K_LEFT:
                    move =  Direction.LEFT

        return move

    def advance(self, move: Direction) -> None:
        """Advance to the next frame."""

        # Move characters and check for collisions
        self.ghosts.move()
        self.pacman.move(move)
        self.ghosts.check_collision()

        # Update pacdots
        dots_changed = False
        if self.pacdots.check_if_eaten(self.pacman):
            self.pacman.score += 10
            self.pacman.move_next = False
            dots_changed = True
        elif self.pacdots.check_if_powered(self.pacman):
            self.pacman.score += 50
            self.pacman.move_next = False
            self.ghosts.frightened = True
            dots_changed = True

        # Alter ghosts depending on remaining dots
        if dots_changed:
            if self.pacdots.remaining == 214:
                self.ghosts.inky.inactive = False
            elif self.pacdots.remaining == 184:
                self.ghosts.clyde.inactive = False
            elif self.pacdots.remaining == self.ghosts.blinky.elroy_first_threshold:
                self.ghosts.blinky.elroy = 1
            elif self.pacdots.remaining == self.ghosts.blinky.elroy_second_threshold:
                self.ghosts.blinky.elroy = 2
            elif self.pacdots.remaining == self.fruit.first_threshold:
                self.fruit.available = True
            elif self.pacdots.remaining == self.fruit.second_threshold:
                self.fruit.available = True

        # Update fruit
        if self.fruit.available:
            if self.pacman.collided_with(self.fruit):
                self.pacman.score += 100
                self.fruit.available = False
            elif self.fruit.available_countdown == 0:
                self.fruit.available = False
            self.fruit.available_countdown -= 1

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
        s = pygame.Surface((self.tile_size * 3, self.tile_size * 3))
        s.set_alpha(128)
        rect = pygame.Rect(0, 0, self.tile_size * 3, self.tile_size * 3)
        for i, direction in enumerate(self.pacman.perspective):
            orthog_direction = Direction(Vector(-direction.value.d_y, direction.value.d_x))
            center = to_pixels((
                self.pacman.position.tile_x + 2 * (direction.value.d_x + orthog_direction.value.d_x),
                self.pacman.position.tile_y + 2 * (direction.value.d_y + orthog_direction.value.d_y)
                ), self.tile_size
            )
            rect.center = center
            sight = self.pacman.vision[i + 4]
            color = (255, 0, 0) if sight else (0, 255, 0)
            s.fill(color)
            self.screen.blit(s, rect.topleft)

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

    game = OrdinalVision()
    game.run()
