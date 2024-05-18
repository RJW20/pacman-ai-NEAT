import pygame

from pacman_app.background import Background
from pacman_app import PacMan, PacDots, Ghosts
from pacman_app.sprites import SpriteSheet, BlinkySprite, PinkySprite, InkySprite, ClydeSprite, FruitSprite
from pacman_app.sprites.letters import Letters
from pacman_app.sprites.numbers import Numbers
from pacman_app.map import Direction
from pacman_app.pixels import to_pixels

from neat import PlaybackPlayers
from neat.settings import settings_handler

from pacman_ai_neat.phase import Phase
from pacman_ai_neat.settings import settings
from pacman_ai_neat.playback_player import PlaybackPlayer


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
        player_args: dict,
        phase: Phase,
    ) -> None:
        
        # Set our current Phase
        match(phase):

            case Phase.ONLY_DOTS:
                self.new_episode = self.only_dots_new_episode
                self.advance = self.only_dots_advance
                self.update_screen = self.only_dots_update_screen

            case Phase.DOTS_AND_GHOSTS:
                self.new_episode = self.dots_and_ghosts_new_episode
                self.advance = self.dots_and_ghosts_advance
                self.update_screen = self.dots_and_ghosts_update_screen

            case Phase.FULL_GAME:
                self.new_episode = self.full_game_new_episode
                self.advance = self.full_game_advance
                self.update_screen = self.full_game_update_screen

        # Pygame set up
        width = 532
        self.tile_size = width // 28
        screen_size = (self.tile_size * 30, self.tile_size * 36)
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption(f'PacMan: Playback of Phase {phase.name}')
        pygame.font.init()
        font_height = int(0.04 * screen_size[1])
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

        # Ghosts set up
        blinky = BlinkySprite(self.pacman, spritesheet)
        pinky = PinkySprite(self.pacman, spritesheet)
        inky = InkySprite(self.pacman, spritesheet)
        clyde = ClydeSprite(self.pacman, spritesheet)
        self.ghosts = Ghosts(self.pacman, blinky, pinky, inky, clyde)

        # Fruit set up
        self.fruit = FruitSprite(spritesheet)

        self.new_episode()

    @property
    def pacman(self) -> PacMan:
        """Return the first (and will be only) member of self.players."""
        return self.players[0]
    
    def initialise_ghosts(self) -> None:
        """Initialise the Ghosts and ensure that they are referencing current self.pacman."""

        for ghost in self.ghosts:
            ghost.pacman = self.pacman
        self.ghosts.pacman = self.pacman
        self.ghosts.initialise()

    def only_dots_new_episode(self) -> None:
        """Start a new episode for Phase.ONLY_DOTS."""

        self.pacman.initialise()
        self.pacdots = PacDots()

    def dots_and_ghosts_new_episode(self) -> None:
        """Start a new episode for Phase.DOTS_AND_GHOSTS."""

        self.pacman.initialise()
        self.initialise_ghosts()
        self.pacdots = PacDots()

    def full_game_new_episode(self) -> None:
        """Start a new episode for Phase.FULL_GAME."""

        self.pacman.initialise()
        self.initialise_ghosts()
        self.pacdots = PacDots()
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
    
    def dot_ghost_threshold(self) -> None:
        """Check if enough PacDots have been eaten to release/update a Ghost."""

        if self.pacdots.remaining == 214:
            self.ghosts.inky.inactive = False
        elif self.pacdots.remaining == 184:
            self.ghosts.clyde.inactive = False
        elif self.pacdots.remaining == self.ghosts.blinky.elroy_first_threshold:
            self.ghosts.blinky.elroy = 1
        elif self.pacdots.remaining == self.ghosts.blinky.elroy_second_threshold:
            self.ghosts.blinky.elroy = 2

    def dot_fruit_threshold(self) -> None:
        """Check if enough PacDots have been eaten to make the Fruit available."""

        if self.pacdots.remaining == self.fruit.first_threshold:
            self.fruit.available = True
        elif self.pacdots.remaining == self.fruit.second_threshold:
            self.fruit.available = True

    def only_dots_advance(self) -> None:
        """Advance to the next frame in Phase.ONLY_DOTS."""

        self.advance_pacman()
        self.check_dots()

    def dots_and_ghosts_advance(self) -> None:
        """Advance to the next frame in Phase.DOTS_AND_GHOSTS."""

        self.advance_pacman()
        self.advance_ghosts()
        self.check_dots()
        self.dot_ghost_threshold()

    def full_game_advance(self) -> None:
        """Advance to the next frame in Phase.FULL_GAME."""

        self.advance_pacman()
        self.advance_ghosts()
        self.check_dots()
        self.check_power_dots()
        self.check_fruit()
        self.dot_ghost_threshold()
        self.dot_fruit_threshold()

    def draw_dots(self) -> None:
        """Draw the PacDots."""

        for dot in self.pacdots.dots:
            dot_position = to_pixels(dot, self.tile_size)
            pygame.draw.circle(self.screen, 'pink', dot_position, self.tile_size*0.2)

    def draw_power_dots(self) -> None:
        """Draw the PowerDots."""

        for dot in self.pacdots.power_dots:
            dot_position = to_pixels(dot, self.tile_size)
            pygame.draw.circle(self.screen, 'pink', dot_position, self.tile_size*0.35)

    def draw_fruit(self) -> None:
        """Draw the Fruit."""

        self.fruit.draw(self.screen)

    def draw_ghosts(self) -> None:
        """Draw the Ghosts."""

        for ghost in self.ghosts:
            if not ghost.inactive:
                ghost.draw(self.screen, self.tile_size)

    def draw_pacman(self) -> None:
        """Draw PacMan."""

        self.pacman.draw(self.screen, self.tile_size)

    def draw_score(self) -> None:
        """Draw the score."""

        self.letters.draw_score(self.screen)
        self.numbers.draw_score(self.screen, self.pacman.score)

    def write_stats(self) -> None:
        """Write the playback stats."""

        # Show the gen
        gen = self.stats_font.render(f'Gen: {self.players.generation}', True, 'white')
        gen_rect = gen.get_rect(topleft=(self.tile_size, 0.5 * self.tile_size))
        self.screen.blit(gen, gen_rect)

        # Show the species_no
        species_no = self.stats_font.render(f'Species: {self.players.species_no + 1}', True, 'white')
        species_no_rect = gen.get_rect(topleft=(self.tile_size, 1.5 * self.tile_size))
        self.screen.blit(species_no, species_no_rect)

        # Show the speed
        speed = self.stats_font.render(f'Speed: {self.speed_multiplier}x', True, 'white')
        speed_rect = speed.get_rect(topright=(29 * self.tile_size, 0.5 * self.tile_size))
        self.screen.blit(speed, speed_rect)

    def only_dots_update_screen(self) -> None:
        """Draw the current frame to the screen in Phase.ONLY_DOTS."""

        self.bg.draw(self.screen)
        self.draw_dots()
        self.draw_pacman()
        self.draw_score()
        self.write_stats()
        pygame.display.flip()

    def dots_and_ghosts_update_screen(self) -> None:
        """Draw the current frame to the screen in Phase.DOTS_AND_GHOSTS."""

        self.bg.draw(self.screen)
        self.draw_dots()
        self.draw_ghosts()
        self.draw_pacman()
        self.draw_score()
        self.write_stats()
        pygame.display.flip()

    def full_game_update_screen(self) -> None:
        """Draw the current frame to the screen in Phase.FULL_GAME."""

        self.bg.draw(self.screen)
        self.draw_dots()
        self.draw_power_dots()
        self.draw_fruit()
        self.draw_ghosts()
        self.draw_pacman()
        self.draw_score()
        self.write_stats()
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


def playback() -> None:

    handled_settings = settings_handler(settings, silent=True)

    phase = Phase[settings['phase'].upper()]
    playback_folder = handled_settings['playback_settings']['save_folder'] + f'/{phase.name.lower()}'
    player_args = handled_settings['player_args']
    pb = Playback(playback_folder, PlaybackPlayer, player_args, phase)
    pb.run()