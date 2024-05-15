import neat

from pacman_ai_neat.player import Player
from pacman_ai_neat.phase import Phase
from pacman_ai_neat.phase_transition import phase_transition
from pacman_ai_neat.settings import settings


def main() -> None:

    phase = Phase[settings['phase'].upper()]

    # Carry out phase_transition if starting a new phase
    is_new_phase = settings['is_new_phase']
    if is_new_phase:
        phase_transition(phase, settings)

    # Set the playback folder
    playback_folder = settings['playback_settings']['save_folder']
    if playback_folder:
        settings['playback_settings']['save_folder'] += f'/{phase.name.lower()}'
    else:
        settings['playback_settings']['save_folder'] = f'playback/{phase.name.lower()}'

    neat.run(
        PlayerClass=Player,
        simulate=phase.simulator_function,
        settings=settings,
    )


if __name__ == '__main__':
    main()