
# Standard libraries
import numpy as np
from numpy import pi
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
    def __init__(self, lr, input_dims, fc1_dims, fc2_dims, fc3_dims, fc4_dims, fc5_dims,
            n_actions):
        super(DeepQNetwork, self).__init__()
        self.input_dims = input_dims
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.fc3_dims = fc3_dims
        self.fc4_dims = fc4_dims
        self.fc5_dims = fc5_dims
        self.n_actions = n_actions
        self.fc1 = nn.Linear(*self.input_dims, self.fc1_dims)
        self.fc2 = nn.Linear(self.fc1_dims, self.fc2_dims)
        self.fc3 = nn.Linear(self.fc2_dims, self.fc3_dims)
        self.fc4 = nn.Linear(self.fc3_dims, self.fc4_dims)
        self.fc5 = nn.Linear(self.fc4_dims, self.fc5_dims)
        self.fc6 = nn.Linear(self.fc5_dims, self.n_actions)

        self.optimizer = optim.Adam(self.parameters(), lr=lr)
        self.loss = nn.MSELoss()
        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)

    def forward(self, state):
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = F.relu(self.fc4(x))
        x = F.relu(self.fc5(x))
        actions = self.fc6(x)

        return actions

class Agent():
    def __init__(self, gamma, epsilon, lr, input_dims, batch_size, n_actions,
            max_mem_size=100_000, eps_end=0.01, eps_dec=0.0005):
        self.gamma = gamma
        self.epsilon = epsilon
        self.eps_min = eps_end
        self.eps_dec = eps_dec
        self.lr = lr
        self.action_space = [i for i in range(n_actions)]
        self.mem_size = max_mem_size
        self.batch_size = batch_size
        self.mem_cntr = 0
        self.iter_cntr = 0
        self.replace_target = 100

        self.Q_eval = DeepQNetwork(lr, input_dims=input_dims,
                                    fc1_dims=512, fc2_dims=1024, fc3_dims=2048, fc4_dims=1024, fc5_dims=512, n_actions=n_actions)
        self.Q_next = DeepQNetwork(lr, input_dims=input_dims,
                                    fc1_dims=512, fc2_dims=1024, fc3_dims=2048, fc4_dims=1024, fc5_dims=512, n_actions=n_actions)

        self.state_memory = np.zeros((self.mem_size, *input_dims), dtype=np.float32)
        self.new_state_memory = np.zeros((self.mem_size, *input_dims), dtype=np.float32)
        self.action_memory = np.zeros(self.mem_size, dtype=np.int32)
        self.reward_memory = np.zeros(self.mem_size, dtype=np.float32)
        self.terminal_memory = np.zeros(self.mem_size, dtype=np.bool)

    def store_transition(self, state, action, reward, state_, terminal):
        index = self.mem_cntr % self.mem_size
        self.state_memory[index] = state
        self.new_state_memory[index] = state_
        self.reward_memory[index] = reward
        self.action_memory[index] = action
        self.terminal_memory[index] = terminal

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
        action_batch = self.action_memory[batch]
        reward_batch = T.tensor(self.reward_memory[batch]).to(self.Q_eval.device)
        terminal_batch = T.tensor(self.terminal_memory[batch]).to(self.Q_eval.device)

        q_eval = self.Q_eval.forward(state_batch)[batch_index, action_batch]
        q_next = self.Q_eval.forward(new_state_batch)
        q_next[terminal_batch] = 0.0

        q_target = reward_batch + self.gamma*T.max(q_next,dim=1)[0]

        loss = self.Q_eval.loss(q_target, q_eval).to(self.Q_eval.device)
        loss.backward()
        self.Q_eval.optimizer.step()

        self.iter_cntr += 1
        self.epsilon = self.epsilon - self.eps_dec if self.epsilon > self.eps_min \
                       else self.eps_min

        #if self.iter_cntr % self.replace_target == 0:
        #   self.Q_next.load_state_dict(self.Q_eval.state_dict())




# Used to visualize, and find position of corners of the vehicle
def rotate_z(p, theta):
    R_z = np.array([[np.cos(theta), -np.sin(theta), 0],
                  [np.sin(theta), np.cos(theta),  0],
                  [0,             0,              1]])

    return np.dot(R_z, p)

# Used to find the difference between two angles
def smallest_signed_angle_between(x, y):
    a = (x - y) % (2*pi)
    b = (y - x) % (2*pi)
    return -a if a < b else b

# Returns a list of x-y coordinates of the corners of the vehicle
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



# Retruns the [x, y] position in the local map for a dock, given the global coordinates (59.908096, 10.719414)
def find_otter_position_in_map(global_coordinates, dock = "dummy_dock"):
    # dock is the name of the map we want to find the position in
    x = 0
    y = 0
    return [x, y]



# Returns the thruster configuration that the Otter should have
def set_vehicle_thrusters(vehicle="otter", method="random", mover=None, inputs=None):

    # Step input on thrusters. Max +- 100
    thruster_configuration = np.array([0, 0], float)
    action = -1

    if vehicle == "otter":
        if method == "random":
            thruster_configuration = np.array([np.random.random_integers(0, 100), np.random.random_integers(0, 100)], float)

        elif method == "fixed":
            if inputs > 10:
                thruster_configuration[0] = 50
                thruster_configuration[1] = -50
                action = 4
            if inputs > 20:
                thruster_configuration[0] = 0
                thruster_configuration[1] = 0
                action = 1
            if inputs > 30:
                thruster_configuration[0] = 50
                thruster_configuration[1] = 50
                action = 0
            if inputs > 40:
                thruster_configuration[0] = 0
                thruster_configuration[1] = 0
                action = 1
            if inputs > 50:
                thruster_configuration[0] = -50
                thruster_configuration[1] = 50
                action = 3
            if inputs > 55:
                thruster_configuration[0] = 0
                thruster_configuration[1] = 0
                action = 1
            if inputs > 70:
                thruster_configuration[0] = 50
                thruster_configuration[1] = 50
                action = 0
            if inputs > 80:
                thruster_configuration[0] = 0
                thruster_configuration[1] = 0
                action = 1

        elif method == "dq_agent":
            action = mover.choose_action(inputs)
            if action == 0: # Go forward
                thruster_configuration[0] = 50
                thruster_configuration[1] = 50
            elif action == 1: # Set to zero
                thruster_configuration[0] = 0
                thruster_configuration[1] = 0
            elif action == 2: # Go backwards
                thruster_configuration[0] = -50
                thruster_configuration[1] = -50
            elif action == 3: # Turn left
                thruster_configuration[0] = -50
                thruster_configuration[1] = 50
            elif action == 4: # Turn right
                thruster_configuration[0] = 50
                thruster_configuration[1] = -50

        elif method == "cybernetics":
            print("Make cybernetics method in set_vehicle_thrusters")
            exit()

    return action, thruster_configuration



def simulate(vehicle_type="otter", dock="dummy_dock", sample_time=0.1, number_of_steps=601, visualize=False, print_information=False, starting_position="random", movement_method="dq_agent", movement_model=None):
    # DQL parameters
    action_taken = -1
    observation = np.zeros(10, dtype=np.float32)
    next_observation = np.zeros(10, dtype=np.float32)
    reward = 0
    done = 0
    # This list will be filled during simulation
    actions_taken = np.zeros(1, dtype=np.int32)
    vehicle_observations = np.zeros([1, 10], dtype=np.float32)
    vehicle_next_observations = np.zeros([1, 10], dtype=np.float32)
    rewards = np.zeros(1, dtype=np.float32)
    dones = np.zeros(1, dtype=np.float32)

    # Initiate the vehicle class
    if vehicle_type == "otter":
        vehicle = otter()

    # Set initial position and attitude of vehicle
    # x, y, z, roll, pitch, yaw (uses NED reference frame)
    eta = np.array([0, 0, 0, 0, 0, 0], np.float32)
    if starting_position == "random":
        eta[0] += 5*np.random.rand() - 2.5
        eta[1] += 5*np.random.rand() - 2.5
        eta[5] += 2*pi*np.random.rand() - pi


    # Gives the position and orientation of the dock
    if dock == "dummy_dock":
        dock_position = [27.5, -27.5]
        dock_angle = np.deg2rad(-135)

    # Setting initial parameters
    nu = vehicle.nu # Velocity
    u_actual = vehicle.u_actual # Actual inputs, defined by otter class (that's what Fossen wrote)
    u_control = np.array([0, 0], float) # Step input on thrusters. Max +- 100

    # For calculating intermediate rewards
    previous_distance_between_vehicle_and_dock = np.hypot(dock_position[0], dock_position[1])
    previous_angular_difference_between_vehicle_and_dock = dock_angle



    # The simulation loop
    for step in range(number_of_steps):
        t = np.round(step * sample_time, 2)

        if t % 1 == 0: # We only evalute the DQL agent at certain intervals
            # Gather observations
            vehicle_yaw = -eta[5]

            distance_between_vehicle_and_dock = np.hypot(dock_position[0]-eta[1], dock_position[1]-eta[0])
            angular_difference_between_vehicle_and_dock = smallest_signed_angle_between(vehicle_yaw, dock_angle)

            # Collects the relevant data into a single array
            observation = np.zeros(10, dtype=np.float32)
            # X,Y-position and yaw
            observation[0] = eta[0] / 50 # x-position (NED frame)
            observation[1] = eta[1] / 50 # y-position (NED frame)
            observation[2] = eta[5] / (2*pi) # yaw (NED frame)
            # Position difference
            observation[3] = (dock_position[0] - eta[1]) / 50 # Difference in x-position (global frame)
            observation[4] = (dock_position[1] - eta[0]) / 50 # Difference in y-position (global frame)
            # Velocities
            observation[5] = nu[0] / 3
            observation[6] = nu[1] / 3
            observation[7] = nu[5] / 3
            # Distance to dock
            observation[8] = distance_between_vehicle_and_dock / np.hypot(27.5, 27.5) # Absolute distance between vehicle and dock
            # Angle to dock
            observation[9] = angular_difference_between_vehicle_and_dock / (2*pi) # Angular difference in radians (not absolute)

            # Add the observation at this time step to the entire history
            vehicle_observations = np.r_[vehicle_observations, [observation]]

            # Sets the vehicle thrusters
            if movement_method == "fixed":
                action_taken, u_control = set_vehicle_thrusters(method=movement_method, mover=movement_model, inputs=t)
            else:
                action_taken, u_control = set_vehicle_thrusters(method=movement_method, mover=movement_model, inputs=observation)
            actions_taken = np.append(actions_taken, action_taken)



        # Apply the actual dynamics by integrating
        [nu, u_actual]  = vehicle.dynamics(eta, nu, u_actual, u_control, sample_time)
        eta = gnc.attitudeEuler(eta, nu, sample_time)



        if t % 1 == 0: # We only evalute the DQL agent at certain intervals
            # Gather next observations
            vehicle_yaw = -eta[5]

            distance_between_vehicle_and_dock = np.hypot(dock_position[0]-eta[1], dock_position[1]-eta[0])
            angular_difference_between_vehicle_and_dock = smallest_signed_angle_between(vehicle_yaw, dock_angle)

            # Collects the relevant data into a single array
            next_observation = np.zeros(10, dtype=np.float32)
            # X,Y-position and yaw
            next_observation[0] = eta[0] / 50 # x-position (NED frame)
            next_observation[1] = eta[1] / 50 # y-position (NED frame)
            next_observation[2] = eta[5] / (2*pi) # yaw (NED frame)
            # Position difference
            next_observation[3] = (dock_position[0] - eta[1]) / 50 # Difference in x-position (global frame)
            next_observation[4] = (dock_position[1] - eta[0]) / 50 # Difference in y-position (global frame)
            # Velocities
            next_observation[5] = nu[0] / 3
            next_observation[6] = nu[1] / 3
            next_observation[7] = nu[5] / 3
            # Distance to dock
            next_observation[8] = distance_between_vehicle_and_dock / np.hypot(27.5, 27.5) # Absolute distance between vehicle and dock
            # Angle to dock
            next_observation[9] = angular_difference_between_vehicle_and_dock / (2*pi) # Angular difference in radians (not absolute)

            # Add the observation at this time step to the entire history
            vehicle_next_observations = np.r_[vehicle_next_observations, [next_observation]]





            # Ends simulation if Otter is out of bounds
            if not (-50 < eta[0] < 50 and -50 < eta[1] < 50):
                if print_information == True:
                    print("\n")
                    print("------------------------")
                    print("Vehicle went out of bounds")
                    print("Ending simulation")
                    print("------------------------")
                reward = ((np.hypot(27.5, 27.5) - distance_between_vehicle_and_dock)/np.hypot(27.5, 27.5)) \
                        + ((pi/2-abs(angular_difference_between_vehicle_and_dock))/(pi/2))
                done = 1
                rewards = np.append(rewards, reward)
                dones = np.append(dones, done)
                break

            # Ends simulation if time is reached
            if t >= np.round((number_of_steps*sample_time), 2) - sample_time: # Checks if we are on the last time step, need to use np.round because of computer numeric error
                if print_information == True:
                    print("\n")
                    print("------------------------")
                    print("Reached time limit")
                    print("Ending simulation")
                    print("------------------------")
                reward = ((np.hypot(27.5, 27.5) - distance_between_vehicle_and_dock)/np.hypot(27.5, 27.5)) \
                        + ((pi/2-abs(angular_difference_between_vehicle_and_dock))/(pi/2))
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
                reward = ((np.hypot(27.5, 27.5) - distance_between_vehicle_and_dock)/np.hypot(27.5, 27.5)) \
                        + ((pi/2-abs(angular_difference_between_vehicle_and_dock))/(pi/2)) \
                        -np.sqrt(nu[0]**2 + nu[1]**2 + nu[2]**2)
                done = 1
                rewards = np.append(rewards, reward)
                dones = np.append(dones, done)
                break


            # Intermediate rewards
            rewards = np.append(rewards, reward)
            dones = np.append(dones, done)








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



    # Omitting first row of lists because it is only zeros
    actions_taken = actions_taken[1:]
    vehicle_observations = vehicle_observations[1:, :]
    vehicle_next_observations = vehicle_next_observations[1:, :]
    rewards = rewards[1:]
    dones = dones[1:]

    print("\nFinal pose:")
    print("X:  ", np.round(eta[1], 2))
    print("Y:  ", np.round(eta[0], 2))
    print("Yaw:", np.round(-eta[5], 2))

    return actions_taken, vehicle_observations, vehicle_next_observations, rewards, dones




# Used in case you want to do some NEAT inspired things
def mutate_network(network_topology, mutation_method="random"):

    if len(network_topology) == 0:
        return [1]

    if mutation_method == "random":
        if np.random.random() >= 0.99: # Add a new layer
            mutated_network_topology = network_topology.append(1)
        else: # Increase neurons in a layer by 1
            mutated_network_topology = network_topology
            mutated_network_topology[np.random.randint(len(network_topology))] += 1

    return mutated_network_topology




























def main():

    # The number of times we will simulate the vehicle
    number_of_simulations = 100_000
    best_simulation_score = -np.inf

    # Create the network
    dq_agent = Agent(gamma=0.99, epsilon=1.0, lr=0.0001, input_dims=[10], batch_size=32, n_actions=5, max_mem_size=100_000, eps_end=0.01, eps_dec=1/(60*number_of_simulations/2))

    # Beginning of the simulations
    for simulation_number in range(number_of_simulations):
        print("Starting simulation:", simulation_number + 1)

        # The actual simulation
        # Note that number_of_steps must be 1 higher than an int of seconds (f.ex sample_time = 0.1, and number_of_steps = 601 for 60 seconds)
        simulation_actions_taken, simulation_vehicle_observations, simulation_vehicle_next_observations, simulation_rewards, simulation_dones = \
            simulate(starting_position="random", movement_model=dq_agent)

        # Displays the simulation reward
        final_reward = simulation_rewards[-1]
        print("")
        print("------------------------")
        print("Final reward:")
        print(final_reward)
        print("------------------------")
        print("\n")

        # Fixes intermediate rewards
        for n in range(len(simulation_rewards)):
            simulation_rewards[-(n+1)] = final_reward*(0.99**n)

        # Store memory
        for n in range(len(simulation_actions_taken)):
            dq_agent.store_transition(simulation_vehicle_observations[n, :], simulation_actions_taken[n], simulation_rewards[n], simulation_vehicle_next_observations[n, :], simulation_dones[n])

            # Train the network
            dq_agent.learn()

        # Saves the network during training
        T.save(dq_agent.Q_eval, "neural_network_models/trained_model.pt")

        # Record the best score
        if final_reward > best_simulation_score:
            best_simulation_score = final_reward
            print("\n---------")
            print("New best:")
            print(np.round(best_simulation_score, 7))
            print("---------\n")

            best_final_pose = [np.round(simulation_vehicle_observations[-1, 1], 2), \
                               np.round(simulation_vehicle_observations[-1, 0], 2), \
                               np.round(-simulation_vehicle_observations[-1, 2], 2)]

            best_simulation_number = simulation_number

    # Shows the best reward
    print("\n------------------------")
    print("All simulations finished")
    print("Best score:")
    print(best_simulation_score)
    print("Best final pose:")
    print(best_final_pose)
    print("Best simulation:")
    print(best_simulation_number)
    print("------------------------\n")

    # Save the network after training
    T.save(dq_agent.Q_eval, "neural_network_models/final_trained_model.pt")





if __name__ == '__main__':
    main()













































#
