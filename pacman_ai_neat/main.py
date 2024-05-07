import neat

from .only_ghosts import Player, simulate, settings


def main() -> None:

    neat.run(
        PlayerClass=Player,
        simulate=simulate,
        settings=settings,
    )


if __name__ == '__main__':
    main()