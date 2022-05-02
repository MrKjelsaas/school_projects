


import tensorflow as tf
from tensorflow import keras
import tensorflow_probability as tfp
import numpy as np
import gym
import datetime as dt

from simulation_environments import otter_simulation_environment
import ppo



# Initializes environment and agent
sim_env = otter_simulation_environment() # Simulation environment
agent = ppo.Agent(input_size=17, number_of_actions=2) # Our PPO agent

N = 20 # Number of steps before we update network policy
n = 0 # Counter to check for update
number_of_simulations = 10 # Number of simulations to run
times_learned = 0 # Counter for number of times agent has learned
scores = [] # Saves all scores



# Begin the simulations
for simulation_number in range(number_of_simulations):

    observation = sim_env.reset()
    done = 0
    score = 0

    # Simulates untill end of simulation
    while not done:
        action, value = agent.choose_action(observation)
        next_observation, reward, done = sim_env.step(100*action)
        n += 1
        score += reward
        agent.remember(observation, action, value, reward, done)
        if n % N == 0:
            agent.learn()
            times_learned += 1

        observation = next_observation

    # Saves score
    scores.append(score)
    last_100_average_score = np.mean(scores[-100:]) # Average score of last 100 simulations

    print("-------------------------------")
    print("Simulation number", simulation_number)
    print("Scored", score)
    print("Last 100 average score:", last_100_average_score)
    print("-------------------------------")
    print("\n")





















