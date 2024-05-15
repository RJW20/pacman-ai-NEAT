import pygame

from pacman_app.map import Direction
from pacman_app.pixels import to_pixels

from pacman_ai_neat.player import Player


class PlaybackPlayer(Player):
    """PacMan with a Genome and Sprite for use in Playback."""

    def __init__(self, playback_player_args: dict) -> None:
        spritesheet = playback_player_args['spritesheet']
        super().__init__(playback_player_args)

        self.neutral = spritesheet.image_at(2, 0, 13, 1.8)
        self.up = [spritesheet.image_at(1, 2, 13, 1.8), spritesheet.image_at(0, 2, 13, 1.8)]
        self.right = [spritesheet.image_at(1, 0, 13, 1.8), spritesheet.image_at(0, 0, 13, 1.8)]
        self.down = [spritesheet.image_at(1, 3, 13, 1.8), spritesheet.image_at(0, 3, 13, 1.8)]
        self.left = [spritesheet.image_at(1, 1, 13, 1.8), spritesheet.image_at(0, 1, 13, 1.8)]
        self.sprite_count = -1
        self.repeat_count = 5
        
    @property
    def sprite(self) -> pygame.Surface:
        """Return the sprite corresponding to PacMan's current position and state."""

        self.sprite_count = (self.sprite_count + 1) % (4 * self.repeat_count)

        if self.sprite_count // self.repeat_count == 0:
            return self.neutral

        match(self.direction):
            case Direction.UP:
                sprite_list = self.up
            case Direction.RIGHT:
                sprite_list = self.right
            case Direction.DOWN:
                sprite_list = self.down
            case Direction.LEFT:
                sprite_list = self.left

        if self.sprite_count // self.repeat_count < 3:
            return sprite_list[self.sprite_count // self.repeat_count - 1]
        else:
            return sprite_list[0]
        
    def draw(self, surface: pygame.Surface, tile_size: int) -> None:
        """Draw self's current sprite onto the surface at the correct position."""

        rect = self.sprite.get_rect()
        rect.center = to_pixels(self.position, tile_size)
        surface.blit(self.sprite, rect)