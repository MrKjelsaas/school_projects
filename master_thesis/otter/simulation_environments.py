
# Standard libraries
import numpy as np
from numpy import pi
import matplotlib.pyplot as plt
import time
import cv2
import gym
import pymap3d as pm
from copy import copy

# These files were collected from https://github.com/cybergalactic/PythonVehicleSimulator
from functions import plotVehicleStates, plotControls, simulate, gnc
from vehicles import otter
from path_planning.a_star_algorithm import a_star


ocean_lab_dock_coordinates = [59.90895368229298, 10.722063882911693]
tjuvholmen_swimming_pier_coordinates = [59.9059, 10.7184]
bygdoeynes_dock_coordinates = [59.9046, 10.7000]



# Used to find the difference between two angles
def smallest_signed_angle_between(x, y):
    a = (x - y) % (2*pi)
    b = (y - x) % (2*pi)
    return -a if a < b else b



# Used to visualize, and find position of corners of the vehicle
def rotate_z(p, theta):
    R_z = np.array([[np.cos(theta), -np.sin(theta), 0],
                  [np.sin(theta), np.cos(theta),  0],
                  [0,             0,              1]])

    return np.dot(R_z, p)



# Returns the position of the vehicle corners
def get_vehicle_corners(eta, vehicle="otter"):
    if vehicle == "otter":
        vehicle_length = 2.0
        vehicle_width = 1.08

    x = eta[1]
    y = eta[0]
    yaw = -eta[5]
    left_back_corner = rotate_z(np.array([-vehicle_width/2, -vehicle_length/2, 0]), yaw)[:2] + np.array([x, y])
    left_front_corner = rotate_z(np.array([-vehicle_width/2, vehicle_length/2, 0]), yaw)[:2] + np.array([x, y])
    right_front_corner = rotate_z(np.array([vehicle_width/2, vehicle_length/2, 0]), yaw)[:2] + np.array([x, y])
    right_back_corner = rotate_z(np.array([vehicle_width/2, -vehicle_length/2, 0]), yaw)[:2] + np.array([x, y])

    return [left_back_corner, left_front_corner, right_front_corner, right_back_corner]



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

















class otter_simulation_environment:

    def __init__(self):

        # Setting initial parameters

        # Miscellaneous
        self.t = 0

        # AI
        self.reward = 0
        self.done = 0

        # Vehicle
        self.vehicle = otter()
        self.starting_position = [59.90878881249425, 10.721071764313887]
        self.eta = np.array([0, 0, 0, 0, 0, 0], dtype=np.float32)
        self.eta[0] = coords_to_xy(self.starting_position)[1] + 5*np.random.rand() - 2.5
        self.eta[1] = coords_to_xy(self.starting_position)[0] + 5*np.random.rand() - 2.5
        self.eta[5] = -(pi/4)*np.random.rand()

        self.nu = self.vehicle.nu
        self.u_actual = self.vehicle.u_actual # Actual inputs, defined by otter class (that's what Fossen wrote)
        self.u_control = np.array([0, 0])
        self.vehicle_length = 2.0
        self.vehicle_width = 1.08
        self.total_speed = np.sqrt(sum(self.nu**2))

        # Route/destination
        self.dock_position = coords_to_xy(ocean_lab_dock_coordinates)
        self.dock_entrance = coords_to_xy([59.90899726728072, 10.721982441177916])
        self.waypoint_acceptance_radius = 2 # Otter needs to be within this distance of waypoint to approve it
        self.obstacle_safety_margin = 2
        e, n, u = pm.geodetic2enu(xy_to_coords(self.dock_position)[0], xy_to_coords(self.dock_position)[1], 0, xy_to_coords(self.dock_entrance)[0], xy_to_coords(self.dock_entrance)[1], 0)
        self.dock_angle = np.arctan2(n, e) - pi/2
        self.waypoints = np.array([])
        self.waypoint_angles = []
        self.generate_binary_map()
        self.plan_route()

        # Observations
        self.vehicle_yaw = smallest_signed_angle_between(0, -self.eta[5])
        self.distance_between_vehicle_and_dock = np.hypot(self.eta[1]-self.dock_position[0], self.eta[0]-self.dock_position[1])
        self.distance_between_vehicle_and_destination = np.hypot(self.eta[1]-self.destination[0], self.eta[0]-self.destination[1])
        self.angular_difference_between_vehicle_and_destination = smallest_signed_angle_between(self.vehicle_yaw, self.destination_angle)
        self.angular_difference_between_vehicle_and_dock = smallest_signed_angle_between(self.vehicle_yaw, self.dock_angle)
        self.thruster_force_difference = abs(self.u_actual[0]) - abs(self.u_actual[1])

        # Required for using it as an OpenAI Gym environment
        #self.observation_space = gym.spaces.box.Box(np.array([-2, -2, 0, 0, 0]), np.array([2, 2, 100, pi, pi]))
        #self.action_space = gym.spaces.box.Box(np.array([-100, -100]), np.array([100, 100]))








    # Resets the environment to initial setting
    def reset(self):

        # Miscellaneous
        self.t = 0

        # AI
        self.reward = 0
        self.done = 0

        # Vehicle
        self.vehicle = otter()
        self.eta = np.array([0, 0, 0, 0, 0, 0], dtype=np.float32)
        self.eta[0] = coords_to_xy(self.starting_position)[1] + 5*np.random.rand() - 2.5
        self.eta[1] = coords_to_xy(self.starting_position)[0] + 5*np.random.rand() - 2.5
        self.eta[5] = -(pi/4)*np.random.rand()

        self.nu = self.vehicle.nu
        self.u_actual = self.vehicle.u_actual # Actual inputs, defined by otter class (that's what Fossen wrote)
        self.u_control = np.array([0, 0])
        self.total_speed = np.sqrt(sum(self.nu**2))

        self.waypoints = np.array([])
        self.waypoint_angles = []
        #self.generate_binary_map()
        self.plan_route()

        # Observations
        self.vehicle_yaw = smallest_signed_angle_between(0, -self.eta[5])
        self.distance_between_vehicle_and_dock = np.hypot(self.eta[1]-self.dock_position[0], self.eta[0]-self.dock_position[1])
        self.distance_between_vehicle_and_destination = np.hypot(self.eta[1]-self.destination[0], self.eta[0]-self.destination[1])
        self.angular_difference_between_vehicle_and_destination = smallest_signed_angle_between(self.vehicle_yaw, self.destination_angle)
        self.angular_difference_between_vehicle_and_dock = smallest_signed_angle_between(self.vehicle_yaw, self.dock_angle)
        self.thruster_force_difference = abs(self.u_actual[0]) - abs(self.u_actual[1])

        return self.get_state()



    # Moves the simulation one step forward (1 second)
    def step(self, action, sample_time=0.1):

        # Perform the actual integration
        for t_step in range(int(1/sample_time)):
            [self.nu, self.u_actual] = self.vehicle.dynamics(self.eta, self.nu, self.u_actual, action, sample_time)
            self.eta = gnc.attitudeEuler(self.eta, self.nu, sample_time)

        self.t += 1

        reward, done = self.evaluate_state()
        self.plan_route()
        new_state = self.get_state()

        return new_state, reward, done#, 0 Add the zero if using OpenAI Gym algorithms



    # Returns observation
    def get_state(self):

        # Gathers observations
        self.vehicle_yaw = smallest_signed_angle_between(0, -self.eta[5])
        self.distance_between_vehicle_and_dock = np.hypot(self.eta[1]-self.dock_position[0], self.eta[0]-self.dock_position[1])
        self.distance_between_vehicle_and_destination = np.hypot(self.eta[1]-self.destination[0], self.eta[0]-self.destination[1])
        self.angular_difference_between_vehicle_and_dock = smallest_signed_angle_between(self.vehicle_yaw, self.dock_angle)
        self.angular_difference_between_vehicle_and_destination = smallest_signed_angle_between(self.vehicle_yaw, self.destination_angle)
        self.direction_to_destination = smallest_signed_angle_between(0, np.arctan2(self.destination[1]-self.eta[0], self.destination[0]-self.eta[1]) - pi/2 - self.vehicle_yaw)
        self.thruster_force_difference = abs(self.u_actual[0]) - abs(self.u_actual[1])
        self.total_speed = np.sqrt(sum(self.nu**2))

        state = np.array([#self.nu[0], # Surge
                          #-self.nu[5], # Yaw rate
                          #self.total_speed, # Root of squared sum of all movements (translational and rotational)
                          #self.distance_between_vehicle_and_dock, # Distance to dock
                          self.distance_between_vehicle_and_destination, # Distance to next waypoint
                          #self.angular_difference_between_vehicle_and_dock, # Angular difference between dock and vehicle (how parallel they are)
                          self.angular_difference_between_vehicle_and_destination, # Angular difference between destination and vehicle (how parallel they are)
                          self.direction_to_destination, # Which direction the destination is in
                          #self.thruster_force_difference
                          ])

        state[0] /= 1
        state[1] /= pi
        state[2] /= pi

        return state



    # Determines reward and termination status
    def evaluate_state(self):
        self.done = 0
        self.reward = 0

        self.total_speed = np.sqrt(sum(self.nu**2))
        self.vehicle_yaw = smallest_signed_angle_between(0, -self.eta[5])
        self.thruster_force_difference = abs(self.u_actual[0]) - abs(self.u_actual[1])
        self.direction_to_destination = smallest_signed_angle_between(0, np.arctan2(self.destination[1]-self.eta[0], self.destination[0]-self.eta[1]) - pi/2 - self.vehicle_yaw)
        d = np.hypot(self.dock_position[0]-self.eta[1], self.dock_position[1]-self.eta[0])
        a = smallest_signed_angle_between(self.vehicle_yaw, self.dock_angle)
        v = self.total_speed

        # Reward based on distance to dock
        self.reward += np.exp(-d/50)
        if d < 1:
            self.reward += np.exp(-abs(a)/pi)

        # Punish too high velocity or yaw rate
        self.reward -= 0.1*np.exp(-abs(v)/3)**2
        self.reward -= 0.1*np.exp(-abs(self.nu[5])/0.326)**2

        # Check for timeout
        if self.t >= 300:
            self.done = 1
            return self.reward, self.done

        # Check if Otter went out of bounds
        if not (0 < self.eta[1] < self.binary_map.shape[0] and 0 < self.eta[0] < self.binary_map.shape[1]):
            self.done = 1
            return self.reward, self.done

        # Check if Otter crashed with the dock
        vehicle_crashed = False
        vehicle_corners = get_vehicle_corners(self.eta)

        for corner in vehicle_corners:
            x, y = corner[0], corner[1]
            if self.binary_map[int(round(x)), int(round(y))]:
                vehicle_crashed = True

        if vehicle_crashed == True:
            self.reward = -100*((self.total_speed/3)**2)
            #self.reward = -100
            self.done = 1

        return self.reward, self.done



    # Draws the position of the Otter on a matplotlib figure
    def render(self):

        render_im = copy(self.render_map)

        x_lower = coords_to_xy([59.90673840232716, 10.716646935910088])[0]
        y_lower = coords_to_xy([59.90673840232716, 10.716646935910088])[1]
        x_upper = coords_to_xy([59.90992925203723, 10.723220722807413])[0]
        y_upper = coords_to_xy([59.90992925203723, 10.723220722807413])[1]

        x = self.eta[1]
        y = self.eta[0]
        yaw = -self.eta[5]
        """
        left_back_corner = rotate_z(np.array([-self.vehicle_width/2, -self.vehicle_length/2, 0]), yaw)[:2] + np.array([x, y])
        left_front_corner = rotate_z(np.array([-self.vehicle_width/2, self.vehicle_length/2, 0]), yaw)[:2] + np.array([x, y])
        right_front_corner = rotate_z(np.array([self.vehicle_width/2, self.vehicle_length/2, 0]), yaw)[:2] + np.array([x, y])
        right_back_corner = rotate_z(np.array([self.vehicle_width/2, -self.vehicle_length/2, 0]), yaw)[:2] + np.array([x, y])
        """
        two_meters_ahead = rotate_z(np.array([0, 2, 0]), yaw)[:2] + np.array([x, y])

        render_im[int(round(x)), int(round(y))] = 1
        #render_im[int(round(two_meters_ahead[0])), int(round(two_meters_ahead[1]))] = 1
        for waypoint in self.waypoints:
            render_im[int(waypoint[0]), int(waypoint[1])] = 1

        render_im = render_im[x_lower:x_upper, y_lower:y_upper]
        render_im = np.rot90(render_im)
        render_im = cv2.resize(render_im, None, fx=3, fy=2)

        cv2.imshow("Map", render_im)
        cv2.waitKey(1)



    # Loads binary maps where 0 is water and 1 is land
    def generate_binary_map(self):
        # "Baseline" map, used for collision checking
        self.binary_map = np.loadtxt('path_planning/binary_map.csv')

        # Used for path planning
        # An added "safety margin" of ca two meters is added to each obstacle
        self.planning_map = np.loadtxt('path_planning/planning_map.csv')

        # Used for rendering
        self.render_map = copy(self.binary_map)






    # Creates a list of waypoints using A*
    def plan_route(self):
        x = int(round(self.eta[1]))
        y = int(round(self.eta[0]))

        # Can't calculate route if out of bounds
        if not 0 < x < self.planning_map.shape[0] or not 0 < y < self.planning_map.shape[1]:
            return

        # Won't bother calculating if we're standing on land since it's not gonna work anyway
        if not self.planning_map[x, y]:

            # Check if we are inside the dock
            d = np.hypot(self.eta[1]-self.dock_position[0], self.eta[0]-self.dock_position[1])
            if d < np.hypot(self.dock_position[0]-self.dock_entrance[0], self.dock_position[1]-self.dock_entrance[1]):
                next_waypoints = np.asarray(a_star(self.planning_map, (x, y), tuple(self.dock_position)))
                if next_waypoints.size >= 2:
                    self.waypoints = next_waypoints

            # "Normal" path planning
            else:
                # Plan route to dock entrance
                next_waypoints = np.asarray(a_star(self.planning_map, (x, y), tuple(self.dock_entrance)))
                if next_waypoints.size >= 2:
                    self.waypoints = next_waypoints

                    # Plan route from dock entrance to dock centre
                    next_waypoints = np.asarray(a_star(self.planning_map, tuple(self.dock_entrance), tuple(self.dock_position)))[1:, :]
                    for n in range(next_waypoints.shape[0]):
                        self.waypoints = np.vstack((self.waypoints, next_waypoints[n]))

        # Remove first waypoints that are closer than waypoint acceptance radius
        while True:
            if self.waypoints.size <= 2:
                break
            d = np.hypot(self.eta[1]-self.waypoints[0, 0], self.eta[0]-self.waypoints[0, 1])
            if d < self.waypoint_acceptance_radius:
                    self.waypoints = self.waypoints[1:, :]
            else:
                break

        # Update waypoint angles and set destination
        self.set_waypoint_angles()
        self.set_next_destination()





    # Adds an obstacle to the binary map
    def add_obstacle(self, obstacle_position, radius=5, boundary="circle"):
        x = obstacle_position[0]
        y = obstacle_position[1]

        for dx in range(-int(round(radius)), int(round(radius+1))):
            for dy in range(-int(round(radius)), int(round(radius+1))):
                if (not 0 <= x+dx < self.binary_map.shape[0]) or (not 0 <= y+dy < self.binary_map.shape[1]):
                    continue

                if boundary=="box":
                    self.render_map[x+dx, y+dy] = 1
                    self.binary_map[x+dx, y+dy] = 1
                    for ddx in range(-self.obstacle_safety_margin, self.obstacle_safety_margin+1):
                        for ddy in range(-self.obstacle_safety_margin, self.obstacle_safety_margin+1):
                            self.planning_map[x+dx+ddx, y+dy+ddy] = 1
                elif boundary=="circle":
                    d = np.hypot(dx, dy)
                    if d <= radius:
                        self.render_map[x+dx, y+dy] = 1
                        self.binary_map[x+dx, y+dy] = 1
                        for ddx in range(-self.obstacle_safety_margin, self.obstacle_safety_margin+1):
                            for ddy in range(-self.obstacle_safety_margin, self.obstacle_safety_margin+1):
                                self.planning_map[x+dx+ddx, y+dy+ddy] = 1

        # Update path based on new environment
        self.plan_route()





    # Removes an obstacle from the binary map
    def remove_obstacle(self, obstacle_position, radius=5, boundary="circle"):
        x = obstacle_position[0]
        y = obstacle_position[1]

        for dx in range(-int(round(radius)), int(round(radius+1))):
            for dy in range(-int(round(radius)), int(round(radius+1))):
                if (not 0 <= x+dx < self.binary_map.shape[0]) or (not 0 <= y+dy < self.binary_map.shape[1]):
                    continue

                if boundary=="box":
                    self.render_map[x+dx, y+dy] = 0
                    self.binary_map[x+dx, y+dy] = 0
                    for ddx in range(-self.obstacle_safety_margin, self.obstacle_safety_margin+1):
                        for ddy in range(-self.obstacle_safety_margin, self.obstacle_safety_margin+1):
                            self.planning_map[x+dx+ddx, y+dy+ddy] = 0
                elif boundary=="circle":
                    d = np.hypot(dx, dy)
                    if d <= radius:
                        self.render_map[x+dx, y+dy] = 0
                        self.binary_map[x+dx, y+dy] = 0
                        for ddx in range(-self.obstacle_safety_margin, self.obstacle_safety_margin+1):
                            for ddy in range(-self.obstacle_safety_margin, self.obstacle_safety_margin+1):
                                self.planning_map[x+dx+ddx, y+dy+ddy] = 0

        # Update path based on new environment
        self.plan_route()




    # Sets the current destination to the next waypoint
    def set_next_destination(self):
        #self.waypoints = self.waypoints[1:, :]
        self.destination = self.waypoints[0]
        #self.waypoint_angles = self.waypoint_angles[1:]
        self.destination_angle = self.waypoint_angles[0]




    # Calculates the angle from waypoints
    def set_waypoint_angles(self):
        self.waypoint_angles = []
        for n in range(len(self.waypoints)-1):
            x = self.waypoints[n+1][0] - self.waypoints[n][0]
            y = self.waypoints[n+1][1] - self.waypoints[n][1]
            angle = np.arctan2(y, x) - pi/2

            self.waypoint_angles.append(angle)

        self.waypoint_angles.append(self.dock_angle)








































class otter_path_following_environment(otter_simulation_environment):

    def get_state(self):

        # Gathers observations
        self.total_speed = np.sqrt(sum(self.nu**2))
        self.vehicle_yaw = smallest_signed_angle_between(0, -self.eta[5])
        self.distance_between_vehicle_and_dock = np.hypot(self.eta[1]-self.dock_position[0], self.eta[0]-self.dock_position[1])
        self.distance_between_vehicle_and_destination = np.hypot(self.eta[1]-self.destination[0], self.eta[0]-self.destination[1])
        self.angular_difference_between_vehicle_and_dock = smallest_signed_angle_between(self.vehicle_yaw, self.dock_angle)
        self.angular_difference_between_vehicle_and_destination = smallest_signed_angle_between(self.vehicle_yaw, self.destination_angle)
        self.direction_to_destination = smallest_signed_angle_between(0, np.arctan2(self.destination[1]-self.eta[0], self.destination[0]-self.eta[1]) - pi/2 - self.vehicle_yaw)

        state = np.array([self.nu[0], # Surge
                          self.distance_between_vehicle_and_destination, # Distance to next waypoint
                          self.angular_difference_between_vehicle_and_destination, # Angular difference between destination and vehicle (how parallel they are)
                          self.direction_to_destination, # Which direction the destination is in
                          ])

        state[0] /= 3
        state[1] /= 1
        state[2] /= pi
        state[3] /= pi

        return state



    def evaluate_state(self):
        self.done = 0
        self.reward = 0

        self.total_speed = np.sqrt(sum(self.nu**2))
        self.vehicle_yaw = smallest_signed_angle_between(0, -self.eta[5])
        self.direction_to_destination = smallest_signed_angle_between(0, np.arctan2(self.destination[1]-self.eta[0], self.destination[0]-self.eta[1]) - pi/2 - self.vehicle_yaw)
        d = np.hypot(self.dock_position[0]-self.eta[1], self.dock_position[1]-self.eta[0])
        a = smallest_signed_angle_between(self.vehicle_yaw, self.destination_angle)
        v = self.nu[0]

        # Reward wanted behavior
        if np.hypot(self.eta[1]-self.dock_entrance[0], self.eta[0]-self.dock_entrance[1]) < 1: # Reward for lining up with destination
            self.reward += np.exp(-abs(a))
        else: # Reward for heading towards destination
            r = ((pi/2)-abs(self.direction_to_destination)) / (pi/2)
            r *= max(0, min(v, 1))
            self.reward += r

        # Punish too high velocity or yaw rate
        self.reward -= 0.1*np.exp(-abs(v)/3)**2
        self.reward -= 0.1*np.exp(-abs(self.nu[5])/0.326)**2



        # Check for timeout
        if self.t >= 300:
            self.done = 1
            return self.reward, self.done

        # Check if Otter went out of bounds
        if not (0 < self.eta[1] < self.binary_map.shape[0] and 0 < self.eta[0] < self.binary_map.shape[1]):
            self.done = 1
            return self.reward, self.done

        # Check if Otter crashed
        vehicle_crashed = False
        vehicle_corners = get_vehicle_corners(self.eta)

        for corner in vehicle_corners:
            x, y = corner[0], corner[1]
            if self.binary_map[int(round(x)), int(round(y))]:
                vehicle_crashed = True

        if vehicle_crashed == True:
            self.reward = -100*((self.total_speed/3)**2)
            #self.reward = -100
            self.done = 1

        return self.reward, self.done



    def plan_route(self):
        x = int(np.round(self.eta[1]))
        y = int(np.round(self.eta[0]))

        # Can't calculate route if out of bounds
        if not 0 < x < self.planning_map.shape[0] or not 0 < y < self.planning_map.shape[1]:
            return

        # Won't bother calculating if we're standing on land since it's not gonna work anyway
        if not self.planning_map[x, y]:

            # Plan route to dock entrance
            next_waypoints = np.asarray(a_star(self.planning_map, (x, y), tuple(self.dock_entrance)))
            if next_waypoints.size >= 2:
                self.waypoints = next_waypoints

        # Remove first waypoints that are closer than waypoint acceptance radius
        while True:
            if self.waypoints.size <= 2:
                break
            d = np.hypot(self.eta[1]-self.waypoints[0, 0], self.eta[0]-self.waypoints[0, 1])
            if d < self.waypoint_acceptance_radius:
                    self.waypoints = self.waypoints[1:, :]
            else:
                break

        # Update waypoint angles and set destination
        self.set_waypoint_angles()
        self.set_next_destination()
















class otter_auto_docking_environment(otter_simulation_environment):

    def reset(self):

        # Miscellaneous
        self.t = 0

        # AI
        self.reward = 0
        self.done = 0

        # Vehicle
        self.vehicle = otter()
        self.eta = np.array([0, 0, 0, 0, 0, 0], dtype=np.float32)
        self.eta[0] = self.dock_entrance[1] + np.random.rand() - 0.5
        self.eta[1] = self.dock_entrance[0] + np.random.rand() - 0.5
        self.eta[5] = -self.dock_angle + (pi/4)*np.random.rand() - (pi/8)

        self.nu = self.vehicle.nu
        self.u_actual = self.vehicle.u_actual # Actual inputs, defined by otter class (that's what Fossen wrote)
        self.u_control = np.array([0, 0])
        self.total_speed = np.sqrt(sum(self.nu**2))

        self.waypoints = np.array([])
        self.waypoint_angles = []
        #self.generate_binary_map()
        self.plan_route()

        # Observations
        self.vehicle_yaw = smallest_signed_angle_between(0, -self.eta[5])
        self.distance_between_vehicle_and_dock = np.hypot(self.eta[1]-self.dock_position[0], self.eta[0]-self.dock_position[1])
        self.distance_between_vehicle_and_destination = np.hypot(self.eta[1]-self.destination[0], self.eta[0]-self.destination[1])
        self.angular_difference_between_vehicle_and_destination = smallest_signed_angle_between(self.vehicle_yaw, self.destination_angle)
        self.angular_difference_between_vehicle_and_dock = smallest_signed_angle_between(self.vehicle_yaw, self.dock_angle)
        self.thruster_force_difference = abs(self.u_actual[0]) - abs(self.u_actual[1])

        return self.get_state()



    def get_state(self):
        # Gathers observations
        self.vehicle_yaw = smallest_signed_angle_between(0, -self.eta[5])
        self.distance_between_vehicle_and_dock = np.hypot(self.eta[1]-self.dock_position[0], self.eta[0]-self.dock_position[1])
        self.distance_between_vehicle_and_destination = np.hypot(self.eta[1]-self.destination[0], self.eta[0]-self.destination[1])
        self.angular_difference_between_vehicle_and_dock = smallest_signed_angle_between(self.vehicle_yaw, self.dock_angle)
        self.angular_difference_between_vehicle_and_destination = smallest_signed_angle_between(self.vehicle_yaw, self.destination_angle)
        self.direction_to_destination = smallest_signed_angle_between(0, np.arctan2(self.destination[1]-self.eta[0], self.destination[0]-self.eta[1]) - pi/2 - self.vehicle_yaw)
        self.thruster_force_difference = abs(self.u_actual[0]) - abs(self.u_actual[1])
        self.total_speed = np.sqrt(sum(self.nu**2))

        state = np.array([self.nu[0], # Surge
                          -self.nu[5], # Yaw rate
                          self.distance_between_vehicle_and_dock, # Distance to dock
                          self.angular_difference_between_vehicle_and_dock, # Angular difference between dock and vehicle (how parallel they are)
                          self.direction_to_destination, # Which direction the destination is in
                          ])

        state[0] /= 3
        state[1] /= 0.326
        state[2] /= 6.4
        state[3] /= pi
        state[4] /= pi

        return state



    def evaluate_state(self):
        self.done = 0
        self.reward = 0

        self.total_speed = np.sqrt(sum(self.nu**2))
        self.vehicle_yaw = smallest_signed_angle_between(0, -self.eta[5])
        self.thruster_force_difference = abs(self.u_actual[0]) - abs(self.u_actual[1])
        self.direction_to_destination = smallest_signed_angle_between(0, np.arctan2(self.destination[1]-self.eta[0], self.destination[0]-self.eta[1]) - pi/2 - self.vehicle_yaw)
        d = np.hypot(self.dock_position[0]-self.eta[1], self.dock_position[1]-self.eta[0])
        a = smallest_signed_angle_between(self.vehicle_yaw, self.dock_angle)
        v = self.nu[0]

        # Reward based on distance to dock
        r = np.exp(-d/3)
        r *= np.exp(-abs(a)/2)
        self.reward += r

        # Punish too high velocity or yaw rate
        self.reward -= 0.1*np.exp(-abs(v)/3)**2
        self.reward -= 0.1*np.exp(-abs(self.nu[5])/0.326)**2

        # Check for timeout
        if self.t >= 300:
            self.done = 1
            return self.reward, self.done

        # Check if Otter went out of bounds
        if not (0 < self.eta[1] < self.binary_map.shape[0] and 0 < self.eta[0] < self.binary_map.shape[1]):
            self.done = 1
            return self.reward, self.done

        # Check if Otter crashed with the dock
        vehicle_crashed = False
        vehicle_corners = get_vehicle_corners(self.eta)

        for corner in vehicle_corners:
            x, y = corner[0], corner[1]
            if self.binary_map[int(round(x)), int(round(y))]:
                vehicle_crashed = True

        if vehicle_crashed == True:
            self.reward = -100*((self.total_speed/3)**2)
            #self.reward = -100
            self.done = 1

        return self.reward, self.done



    def plan_route(self):
        x = int(np.round(self.eta[1]))
        y = int(np.round(self.eta[0]))

        # Can't calculate route if out of bounds
        if not 0 < x < self.planning_map.shape[0] or not 0 < y < self.planning_map.shape[1]:
            return

        # Won't bother calculating if we're standing on land since it's not gonna work anyway
        if not self.planning_map[x, y]:

            # Plan route to dock centre
            next_waypoints = np.asarray(a_star(self.planning_map, (x, y), tuple(self.dock_position)))
            if next_waypoints.size >= 2:
                self.waypoints = next_waypoints

        # Remove first waypoints that are closer than waypoint acceptance radius
        while True:
            if self.waypoints.size <= 2:
                break
            d = np.hypot(self.eta[1]-self.waypoints[0, 0], self.eta[0]-self.waypoints[0, 1])
            if d < self.waypoint_acceptance_radius:
                    self.waypoints = self.waypoints[1:, :]
            else:
                break

        # Update waypoint angles and set destination
        self.set_waypoint_angles()
        self.set_next_destination()





    def render(self):

        render_im = copy(self.render_map)

        x_lower = coords_to_xy([59.90882238055097, 10.721619898208425])[0]
        y_lower = coords_to_xy([59.90882238055097, 10.721619898208425])[1]
        x_upper = coords_to_xy([59.90918752849223, 10.722226816025234])[0]
        y_upper = coords_to_xy([59.90918752849223, 10.722226816025234])[1]

        x = self.eta[1]
        y = self.eta[0]
        yaw = -self.eta[5]
        """
        left_back_corner = rotate_z(np.array([-self.vehicle_width/2, -self.vehicle_length/2, 0]), yaw)[:2] + np.array([x, y])
        left_front_corner = rotate_z(np.array([-self.vehicle_width/2, self.vehicle_length/2, 0]), yaw)[:2] + np.array([x, y])
        right_front_corner = rotate_z(np.array([self.vehicle_width/2, self.vehicle_length/2, 0]), yaw)[:2] + np.array([x, y])
        right_back_corner = rotate_z(np.array([self.vehicle_width/2, -self.vehicle_length/2, 0]), yaw)[:2] + np.array([x, y])
        """
        two_meters_ahead = rotate_z(np.array([0, 2, 0]), yaw)[:2] + np.array([x, y])

        render_im[int(round(x)), int(round(y))] = 1
        #render_im[int(round(two_meters_ahead[0])), int(round(two_meters_ahead[1]))] = 1
        for waypoint in self.waypoints:
            render_im[int(waypoint[0]), int(waypoint[1])] = 1

        render_im = render_im[x_lower:x_upper, y_lower:y_upper]
        render_im = np.rot90(render_im)
        render_im = cv2.resize(render_im, None, fx=12, fy=9)

        cv2.imshow("Map", render_im)
        cv2.waitKey(1)
