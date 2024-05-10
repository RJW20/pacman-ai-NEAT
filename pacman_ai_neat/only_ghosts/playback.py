from pacman_ai_neat.playback import Playback
from pacman_ai_neat.only_ghosts.settings import settings
from pacman_ai_neat.only_ghosts.playback_player import PlaybackPlayer

from neat.settings import settings_handler


def playback() -> None:

    handled_settings = settings_handler(settings, silent=True)
    playback_folder = handled_settings['playback_settings']['save_folder']
    player_args = handled_settings['player_args']
    pb = Playback(
        playback_folder,
        PlaybackPlayer,
        player_args,
        True,
        False,
        False,
        False,
    )
    pb.run()


if __name__ == '__main__':
    playback()