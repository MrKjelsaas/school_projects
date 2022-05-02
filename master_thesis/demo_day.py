
# Standard libraries
import numpy as np
from numpy import round, pi
import time
import socket
import pickle
import os
import neat
import pymap3d as pm

# Our home-grown libraries
from otter import otter
from ship_dynamics import ship_dynamics_functions
from path_planning import a_star_algorithm
from path_planning.a_star_algorithm import a_star
from obstacle_detection import obstacle_detector
from otter.simulation_environments import otter_simulation_environment

ocean_lab_dock_coordinates = [59.90895368229298, 10.722063882911693]
tjuvholmen_swimming_pier_coordinates = [59.9059, 10.7184]
bygdoeynes_dock_coordinates = [59.9046, 10.7000]

print("Ocean lab:", ocean_lab_dock_coordinates)
print("Tjuvholmen swimming pier:", tjuvholmen_swimming_pier_coordinates)
print("Bygdøynes dock:", bygdoeynes_dock_coordinates)
print("")

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



# Used to find the difference between two angles
def smallest_signed_angle_between(x, y):
    a = (x - y) % (2*pi)
    b = (y - x) % (2*pi)
    return -a if a < b else b







speed_limit_coefficient = 0.6











# Load path following genome
print("Importing path following winner")
with open('path_following_winner', 'rb') as f:
    path_following_genome = pickle.load(f)

# Load the config file, which is assumed to live in
# the same directory as this script.
local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'path_following_config')
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)

path_following_net = neat.nn.FeedForwardNetwork.create(path_following_genome, config)

# Load auto docking genome
print("Importing auto docking winner")
with open('auto_docking_winner', 'rb') as f:
    auto_docking_genome = pickle.load(f)

# Load the config file, which is assumed to live in
# the same directory as this script.
local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'auto_docking_config')
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)

auto_docking_net = neat.nn.FeedForwardNetwork.create(auto_docking_genome, config)







print("Initializing Otter")
the_otter = otter.otter_usv()
the_otter.verbose = False # We don't need to see everything now

print("Connecting to Otter over TCP")
the_otter.establish_connection()

print("Setting initial values")
the_otter.update_values()
time.sleep(0.2)
the_otter.update_values()

print("Collecting maps")
the_otter.generate_binary_map()

print("Finding route to destination...")
the_otter.plan_route()
print("Found a route")
print("Beginning main loop")
print("-------------------------------")
print("\n\n")



last_time_reported = time.time()
mission = "Path following"
print("Starting path following procedure")
while mission == "Path following":

    # Check if we have reached the dock
    if the_otter.distance_to_dock < 7:
        mission = "Auto docking"
        print("Reached dock")
        break

    # Get latest info on state
    the_otter.update_values()
    time.sleep(0.2)

    #Check for obstacles
    if not the_otter.check_for_obstacle(): # If an obstacle is found, a new route is automatically planned
        # Plan route
        the_otter.plan_route()

    # Get auto docking state
    observation = the_otter.get_path_following_state()

    # Set thrusters
    action = path_following_net.activate(observation)
    action = np.array([action[0], action[1]], dtype=np.float64)
    action *= speed_limit_coefficient # Apply a coefficient to limit max speed
    the_otter.set_thrusters(action[0], action[1])

    # Report status
    if time.time() - last_time_reported > 3:

        print("")
        print("-----------------------------------------")
        print("Mission:................", mission)
        print("Observation:............", observation)
        print("Action:.................", action)
        print("Velocity:...............", the_otter.current_speed)
        print("Position:...............", the_otter.current_position)
        print("Yaw:....................", the_otter.yaw)
        print("Distance to destination:", the_otter.distance_between_vehicle_and_destination)
        print("-----------------------------------------")

        last_time_reported = time.time()





print("Starting auto docking procedure")
while mission == "Auto docking":

    # Check for acceptable parking
    if the_otter.distance_to_dock < 1:
        if the_otter.current_speed < 0.5:
            mission = None
            the_otter.drift()
            break

    # Get latest info on state
    the_otter.update_values()
    time.sleep(0.2)

    # Plan route
    the_otter.plan_route()

    # Get auto docking state
    observation = the_otter.get_auto_docking_state()

    # Set thrusters
    action = auto_docking_net.activate(observation)
    action = np.array([action[0], action[1]], dtype=np.float64)
    action *= speed_limit_coefficient # Apply a coefficient to limit max speed
    the_otter.set_thrusters(action[0], action[1])

    # Report status
    if time.time() - last_time_reported > 3:

        print("")
        print("-----------------------------------------")
        print("Mission:................", mission)
        print("Observation:............", observation)
        print("Action:.................", action)
        print("Velocity:...............", the_otter.current_speed)
        print("Position:...............", the_otter.current_position)
        print("Yaw:....................", the_otter.yaw)
        print("Distance to destination:", the_otter.distance_between_vehicle_and_destination)
        print("-----------------------------------------")

        last_time_reported = time.time()



print("\n")
print("How's my parking?\n")





print("Closing connection to Otter")
print("Done")
the_otter.close_connection()
