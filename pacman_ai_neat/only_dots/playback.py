from pacman_ai_neat.playback import Playback
from pacman_ai_neat.only_dots.settings import settings
from pacman_ai_neat.only_dots.playback_player import PlaybackPlayer

from neat.settings import settings_handler


def playback() -> None:

    handled_settings = settings_handler(settings, silent=True)
    playback_folder = handled_settings['playback_settings']['save_folder']
    player_args = handled_settings['player_args']
    pb = Playback(
        playback_folder,
        PlaybackPlayer,
        player_args,
        False,
        True,
        False,
        False,
    )
    pb.run()


if __name__ == '__main__':
    playback()