


import gym
import numpy as np
from simulation_environments import otter_simulation_environment
import pickle

import spinup



def get_env():
    return otter_simulation_environment()


# Initializes environment and agent
sim_env = otter_simulation_environment() # Simulation environment
result = spinup.ppo_pytorch(get_env, epochs=10_000)

print("\n\n")
print(result)
print("\n\n")

with open('ppo_result.pkl', 'wb') as file:
    pickle.dump(result, file)

