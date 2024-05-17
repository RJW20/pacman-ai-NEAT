import neat

from pacman_ai_neat.player import Player
from pacman_ai_neat.simulator import simulate
from pacman_ai_neat.settings import settings


def main() -> None:

    neat.run(
        PlayerClass=Player,
        simulate=simulate,
        settings=settings,
    )


if __name__ == '__main__':
    main()