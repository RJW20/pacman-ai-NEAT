from pathlib import Path

from pacman_ai_neat.phase import Phase
from pacman_ai_neat.player import Player
from neat.population import Population


def phase_transition(new_phase: Phase, settings: dict) -> None:
    """Take the Population in settings['population_settings']['save_folder'] and reset the attributes."""

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

    # Overwrite the old save
    population.save()