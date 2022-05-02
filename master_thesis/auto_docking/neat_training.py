
import multiprocessing
import os
import pickle

import neat
import numpy as np
from numpy import pi, tanh

from simulation_environments import otter_simulation_environment

runs_per_net = 5



# Use the NN network phenotype and the discrete actuator force function.
def eval_genome(genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    fitnesses = []

    for runs in range(runs_per_net):
        env = otter_simulation_environment()

        observation = env.reset()
        fitness = 0.0
        done = False
        while not done:

            action = net.activate(observation)
            action = np.array([action[0], action[1]], dtype=np.float64)
            action = 100*tanh(action)
            observation, reward, done = env.step(action)
            #fitness += reward

        fitness += reward
        fitnesses.append(fitness)

    return np.mean(fitnesses)


def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome, config)


def run():
    # Load the config file, which is assumed to live in
    # the same directory as this script.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    pop = neat.Population(config)
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.StdOutReporter(True))

    pe = neat.ParallelEvaluator(multiprocessing.cpu_count(), eval_genome)
    winner = pop.run(pe.evaluate)

    # Save the winner.
    with open('winner', 'wb') as f:
        pickle.dump(winner, f)

    print(winner)





if __name__ == '__main__':
    run()