import os
import pickle
import neat
import visualize
import gym
import numpy as np
from numpy import pi, tanh
import time
import pymap3d as pm

from otter.simulation_environments import otter_auto_docking_environment

def coords_to_xy(coordinates):
    lat = coordinates[0]
    lon = coordinates[1]

    SW_lat = 59 + (54/60)
    SW_lon = 10 + (41/60)

    e, n, u = pm.geodetic2enu(lat, lon, 0, SW_lat, SW_lon, 0)

    return[int(round(e)), int(round(n))]



def xy_to_coords(xy):
    x = xy[0]
    y = xy[1]

    SW_lat = 59 + (54/60)
    SW_lon = 10 + (41/60)

    lat, lon, alt = pm.enu2geodetic(x, y, 0, SW_lat, SW_lon, 0)

    return [lat, lon]




# load the winner
with open('auto_docking_temp_winner', 'rb') as f:
    c = pickle.load(f)

print('Loaded genome:')
print(c)

# Load the config file, which is assumed to live in
# the same directory as this script.
local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'auto_docking_config')
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)

net = neat.nn.FeedForwardNetwork.create(c, config)

#visualize.draw_net(config, c, True)

env = otter_auto_docking_environment()
observation = env.reset()
fitness = 0.0

done = False
while not done:

    action = net.activate(observation)
    action = np.array([action[0], action[1]], dtype=np.float64)
    action *= 100
    #action = 100*tanh(action)

    observation, reward, done = env.step(action)
    fitness += reward

    print("t:", env.t)
    print("action:", np.round(action, 2))
    print("pos:", np.round(env.eta[1], 2), np.round(env.eta[0], 2))
    print("yaw:", np.round(-env.eta[5], 2))
    print("d:", np.round(np.hypot(env.eta[1]-env.dock_position[0], env.eta[0]-env.dock_position[1]), 2))
    print("v:", np.round(env.total_speed, 2))
    print("a:", np.round(env.direction_to_destination, 2))
    print("a_d:", np.round(env.angular_difference_between_vehicle_and_dock, 2))
    print("")

    env.render()
    time.sleep(0.1)

print("fitness:", fitness)



