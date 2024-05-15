from pathlib import Path

from pacman_ai_neat.phase import Phase
from pacman_ai_neat.player import Player
from neat.population import Population


def phase_transition(new_phase: Phase, settings: dict) -> None:
    """Take the Population in settings['population_settings']['save_folder'] and:
    - reset the attributes,
    - remove the species,
    - replace the Genomes with mutations of the original's best.
    """

    # Load the old Population
    try:
        load_folder = Path(settings['population_settings']['save_folder'])
        population = Population.load(Player, settings, load_folder)
    except KeyError:
        raise Exception('Unable to find the save of the previous phase, if this is the first phase ' + \
                        'please set settings[\'is_new_phase\'] to False.')
    
    # Reset the attributes
    population.generation = 1
    population.staleness = 0
    population.best_fitness = 0

    # Get the best Genome
    population.species.sort(key=lambda specie: specie.best_fitness, reverse=True)
    best_genome = population.species[0].rep
    best_player = population.player_factory.empty_player()
    best_player.fitness = 1
    best_player.genome = best_genome

    # Remove the species
    population.species = []

    # Create mutations of the best Genome
    population.players = population.player_factory.generate_offspring(
        parents=[best_player],
        total=population._size,
        history=population.history,
    )

    # Overwrite the old save
    population.save()