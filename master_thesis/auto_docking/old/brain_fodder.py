
import numpy as np
from numpy import tanh
from copy import deepcopy
import time

from simulation_environments import otter_simulation_environment
from fourier_brain import brain





number_of_simulations = 100_000_000 # Number of simulations to run
number_of_brains = 10

number_of_attempts = 1
best_score = 0
final_scores = np.zeros([number_of_attempts, number_of_brains])




sim_env = otter_simulation_environment()
best_brain = brain(number_of_inputs=7, number_of_outputs=2)
test_brains = []
for n in range(number_of_brains):
    test_brains.append(brain(number_of_inputs=7, number_of_outputs=2))

    # Set random starting weights
    counter = 0
    for layer in range(len(test_brains[n].weights)):
        for i in range(np.shape(test_brains[n].weights[layer])[0]):
            for j in range(np.shape(test_brains[n].weights[layer])[1]):
                test_brains[n].weights[layer][i, j] = np.random.rand()
                if counter % 2 == 0:
                    test_brains[n].weights[layer][i, j] *= -1
                counter +=1






for simulation_number in range(number_of_simulations):

    print("-------------------------")
    print("Starting simulation:", simulation_number+1)
    print("")

    for n in range(len(test_brains)):
        # Mutate network
        if np.random.rand() < 0.1:
            test_brains[n].mutate("topology")
        else:
            if np.random.rand() < 0.5:
                test_brains[n].mutate("alter_weight", method="flip")
            else:
                test_brains[n].mutate("alter_weight", method="standard")

        observation = sim_env.reset()
        done = 0
        reward = 0
        score = 0

        # Simulates the environment
        while not done:
            action = 100*tanh(test_brains[n].forward(observation))
            next_observation, reward, done = sim_env.step(action)
            observation = next_observation
            score += reward

        final_scores[simulation_number%number_of_attempts][n] = score

    # Calculates average score for last simulations
    trailing_average_score = np.average(final_scores, axis=0)


    # Gradually increase number_of_attempts every log10 number of simulations
    number_of_attempts = int(np.log10(simulation_number+1)+1)
    while number_of_attempts > np.shape(final_scores)[0]:
        final_scores = np.r_[final_scores, [np.mean(trailing_average_score, axis=0)*np.ones(number_of_brains)]]



    # Prints information on the brains
    if (simulation_number+1) % 250 == 0:
        for brain_number in range(len(test_brains)):
            print("\n---")
            print("Test brain", brain_number)
            print(test_brains[brain_number].neuron_layers)
            print("---\n")
            time.sleep(1)


    # Replaces worst brain with best brain every (number_of_attempts) simulations
    if (simulation_number+1) % number_of_attempts == 0:
        test_brains[np.argmin(final_scores)] = deepcopy(best_brain)
        print("Replaced", np.argmin(final_scores))
        print("")

    # Saves the brain that performs the best
    if np.max(final_scores[simulation_number%number_of_attempts]) > best_score:
        best_brain = deepcopy(test_brains[np.argmax(final_scores[simulation_number%number_of_attempts])])
        best_score = np.max(final_scores[simulation_number%number_of_attempts])
        print("New record!")
        print("New best:", np.round(best_score, 3))
        print("")



    # Prints info
    trailing_average_score = np.average(final_scores, axis=0)
    print("Last", number_of_attempts, "attempts average:")
    print(np.round(trailing_average_score, 3))
    print("")
    print("Mean:  ", np.round(np.mean(trailing_average_score), 3))
    print("Winner:", np.argmax(final_scores[simulation_number%number_of_attempts]))
    print("Score: ", np.round(np.max(final_scores[simulation_number%number_of_attempts]), 3))
    print("Best:  ", np.round(best_score, 3))
    print("-------------------------")
    print("\n")













