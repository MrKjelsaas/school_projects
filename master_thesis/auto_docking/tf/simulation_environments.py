
# Standard libraries
import numpy as np
from numpy import pi
import matplotlib.pyplot as plt

# These files were collected from https://github.com/cybergalactic/PythonVehicleSimulator
from functions import plotVehicleStates, plotControls, simulate, gnc
from vehicles import otter





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















class otter_simulation_environment:

    def __init__(self):

        # Setting initial parameters

        # PPO learning
        self.reward = 0
        self.done = 0
        self.probabilitiy = 0
        self.value = 0

        # Vehicle
        self.vehicle = otter()
        self.eta = np.array([0, 0, 0, 0, 0, 0], dtype=np.float32)
        self.nu = self.vehicle.nu
        self.u_actual = self.vehicle.u_actual # Actual inputs, defined by otter class (that's what Fossen wrote)
        self.u_control = np.array([0, 0])

        # Dock
        self.dock_position = [27.5, -27.5]
        self.dock_angle = np.deg2rad(-135)

        # Obstacles
        self.obstacles = np.array([[23.75, -26.25],
                                   [28.75, -31.25],
                                   [31.25, -28.75],
                                   [26.25, -23.75]])

        # Observations
        self.vehicle_yaw = smallest_signed_angle_between(0, -self.eta[5])
        self.distance_between_vehicle_and_dock = np.hypot(self.eta[1]-self.dock_position[0], self.eta[0]-self.dock_position[1])
        self.angular_difference_between_vehicle_and_dock = smallest_signed_angle_between(self.vehicle_yaw, self.dock_angle)
        self.distance_to_closest_obstacle = np.inf
        for obstacle in self.obstacles:
           d = np.hypot(self.eta[1]-obstacle[0], self.eta[0]-obstacle[1])
           if d < self.distance_to_closest_obstacle:
               self.distance_to_closest_obstacle = d
               self.angle_to_closest_obstacle = smallest_signed_angle_between(0, np.arctan2(obstacle[1]-self.eta[0], obstacle[0]-self.eta[1]) - pi/2 - self.vehicle_yaw)

        # Miscellaneous
        self.t = 0




    # Resets the environment to initial setting
    def reset(self):

        # PPO learning
        self.reward = 0
        self.done = 0
        self.probabilitiy = 0
        self.value = 0

        # Vehicle
        self.vehicle = otter()
        self.eta = np.array([0, 0, 0, 0, 0, 0], dtype=np.float32)
        self.nu = self.vehicle.nu
        self.u_actual = self.vehicle.u_actual # Actual inputs, defined by otter class (that's what Fossen wrote)
        self.u_control = np.array([0, 0])

        self.t = 0

        return self.get_state()



    # Moves the simulation one step forward (1 second)
    def step(self, action, sample_time=0.1):

        # Perform the actual integration
        for t_step in range(int(1/sample_time)):
            [self.nu, self.u_actual] = self.vehicle.dynamics(self.eta, self.nu, self.u_actual, action, sample_time)
            self.eta = gnc.attitudeEuler(self.eta, self.nu, sample_time)

        self.t += 1

        new_state = self.get_state()
        reward, done = self.evaluate_state()

        return new_state, reward, done



    def get_state(self):

        # Gathers observations
        self.vehicle_yaw = smallest_signed_angle_between(0, -self.eta[5])
        self.distance_between_vehicle_and_dock = np.hypot(self.eta[1]-self.dock_position[0], self.eta[0]-self.dock_position[1])
        self.angular_difference_between_vehicle_and_dock = smallest_signed_angle_between(self.vehicle_yaw, self.dock_angle)

        self.distance_to_closest_obstacle = np.inf
        for obstacle in self.obstacles:
            d = np.hypot(self.eta[1]-obstacle[0], self.eta[0]-obstacle[1])
            if d < self.distance_to_closest_obstacle:
                self.distance_to_closest_obstacle = d
                self.angle_to_closest_obstacle = smallest_signed_angle_between(0, np.arctan2(obstacle[1]-self.eta[0], obstacle[0]-self.eta[1]) - pi/2 - self.vehicle_yaw)

        # Creates the state array
        state = np.empty(0)

        # Appends observations to state
        for n in range(len(self.nu)):
            state = np.append(state, self.nu[n]) # Velocities
        for n in range(len(self.eta)):
            state = np.append(state, self.eta[n]) # Positions/orientations

        state = np.append(state, self.distance_between_vehicle_and_dock) # Distance to dock
        state = np.append(state, self.angular_difference_between_vehicle_and_dock) # Angular difference between dock and vehicle (how parallel they are)
        state = np.append(state, smallest_signed_angle_between(0, np.arctan2(self.dock_position[1]-self.eta[0], self.dock_position[0]-self.eta[1]) - pi/2 - self.vehicle_yaw)) # Which direction the dock is in
        state = np.append(state, self.distance_to_closest_obstacle) # Distance to closest obstacle
        state = np.append(state, self.angle_to_closest_obstacle) # Angle to closest obstacle

        return state



    # Determines reward and termination status
    def evaluate_state(self):

        # Intermediate rewards
        self.reward = 50*np.exp(-self.distance_between_vehicle_and_dock/10)
        if self.distance_between_vehicle_and_dock < 1: # Adds reward for angle if close enough
            self.reward += 50*np.exp(-abs(self.angular_difference_between_vehicle_and_dock)/pi)
        self.done = 0

        # Check for timeout
        if self.t >= 120:
            self.done = 1
            return self.reward, self.done

        # Check if Otter went out of bounds
        if not (-50 < self.eta[0] < 50 and -50 < self.eta[1] < 50):
            self.done = 1
            return self.reward, self.done

        # Check if Otter crashed with the dock
        vehicle_crashed = False
        vehicle_corners = get_vehicle_corners(self.eta)

        for corner in vehicle_corners:
            x, y = corner[0], corner[1]
            if 28.75 <= x < 31.35:
                if y < x-60:
                    vehicle_crashed = True

            if 0 <= x < 28.75:
                if (y < x-50) and (y < -x-2.5):
                    vehicle_crashed = True

            if 26.25 <= x < 50:
                if (y < x-50) and (y > -x+2.5):
                    vehicle_crashed = True

        if vehicle_crashed == True:
            self.reward -= np.exp(abs(self.nu[0]))
            self.done = 1
        return self.reward, self.done








































if __name__ == "__main__":


    sim_env = otter_simulation_environment()

    sim_env.reset()

    print(sim_env.get_state(), "\n")

    for i in range(10):
        sim_env.step([100, 100])

    print(sim_env.get_state())








