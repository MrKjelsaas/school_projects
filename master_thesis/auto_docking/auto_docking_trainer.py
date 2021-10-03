
# Standard libraries
import numpy as np
import matplotlib.pyplot as plt

# AI libraries
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

# These files were collected from https://github.com/cybergalactic/PythonVehicleSimulator
from functions import plotVehicleStates, plotControls, simulate, gnc
from vehicles import otter






class DeepQNetwork(nn.Module):
    def __init__(self, lr, input_dims, fc1_dims, fc2_dims, n_actions):
        super(DeepQNetwork, self).__init__()
        self.input_dims = input_dims
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.n_actions = n_actions
        self.fc1 = nn.Linear(*self.input_dims, self.fc1_dims)
        self.fc2 = nn.Linear(self.fc2_dims, self.fc2_dims)
        self.fc3 = nn.Linear(self.fc2_dims, self.n_actions)
        self.optimizer = optim.Adam(self.parameters(), lr=lr)
        self.loss = nn.MSELoss()
        self.device = T.device('coda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)

    def forward(self, state):
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        actions = self.fc3(x)

        return actions

class Agent():
    def __init__(self, gamma, epsilon, lr, input_dims, batch_size, n_actions, max_mem_size=100_000, eps_end=0.01, eps_dec=5e-4):
        self.gamma = gamma
        self.epsilon = epsilon
        self.eps_min = eps_end
        self.eps_dec = eps_dec
        self.lr = lr
        self.action_space = [i for i in range(n_actions)]
        self.mem_size = max_mem_size
        self.batch_size = batch_size
        self.mem_cntr = 0

        self.Q_eval = DeepQNetwork(self.lr, n_actions=n_actions, input_dims=input_dims, fc1_dims=256, fc2_dims=256)

        self.state_memory = np.zeros((self.mem_size, *input_dims), dtype=np.float32)
        self.new_state_memory = np.zeros((self.mem_size, *input_dims), dtype=np.float32)
        self.action_memory = np.zeros(self.mem_size, dtype=np.int32)
        self.reward_memory = np.zeros(self.mem_size, dtype=np.float32)
        self.terminal_memory = np.zeros(self.mem_size, dtype=np.bool)

    def store_transition(self, state, action, reward, new_state, done):
        index = self.mem_cntr % self.mem_size
        self.state_memory[index] = state
        self.new_state_memory[index] = new_state
        self.reward_memory[index] = reward
        self.action_memory[index] = action
        self.terminal_memory[index] = done

        self.mem_cntr += 1

    def choose_action(self, observation):
        if np.random.random() > self.epsilon:
            state = T.tensor([observation]).to(self.Q_eval.device)
            actions = self.Q_eval.forward(state)
            action = T.argmax(actions).item()
        else:
            action = np.random.choice(self.action_space)

        return action

    def learn(self):
        if self.mem_cntr < self.batch_size:
            return

        self.Q_eval.optimizer.zero_grad()

        max_mem = min(self.mem_cntr, self.mem_size)
        batch = np.random.choice(max_mem, self.batch_size, replace=False)

        batch_index = np.arange(self.batch_size, dtype=np.int32)

        state_batch = T.tensor(self.state_memory[batch]).to(self.Q_eval.device)
        new_state_batch = T.tensor(self.new_state_memory[batch]).to(self.Q_eval.device)
        reward_batch = T.tensor(self.reward_memory[batch]).to(self.Q_eval.device)
        terminal_batch = T.tensor(self.terminal_memory[batch]).to(self.Q_eval.device)

        action_batch = self.action_memory[batch]

        q_eval = self.Q_eval.forward(state_batch)[batch_index, action_batch]
        q_next = self.Q_eval.forward(new_state_batch)
        q_next[terminal_batch] = 0.0

        q_target = reward_batch + self.gamma * T.max(q_next, dim=1)[0]

        loss = self.Q_eval.loss(q_target, q_eval).to(self.Q_eval.device)
        loss.backward()
        self.Q_eval.optimizer.step()

        if self.epsilon > self.eps_min:
            self.epsilon = self.epsilon - self.eps_dec
        else:
            self.epsilon = self.eps_min





def degrees_to_radians(x):
    return x * np.pi / 180



def radians_to_degrees(x):
    return x * 180 / np.pi



def rotate_z(p, theta):
    R_z = np.array([[np.cos(theta), -np.sin(theta), 0],
                  [np.sin(theta), np.cos(theta),  0],
                  [0,             0,              1]])

    return np.dot(R_z, p)



# Returns a list of x-y coordinates of the corners of the Otter
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



# Draws the position of the Otter on a matplotlib figure
def plot_vehicle_position(eta, vehicle_type = "otter", plot_show = False, draw_center = False):
    if vehicle_type == "otter":
        vehicle_length = 2.0
        vehicle_width = 1.08

    x = eta[1]
    y = eta[0]
    yaw = -eta[5]
    left_back_corner = rotate_z(np.array([-vehicle_width/2, -vehicle_length/2, 0]), yaw)[:2] + np.array([x, y])
    left_front_corner = rotate_z(np.array([-vehicle_width/2, vehicle_length/2, 0]), yaw)[:2] + np.array([x, y])
    right_front_corner = rotate_z(np.array([vehicle_width/2, vehicle_length/2, 0]), yaw)[:2] + np.array([x, y])
    right_back_corner = rotate_z(np.array([vehicle_width/2, -vehicle_length/2, 0]), yaw)[:2] + np.array([x, y])
    two_meters_ahead = rotate_z(np.array([0, 2, 0]), yaw)[:2] + np.array([x, y])

    if draw_center == True:
        plt.scatter(x, y)

    plt.plot([left_back_corner[0], left_front_corner[0]], [left_back_corner[1], left_front_corner[1]])
    plt.plot([left_front_corner[0], right_front_corner[0]], [left_front_corner[1], right_front_corner[1]])
    plt.plot([right_front_corner[0], right_back_corner[0]], [right_front_corner[1], right_back_corner[1]])
    plt.plot([right_back_corner[0], left_back_corner[0]], [right_back_corner[1], left_back_corner[1]])
    plt.plot([x, two_meters_ahead[0]], [y, two_meters_ahead[1]])

    if plot_show == True:
        plt.show()



# Draws a sample dock on a matplotlib figure
def plot_dock(dock = "dummy_dock", plot_show = False, draw_center = True):

    if dock == "dummy_dock":
        point_0 = [0, -50]
        point_1 = [23.75, -26.25]
        point_2 = [28.75, -31.25]
        point_3 = [31.25, -28.75]
        point_4 = [26.25, -23.75]
        point_5 = [50, 0]
        dock_center = [27.5, -27.5]

        if draw_center == True:
            plt.scatter(dock_center[0], dock_center[1])

        """
        plt.scatter(point_0[0], point_0[1])
        plt.scatter(point_1[0], point_1[1])
        plt.scatter(point_2[0], point_2[1])
        plt.scatter(point_3[0], point_3[1])
        plt.scatter(point_4[0], point_4[1])
        plt.scatter(point_5[0], point_5[1])
        """

        plt.plot([point_0[0], point_1[0]], [point_0[1], point_1[1]])
        plt.plot([point_1[0], point_2[0]], [point_1[1], point_2[1]])
        plt.plot([point_2[0], point_3[0]], [point_2[1], point_3[1]])
        plt.plot([point_3[0], point_4[0]], [point_3[1], point_4[1]])
        plt.plot([point_4[0], point_5[0]], [point_4[1], point_5[1]])

        if plot_show == True:
            plt.show()

        return

    if dock == "tjuvholmen_swimming_pier":
        return

    if dock == "oslomet_oceanlab_dock":
        return



# Taken from https://en.wikipedia.org/wiki/Geographic_coordinate_system
# Standard value is for OsloMet Oceanlab
def distance_at_longitude(degrees, phi = 10.719278575838432):
    phi = degrees_to_radians(phi)
    return degrees * (11412.84*np.cos(phi) - 93.5*np.cos(3*phi) + 0.118*np.cos(5*phi))



# Taken from https://en.wikipedia.org/wiki/Geographic_coordinate_system
# Standard value is for OsloMet Oceanlab
def distance_at_latitude(degrees, phi = 59.90865634998943):
    phi = degrees_to_radians(phi)
    return degrees * (111132.92 - 559.82*np.cos(2*phi) + 1.175*np.cos(4*phi) - 0.0023*np.cos(6*phi))



# Returns distance in meters between two decimal coordinates
def map_distance(start, end):
    lat_distance = distance_at_latitude(end[0]-start[0], np.average([start[0], end[0]]))
    lon_distance = distance_at_longitude(end[1]-start[1], np.average([start[1], end[1]]))
    distance = np.hypot(lat_distance, lon_distance)
    return distance



# Retruns the [x, y] position in the local map for a dock, given the global coordinates (59.908096, 10.719414)
def find_otter_position_in_map(global_coordinates, dock = "dummy_dock"):
    # dock is the name of the map we want to find the position in
    x = 0
    y = 0
    return [x, y]









# Returns the thruster configuration that the Otter should have
def set_vehicle_thrusters(vehicle="otter", method="random", mover = None, inputs=None):

    # Step input on thrusters. Max +- 100
    thruster_configuration = np.array([0, 0], float)

    if vehicle == "otter":
        if method == "random":
            thruster_configuration = np.array([np.random.random_integers(0, 100), np.random.random_integers(0, 100)], float)

        elif method == "dq_agent":
            action = mover.choose_action(inputs)
            if action == 0: # Go forward
                thruster_configuration[0] = 30
                thruster_configuration[1] = 30
            elif action == 1: # Set to zero
                thruster_configuration[0] = 0
                thruster_configuration[1] = 0
            elif action == 2: # Go backwards
                thruster_configuration[0] = -30
                thruster_configuration[1] = -30
            elif action == 3: # Turn left
                thruster_configuration[0] = -30
                thruster_configuration[1] = 30
            elif action == 4: # Turn right
                thruster_configuration[0] = 30
                thruster_configuration[1] = -30

    return action, thruster_configuration



def simulate(vehicle_type="otter", dock="dummy_dock", sample_time=0.02, number_of_steps=9010, visualize=True, print_information=True, starting_position="random", movement_model=None):
    # DQL parameters
    action_taken = None
    observation = np.zeros(17, dtype=np.float32)
    next_observation = np.zeros(17, dtype=np.float32)
    reward = 0
    done = False
    # This list will be filled during simulation
    actions_taken = np.zeros(1, dtype=np.int32)
    vehicle_observations = np.zeros([1, 17], dtype=np.float32)
    vehicle_next_observations = np.zeros([1, 17], dtype=np.float32)
    rewards = np.zeros(1, dtype=np.float32)
    dones = np.zeros(1, dtype=np.float32)

    # Initiate the vehicle class
    if vehicle_type == "otter":
        vehicle = otter()

    # Set initial position and attitude of vehicle
    eta = np.array([0, 0, 0, 0, 0, 0], float)
    if starting_position == "random":
        eta[0] = 20*np.random.rand() - 10
        eta[1] = 20*np.random.rand() - 10
        eta[5] = 2*np.pi*np.random.rand() - np.pi
    """x, y, z, roll, pitch, yaw
    Positive x axis is straight ahead
    Positive y axis is towards starboard
    Positive z axis is into the ocean"""

    # Gives the position and orientation of the dock
    if dock == "dummy_dock":
        dock_position = [27.5, -27.5]
        dock_angle = degrees_to_radians(225)

    # Setting initial parameters
    nu = vehicle.nu # Velocity
    u_actual = vehicle.u_actual # Actual inputs, defined by otter class (that's what Fossen wrote)
    u_control = np.array([0, 0], float) # Step input on thrusters. Max +- 100
    previous_vehicle_surge = 0 # Used for calculating acceleration
    previous_vehicle_sway = 0 # Used for calculating acceleration
    previous_vehicle_heave = 0 # Used for calculating acceleration
    previous_vehicle_yaw_velocity = 0 # Used for calculating acceleration

    # The simulation loop
    for step in range(number_of_steps):
        t = step * sample_time

        # Sets the force on the left and right thrusters
        if movement_model == None:
            if t == 10:
                u_control = np.array([90, -90], float)
            if t == 20:
                u_control = np.array([0, 0], float)
            if t == 30:
                u_control = np.array([90, 90], float)
            if t == 40:
                u_control = np.array([0, 0], float)
            if t == 50:
                u_control = np.array([-30, 30], float)
            if t == 60:
                u_control = np.array([0, 0], float)
            if t == 70:
                u_control = np.array([60, 60], float)
            if t == 80:
                u_control = np.array([0, 0], float)

        else:
            # Gather observation
            vehicle_x_position = eta[1]
            vehicle_y_position = eta[0]

            vehicle_yaw = eta[5]
            vehicle_surge = nu[0]
            vehicle_sway = nu[1]
            vehicle_heave = nu[2]
            vehicle_total_speed = np.sqrt(nu[0]**2 + nu[1]**2 + nu[2]**2)

            vehicle_surge_acceleration = nu[0] - previous_vehicle_surge
            vehicle_sway_acceleration = nu[1] - previous_vehicle_sway
            vehicle_heave_acceleration = nu[2] - previous_vehicle_heave
            vehicle_yaw_acceleration = eta[5] - previous_vehicle_yaw_velocity

            distance_between_vehicle_and_dock = np.hypot(dock_position[0]-vehicle_x_position, dock_position[1]-vehicle_y_position)
            angular_difference_between_vehicle_and_dock = dock_angle + vehicle_yaw
            while angular_difference_between_vehicle_and_dock > np.pi:
                angular_difference_between_vehicle_and_dock -= 2*np.pi
            while angular_difference_between_vehicle_and_dock <= -np.pi:
                angular_difference_between_vehicle_and_dock += 2*np.pi

            # Collects the relevant data into a single array
            observation = np.zeros(17, dtype=np.float32)
            # All linear and angular velocities
            observation[0] = nu[0] # Vehicle surge
            observation[1] = nu[1] # Vehicle sway
            observation[2] = nu[2] # Vehicle heave
            observation[3] = nu[3] # Vehicle roll velocity
            observation[4] = nu[4] # Vehicle pitch velocity
            observation[5] = nu[5] # Vehicle yaw velocity
            # Surge/sway/heave/yaw acceleration
            observation[6] = vehicle_surge_acceleration # Surge acceleration
            observation[7] = vehicle_sway_acceleration # Sway acceleration
            observation[8] = vehicle_heave_acceleration # Heave acceleration
            observation[9] = vehicle_yaw_acceleration # Yaw acceleration
            # Current heading
            observation[10] = eta[5] # Vehicle yaw
            # Position difference
            observation[11] = dock_position[0] - eta[1] # Difference in x-position (global frame)
            observation[12] = dock_position[1] - eta[0] # Difference in y-position (global frame)
            # Distance to dock
            observation[13] = distance_between_vehicle_and_dock # Absolute distance between vehicle and dock
            # Angle to dock
            observation[14] = angular_difference_between_vehicle_and_dock # Angular difference in radians (not absolute)
            # Current thruster configuration
            observation[15] = u_control[0] # Left thruster
            observation[16] = u_control[1] # Right thruster

            vehicle_observations = np.r_[vehicle_observations, [observation]]

            action_taken, u_control = set_vehicle_thrusters(method="dq_agent", mover=movement_model, inputs=observation)
            actions_taken = np.append(actions_taken, action_taken)

        # Apply the actual dynamics by integrating
        [nu, u_actual]  = vehicle.dynamics(eta, nu, u_actual, u_control, sample_time)
        eta = gnc.attitudeEuler(eta, nu, sample_time)

        # Gather relevant data
        vehicle_x_position = eta[1]
        vehicle_y_position = eta[0]

        vehicle_yaw = eta[5]
        vehicle_surge = nu[0]
        vehicle_sway = nu[1]
        vehicle_heave = nu[2]
        vehicle_total_speed = np.sqrt(nu[0]**2 + nu[1]**2 + nu[2]**2)

        vehicle_surge_acceleration = nu[0] - previous_vehicle_surge
        vehicle_sway_acceleration = nu[1] - previous_vehicle_sway
        vehicle_heave_acceleration = nu[2] - previous_vehicle_heave
        vehicle_yaw_acceleration = eta[5] - previous_vehicle_yaw_velocity

        distance_between_vehicle_and_dock = np.hypot(dock_position[0]-vehicle_x_position, dock_position[1]-vehicle_y_position)
        angular_difference_between_vehicle_and_dock = dock_angle + vehicle_yaw
        while angular_difference_between_vehicle_and_dock > np.pi:
            angular_difference_between_vehicle_and_dock -= 2*np.pi
        while angular_difference_between_vehicle_and_dock <= -np.pi:
            angular_difference_between_vehicle_and_dock += 2*np.pi

        # Collects the relevant data into a single array
        next_observation = np.zeros(17, dtype=np.float32)
        # All linear and angular velocities
        next_observation[0] = nu[0] # Vehicle surge
        next_observation[1] = nu[1] # Vehicle sway
        next_observation[2] = nu[2] # Vehicle heave
        next_observation[3] = nu[3] # Vehicle roll velocity
        next_observation[4] = nu[4] # Vehicle pitch velocity
        next_observation[5] = nu[5] # Vehicle yaw velocity
        # Surge/sway/heave/yaw acceleration
        next_observation[6] = vehicle_surge_acceleration # Surge acceleration
        next_observation[7] = vehicle_sway_acceleration # Sway acceleration
        next_observation[8] = vehicle_heave_acceleration # Heave acceleration
        next_observation[9] = vehicle_yaw_acceleration # Yaw acceleration
        # Current heading
        next_observation[10] = eta[5] # Vehicle yaw
        # Position difference
        next_observation[11] = dock_position[0] - eta[1] # Difference in x-position (global frame)
        next_observation[12] = dock_position[1] - eta[0] # Difference in y-position (global frame)
        # Distance to dock
        next_observation[13] = distance_between_vehicle_and_dock # Absolute distance between vehicle and dock
        # Angle to dock
        next_observation[14] = angular_difference_between_vehicle_and_dock # Angular difference in radians (not absolute)
        # Current thruster configuration
        next_observation[15] = u_control[0] # Left thruster
        next_observation[16] = u_control[1] # Right thruster

        # Add the observation at this time step to the entire history
        vehicle_next_observations = np.r_[vehicle_next_observations, [next_observation]]

        # Used to calculate acceleration
        previous_vehicle_surge = nu[0]
        previous_vehicle_sway = nu[1]
        previous_vehicle_heave = nu[2]
        previous_vehicle_yaw_velocity = eta[5]






        # Prints information on the vehicle
        # Note that information is in NED reference frame
        if print_information == True:
            if t % 10 == 0:
                print("t:", t)
                print("u_control:", u_control)
                print("")
                print("Surge:", nu[0])
                print("Sway:", nu[1])
                print("Heave:", nu[2])
                print("Total speed:", np.sqrt(nu[0]**2 + nu[1]**2 + nu[2]**2))
                print("")
                print("x:", eta[0])
                print("y:", eta[1])
                print("z:", eta[2])
                print("")
                print("Roll:", eta[3])
                print("Pitch:", eta[4])
                print("Yaw:", eta[5])
                print("Angular difference:", angular_difference_between_vehicle_and_dock)

                print("\n")

        # Visualizes the vessel's position and orientation
        if visualize == True:
            plt.clf()
            plt.ion()
            plt.xlim(-50, 50)
            plt.ylim(-50, 50)
            plot_vehicle_position(eta)
            plot_dock()
            plt.draw()
            plt.pause(0.001)





        # Ends simulation if Otter is out of bounds
        if not (-50 < eta[0] < 50 and -50 < eta[1] < 50):
            if print_information == True:
                print("\n")
                print("------------------------")
                print("Vehicle went out of bounds")
                print("Ending simulation")
                print("------------------------")
            reward = -1
            done = True
            rewards = np.append(rewards, reward)
            dones = np.append(dones, done)
            break

        # Ends simulation if time is reached
        if t >= (number_of_steps*sample_time) - sample_time: # Checks if we are on the last time step
            if print_information == True:
                print("\n")
                print("------------------------")
                print("Reached time limit")
                print("Ending simulation")
                print("------------------------")
            reward = (np.hypot(100, 100) - distance_between_vehicle_and_dock)/np.hypot(100, 100) + (np.pi - abs(angular_difference_between_vehicle_and_dock))/np.pi
            done = True
            rewards = np.append(rewards, reward)
            dones = np.append(dones, done)
            break

        # Check if Otter crashed with the dock
        vehicle_crashed = False
        vehicle_corners = get_vehicle_corners(eta)

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
            if print_information == True:
                print("\n")
                print("------------------------")
                print("Vehicle crashed into the dock")
                print("Ending simulation")
                print("------------------------")
            reward = -0.5*vehicle_total_speed**2
            done = True
            rewards = np.append(rewards, reward)
            dones = np.append(dones, done)
            break

        rewards = np.append(rewards, reward)
        dones = np.append(dones, done)

    # Omitting first row of lists because it is only zeros
    actions_taken = actions_taken[1:]
    vehicle_observations = vehicle_observations[1:, :]
    vehicle_next_observations = vehicle_next_observations[1:, :]
    rewards = rewards[1:]
    dones = dones[1:]

    return actions_taken, vehicle_observations, vehicle_next_observations, rewards, dones




# Used in case you want to do some NEAT inspired things
def mutate_network(network_topology, mutation_method="random"):

    if len(network_topology) == 0:
        return [1]

    if mutation_method == "random":
        if np.random.random() >= 0.8: # Add a new layer
            mutated_network_topology = network_topology.append(1)
        else: # Increase neurons in a layer by 1
            mutated_network_topology = network_topology
            mutated_network_topology[np.random.randint(len(network_topology))] += 1

    return mutated_network_topology





















# The number of times we will simulate the vehicle
number_of_simulations = 10000

# Create the network
dq_agent = Agent(gamma=0.99, epsilon=1.0, lr=0.003, input_dims=[17], batch_size=64, n_actions=5)

# Beginning of the simulations
for simulation_number in range(number_of_simulations):
    print("Starting simulation:", simulation_number + 1)

    # The actual simulation
    simulation_actions_taken, simulation_vehicle_observations, simulation_vehicle_next_observations, simulation_rewards, simulation_dones = simulate(sample_time=0.1, number_of_steps=1000, visualize=False, print_information=False, movement_model=dq_agent)
    """
    if simulation_number % 100000 == 0:
        simulation_actions_taken, simulation_vehicle_observations, simulation_vehicle_next_observations, simulation_rewards, simulation_dones = simulate(sample_time=0.1, number_of_steps=1000, visualize=True, print_information=True, movement_model=dq_agent)
    else:
        simulation_actions_taken, simulation_vehicle_observations, simulation_vehicle_next_observations, simulation_rewards, simulation_dones = simulate(sample_time=0.1, number_of_steps=1000, visualize=False, print_information=False, movement_model=dq_agent)
    """

    # Displays the simulation reward
    print("")
    print("------------------------")
    print("Simulation reward:")
    print(simulation_rewards[-1])
    print("------------------------")
    print("\n")



    # Create the memory
    final_reward = simulation_rewards[-1]
    for n in range(len(simulation_rewards)):
        simulation_rewards[n] = final_reward*np.exp(-n/100)
    simulation_rewards = np.flipud(simulation_rewards)

    for n in range(len(simulation_actions_taken)):
        dq_agent.store_transition(simulation_vehicle_observations[n, :], simulation_actions_taken[n], simulation_rewards[n], simulation_vehicle_next_observations[n], simulation_dones[n])

    # Train the network
    dq_agent.learn()












































"""
Plan of attack:

- Set up an environment for the agent to train in
 - A map of the docking area
 - A way to simulate the otter

- State
 - GPS position
 - Speed
 - Yaw
 - Camera feed
 - Lidar?

- Control the inputs
 - Thruster power allocation
  - Increase left thruster, increase right thruster
  - Increase left thruster, no change right thruster
  - Increase left thruster, decrease right thruster
  - No change left thruster, increase right thruster
  - No change left thruster, no change right thruster
  - No change left thruster, decrease right thruster
  - Decrease left thruster, increase right thruster
  - Decrease left thruster, no change right thruster
  - Decrease left thruster, decrease right thruster

- Session ends if:
 - Vessel docked
 - Vessel crashes
 - Timeout
 - Vessel out of bounds

- Positive reward:
 - Ongoing
  - Heading in right direction? (We can do this in the beginning to train it, then remove it when it performs okay)
 - Final
  - How close the vessel is to the destination
  - Correct orientation

- Negative reward:
 - Crashes
 - Time
 - Fuel consumption?





"""
