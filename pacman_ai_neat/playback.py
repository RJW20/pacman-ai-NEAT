import pygame

from pacman_app.background import Background
from pacman_app import PacMan, PacDots, Ghosts
from pacman_app.sprites import SpriteSheet, BlinkySprite, PinkySprite, InkySprite, ClydeSprite, FruitSprite
from pacman_app.sprites.letters import Letters
from pacman_app.sprites.numbers import Numbers
from pacman_app.map import Direction
from pacman_app.pixels import to_pixels

from neat import PlaybackPlayers


class Playback:
    """Controller of all objects that are present in the Playback.
    
    Switch between generations with the left and right arrow keys.
    Switch between Species with the up and down arrow keys.
    Slow down up or speed up the playback with the j and k keys.
    """

    def __init__(
        self,
        playback_folder: str,
        playback_player: type,
        player_args,
        ghosts: bool,
        pacdots: bool,
        powerdots: bool,
        fruit: bool,
    ) -> None:
        
        # Store our current mode
        self.include_ghosts = ghosts
        self.include_pacdots = pacdots
        self.include_powerdots = powerdots
        self.include_fruit = fruit

        # Pygame set up
        width = 532
        self.tile_size = width // 28
        screen_size = (self.tile_size * 30, self.tile_size * 36)
        self.screen = pygame.display.set_mode(screen_size)
        caption = [(ghosts, 'ghosts'), (pacdots, 'pacdots'), (powerdots, 'powerdots'), (fruit, 'fruit')]
        pygame.display.set_caption("PacMan: Playback with " + ", ".join([inclusion[1] for inclusion in caption if inclusion[0]]))
        pygame.font.init()
        font_height = int(0.06 * screen_size[1])
        self.stats_font = pygame.font.Font(pygame.font.get_default_font(), int(0.7 * font_height))
        self.clock = pygame.time.Clock()
        self.base_speed = 60
        self.speed_multiplier = 1

        # Background set up
        self.bg = Background(self.tile_size)

        # Letter/number set up
        spritesheet = SpriteSheet(self.tile_size)
        self.letters = Letters(spritesheet)
        self.numbers = Numbers(spritesheet)

        # PlaybackPlayer set up
        player_args['spritesheet'] = spritesheet
        self.players = PlaybackPlayers(playback_folder, playback_player, player_args)
        if len(list(self.players)) > 1:
            raise Exception('One should not attempt to view playback of more than one PacMan at a time')
        self.pacman.initialise()

        # Ghosts set up
        if self.include_ghosts:
            blinky = BlinkySprite(self.pacman, spritesheet)
            pinky = PinkySprite(self.pacman, spritesheet)
            inky = InkySprite(self.pacman, spritesheet)
            clyde = ClydeSprite(self.pacman, spritesheet)
            self.ghosts = Ghosts(self.pacman, blinky, pinky, inky, clyde)
            self.ghosts.initialise()

            # If only ghosts then have all active from the start
            if all([not self.include_pacdots, not self.include_powerdots, not self.include_fruit]):
                self.ghosts.inky.inactive = False
                self.ghosts.clyde.inactive = False

        # Dot set up
        if self.include_pacdots or self.include_powerdots:        
            self.pacdots = PacDots()

        # Fruit set up
        if self.include_fruit:
            self.fruit = FruitSprite(spritesheet)

    @property
    def pacman(self) -> PacMan:
        """Return the first (and will be only) member of self.players."""
        return self.players[0]
    
    def new_episode(self) -> None:
        """Return all game objects to starting state."""

        self.pacman.initialise()
        if self.include_ghosts:
            self.ghosts.initialise()

            # If only ghosts then have all active from the start
            if all([not self.include_pacdots, not self.include_powerdots, not self.include_fruit]):
                self.ghosts.inky.inactive = False
                self.ghosts.clyde.inactive = False
                return
            
        if self.include_pacdots or self.include_powerdots:
            self.pacdots = PacDots()
        if self.include_fruit:
            self.fruit.available = False


    def check_key_press(self) -> Direction:
        """Check for new key presses."""

        for event in pygame.event.get():

            if event.type == pygame.QUIT: 
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RIGHT:
                    self.players.generation += 1
                    self.new_episode()
                elif event.key == pygame.K_LEFT:
                    self.players.generation -= 1
                    self.new_episode()

                elif event.key == pygame.K_UP:
                    self.players.species_no += 1
                    self.new_episode()
                elif event.key == pygame.K_DOWN:
                    self.players.species_no -= 1
                    self.new_episode()

                elif event.key == pygame.K_j:
                    self.speed_multiplier = max(1, self.speed_multiplier // 2)
                elif event.key == pygame.K_k:
                    self.speed_multiplier *= 2
    
    def advance(self) -> None:
        """Advance to the next frame."""

        # Move PacMan
        if self.include_ghosts:
            self.pacman.look(self.ghosts)
        else:
            self.pacman.look()
        move = self.pacman.think()
        self.pacman.move(move)

        # Move ghosts and check collisions
        if self.include_ghosts:
            self.ghosts.move()
            self.ghosts.check_collision()

        # Update pacdots
        if self.include_pacdots:
            dots_changed = False
            if self.pacdots.check_if_eaten(self.pacman):
                self.pacman.score += 10
                self.pacman.move_next = False
                dots_changed = True
        if self.include_powerdots:
            dots_changed = False
            if self.pacdots.check_if_powered(self.pacman):
                self.pacman.score += 50
                self.pacman.move_next = False
                self.ghosts.frightened = True
                dots_changed = True

        # Check for dot checkpoints 
        if self.include_pacdots and dots_changed:

            if self.include_ghosts:
                if self.pacdots.remaining == 214:
                    self.ghosts.inky.inactive = False
                elif self.pacdots.remaining == 184:
                    self.ghosts.clyde.inactive = False
                elif self.pacdots.remaining == self.ghosts.blinky.elroy_first_threshold:
                    self.ghosts.blinky.elroy = 1
                elif self.pacdots.remaining == self.ghosts.blinky.elroy_second_threshold:
                    self.ghosts.blinky.elroy = 2

            if self.include_fruit:
                if self.pacdots.remaining == self.fruit.first_threshold:
                    self.fruit.available = True
                elif self.pacdots.remaining == self.fruit.second_threshold:
                    self.fruit.available = True

        # Update fruit
        if self.include_fruit:
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
        if self.include_pacdots:
            for dot in self.pacdots.dots:
                dot_position = to_pixels(dot, self.tile_size)
                pygame.draw.circle(self.screen, 'pink', dot_position, self.tile_size*0.2)

        if self.include_powerdots:
            for dot in self.pacdots.power_dots:
                dot_position = to_pixels(dot, self.tile_size)
                pygame.draw.circle(self.screen, 'pink', dot_position, self.tile_size*0.35)

        # Draw fruit
        if self.include_fruit and self.fruit.available:
            self.fruit.draw(self.screen)

        # Ghosts next
        if self.include_ghosts:
            for ghost in self.ghosts:
                if not ghost.inactive:
                    ghost.draw(self.screen, self.tile_size)

        # Finally pacman
        self.pacman.draw(self.screen, self.tile_size)

        # Write up-to-date score
        self.letters.draw_score(self.screen)
        self.numbers.draw_score(self.screen, self.pacman.score)

        # Show the gen
        gen = self.stats_font.render(f'Gen: {self.players.generation}', True, 'white')
        gen_rect = gen.get_rect(topleft=(self.tile_size, self.tile_size))
        self.screen.blit(gen, gen_rect)

        # Show the species_no
        species_no = self.stats_font.render(f'Species: {self.players.species_no + 1}', True, 'white')
        species_no_rect = gen.get_rect(topleft=(self.tile_size, 3 * self.tile_size))
        self.screen.blit(species_no, species_no_rect)

        # Show the speed
        speed = self.stats_font.render(f'Speed: {self.speed_multiplier}x', True, 'white')
        speed_rect = speed.get_rect(topright=(29 * self.tile_size, self.tile_size))
        self.screen.blit(speed, speed_rect)

        # Update the screen
        pygame.display.flip()

    def run(self) -> None:
        """Run the main game loop."""

        while True:
            self.check_key_press()
            self.advance()
            self.update_screen()

            if self.pacman.dead:
                self.new_episode()

            self.clock.tick(self.base_speed * self.speed_multiplier)
