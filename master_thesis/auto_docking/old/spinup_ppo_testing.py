

# AI libraries
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import gym
import numpy as np
from simulation_environments import otter_simulation_environment
import pickle

import spinup



with open('ppo_result.pkl', 'rb') as file:
    agent = pickle.load(file)

env = otter_simulation_environment()
observation = env.reset()

done = False
while not done:
    actions = agent.act(torch.as_tensor(obs, dtype=torch.float32))

    observation, reward, done, _ = env.step(actions)

    print("t:", env.t)
    print("action:", np.round(action, 2))
    print("")

    env.render()
    time.sleep(0.1)