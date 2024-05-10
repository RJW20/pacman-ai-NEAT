import neat

from pacman_ai_neat.only_dots import Player, simulate, settings


def main() -> None:

    neat.run(
        PlayerClass=Player,
        simulate=simulate,
        settings=settings,
    )


if __name__ == '__main__':
    main()