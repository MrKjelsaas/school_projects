


import gym
import numpy as np
from simulation_environments import otter_simulation_environment
from ppo_learning import Agent




# Initializes environment and agent
sim_env = otter_simulation_environment() # Simulation environment
agent = Agent(n_actions=5, input_dims=(7,)) # Our PPO agent

N = 20 # Number of steps before we update network policy
n = 0 # Counter to check for update
number_of_simulations = 100_000 # Number of simulations to run
times_learned = 0 # Counter for number of times agent has learned
scores = [] # Saves all scores

action_table = [np.array([100, 100], dtype=np.float32),
                np.array([0, 0], dtype=np.float32),
                np.array([-100, -100], dtype=np.float32),
                np.array([-100, 100], dtype=np.float32),
                np.array([100, -100], dtype=np.float32)]


# Begin the simulations
for simulation_number in range(number_of_simulations):

    observation = sim_env.reset()
    done = 0
    score = 0

    # Simulates untill end of simulation
    while not done:
        action, probability, value = agent.choose_action(observation)
        next_observation, reward, done = sim_env.step(action_table[action])
        n += 1
        score += reward
        agent.remember(observation, action, probability, value, reward, done)
        if n % N == 0:
            agent.learn()
            times_learned += 1

        observation = next_observation

    # Saves score
    scores.append(score)
    last_100_average_score = np.mean(scores[-100:]) # Average score of last 100 simulations

    print("-------------------------------")
    print("Simulation number:", simulation_number)
    print("Score:            ", np.round(score, 2))
    print("Average score:    ", np.round(last_100_average_score, 2))
    print("-------------------------------")
    print("\n")