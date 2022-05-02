import os
import pickle
import neat
import visualize
import gym
import numpy as np
from numpy import pi, tanh
import time

from simulation_environments import otter_simulation_environment

# load the winner
with open('neural_network_models/first_winner/winner', 'rb') as f:
    c = pickle.load(f)

print('Loaded genome:')
print(c)

# Load the config file, which is assumed to live in
# the same directory as this script.
local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config')
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)

net = neat.nn.FeedForwardNetwork.create(c, config)

visualize.draw_net(config, c, True)

env = otter_simulation_environment()
observation = env.reset()

done = False
while not done:
    action = net.activate(observation)
    action = np.array([action[0], action[1]], dtype=np.float64)
    action = 100*tanh(action)

    observation, reward, done = env.step(action)

    print("t:", env.t)
    print("action:", np.round(action, 2))
    print("")

    env.render()
    time.sleep(0.1)