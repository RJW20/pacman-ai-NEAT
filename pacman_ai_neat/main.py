import neat

from pacman_ai_neat.player import Player
from pacman_ai_neat.phase import Phase
from pacman_ai_neat.settings import settings


def main() -> None:

    phase = Phase[settings['phase'].upper()]

    neat.run(
        PlayerClass=Player,
        simulate=phase.simulator_function,
        settings=settings,
    )


if __name__ == '__main__':
    main()