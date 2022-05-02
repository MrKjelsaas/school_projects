
# Standard libraries
import numpy as np
from numpy import pi
import matplotlib.pyplot as plt
import threading

# AI libraries
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from dq_learning import Agent, DeepQNetwork

# These files were collected from https://github.com/cybergalactic/PythonVehicleSimulator
from functions import plotVehicleStates, plotControls, simulate, gnc
from vehicles import otter





# Used to get the return value of a thread
class return_result_thread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
        def function():
            self.result = target(*args, **kwargs)
        super().__init__(group=group, target=function, name=name, daemon=daemon)



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
            thruster_configuration = np.array([np.random.random_integers(-100, 100), np.random.random_integers(-100, 100)], float)

        elif method == "dq_agent":
            action = mover.choose_action(inputs)
            if action == 0: # Go forward
                thruster_configuration[0] = 100
                thruster_configuration[1] = 100
            elif action == 1: # Set to zero
                thruster_configuration[0] = 0
                thruster_configuration[1] = 0
            elif action == 2: # Go backwards
                thruster_configuration[0] = -100
                thruster_configuration[1] = -100
            elif action == 3: # Turn left
                thruster_configuration[0] = -100
                thruster_configuration[1] = 100
            elif action == 4: # Turn right
                thruster_configuration[0] = 100
                thruster_configuration[1] = -100

        elif method == "deterministic":
            #inputs=[nu[0], nu[5], distance_between_vehicle_and_dock, angular_difference_between_vehicle_and_dock, smallest_signed_angle_between(0, np.arctan2(dock_position[1]-eta[0], dock_position[0]-eta[1]) - pi/2 + vehicle_yaw)])

            # Stop thrusters if moving too fast
            if inputs[0] > 0.5:
                return 1, [0, 0]

            # Approach the dock
            if inputs[2] > 3:
                if inputs[4] < np.deg2rad(-10): # Turns towards the dock
                    return 4, [50, -50]
                if inputs[4] > np.deg2rad(10): # Turns towards the dock
                    return 3, [-50, 50]
                else: # Drive towards the dock
                    return 0, [50, 50]

            # Checks if vehicle is ca in front of the dock
            if abs(smallest_signed_angle_between(inputs[3], inputs[4])) > np.deg2rad(5):
                # Turns towards the dock
                if abs(inputs[1]) > 0.1: # Don't turn too fast
                    return 1, [0, 0]
                if smallest_signed_angle_between(inputs[3], inputs[4]) < 0:
                    return 4, [50, -50]
                else:
                    return 3, [-50, 50]

            # Slowly approach the dock
            if inputs[2] > 3:
                return 0, [50, 50]

            # Attempt to angle the boat
            if inputs[3] < np.deg2rad(-10):
                return 4, [50, -50]
            if inputs[3] > np.deg2rad(10):
                return 3, [-50, 50]

            if abs(inputs[4]) > np.deg2rad(90): # Move backwards, we've probably driven past the dock
                return 2, [-50, -50]

            return 1, [0, 0]

    return action, thruster_configuration



def simulate(vehicle_type="otter", dock="dummy_dock", sample_time=0.1, seconds_to_simulate=120, visualize=False, print_information=False, starting_position="random", movement_method="dq_agent", movement_model=None):

    # For DQ training
    reward = 0
    done = False

    # This list will be filled during simulation
    actions_taken = np.zeros(1, dtype=np.int32)
    vehicle_observations = np.zeros([1, NUMBER_OF_INPUTS], dtype=np.float32)
    vehicle_next_observations = np.zeros([1, NUMBER_OF_INPUTS], dtype=np.float32)
    rewards = np.zeros(1, dtype=np.float32)
    dones = np.zeros(1, dtype=bool)

    # Initiate the vehicle class
    if vehicle_type == "otter":
        vehicle = otter()

    # Set initial position and attitude of vehicle
    # x, y, z, roll, pitch, yaw (uses NED reference frame)
    eta = np.array([0, 0, 0, 0, 0, 0], np.float32)
    if isinstance(starting_position, list):
        if len(starting_position) == 3:
            eta[1] = starting_position[0]
            eta[0] = starting_position[1]
            eta[5] = -starting_position[2]
        else:
            eta = starting_position

    elif starting_position == "random":
        eta[0] += 10*np.random.rand() - 5
        eta[1] += 10*np.random.rand() - 5
        eta[5] += 2*pi*np.random.rand() - pi

    # Gives the position and orientation of the dock
    if dock == "dummy_dock":
        dock_position = [27.5, -27.5]
        dock_angle = np.deg2rad(-135)

    # Setting initial parameters
    nu = vehicle.nu # Velocity
    u_actual = vehicle.u_actual # Actual inputs, defined by otter class (that's what Fossen wrote)
    u_control = np.array([0, 0], float) # Step input on thrusters. Max +- 100



    # The simulation loop
    for t in range(seconds_to_simulate):

        # Gather observations
        vehicle_yaw = smallest_signed_angle_between(0, -eta[5])
        distance_between_vehicle_and_dock = np.hypot(dock_position[0]-eta[1], dock_position[1]-eta[0])
        angular_difference_between_vehicle_and_dock = smallest_signed_angle_between(vehicle_yaw, dock_angle)

        # Collects the relevant data into a single array
        observation = np.array([nu[0], # surge
                                -nu[5], # yaw rotational velocity
                                distance_between_vehicle_and_dock, # distance to dock
                                angular_difference_between_vehicle_and_dock, # angular difference between dock rotation and vehicle rotation
                                smallest_signed_angle_between(0, np.arctan2(dock_position[1]-eta[0], dock_position[0]-eta[1]) - pi/2 - vehicle_yaw) # which direction the dock is in
                                ], dtype=np.float32)

        # Feature scaling
        feature_scaling_array = np.array([1, 0.1, np.hypot(27.5, -27.5), pi, pi])
        observation /= feature_scaling_array

        # Add the observation at this time step to the entire history
        vehicle_observations = np.r_[vehicle_observations, [observation]]

        # Sets the vehicle thrusters
        if movement_method == "dq_agent":
            action_taken, u_control = set_vehicle_thrusters(method=movement_method, mover=movement_model, inputs=observation)
        elif movement_method == "deterministic":
            action_taken, u_control = set_vehicle_thrusters(method=movement_method, inputs=observation*feature_scaling_array)
        actions_taken = np.append(actions_taken, action_taken)



        # Apply the actual dynamics by integrating
        for t_step in range(int(1/sample_time)):
            [nu, u_actual] = vehicle.dynamics(eta, nu, u_actual, u_control, sample_time)
            eta = gnc.attitudeEuler(eta, nu, sample_time)



        # Gather next observations
        vehicle_yaw = smallest_signed_angle_between(0, -eta[5])
        distance_between_vehicle_and_dock = np.hypot(dock_position[0]-eta[1], dock_position[1]-eta[0])
        angular_difference_between_vehicle_and_dock = smallest_signed_angle_between(vehicle_yaw, dock_angle)

        # Collects the relevant data into a single array
        next_observation = np.array([nu[0], # surge
                                    -nu[5], # yaw rotational velocity
                                    distance_between_vehicle_and_dock, # distance to dock
                                    angular_difference_between_vehicle_and_dock, # angular difference between dock rotation and vehicle rotation
                                    smallest_signed_angle_between(0, np.arctan2(dock_position[1]-eta[0], dock_position[0]-eta[1]) - pi/2 - vehicle_yaw) # which direction the dock is in
                                    ], dtype=np.float32)
        # Feature scaling
        next_observation /= feature_scaling_array

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
            reward = 50*np.exp(-distance_between_vehicle_and_dock/10)
            done = True

            rewards = np.append(rewards, reward)
            dones = np.append(dones, done)
            break

        # Ends simulation if time is reached
        if t == seconds_to_simulate-1: # Checks if we are on the last time step
            if print_information == True:
                print("\n")
                print("------------------------")
                print("Reached time limit")
                print("Ending simulation")
                print("------------------------")
            reward = 50*np.exp(-distance_between_vehicle_and_dock/10)
            if distance_between_vehicle_and_dock < 1: # Adds reward for angle if close enough
                reward += 50*np.exp(-abs(angular_difference_between_vehicle_and_dock)/10)
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
            reward = 50*np.exp(-distance_between_vehicle_and_dock/10)
            reward -= np.exp(abs(nu[0]))
            done = True

            rewards = np.append(rewards, reward)
            dones = np.append(dones, done)
            break

        # Intermediate rewards
        reward = 50*np.exp(-distance_between_vehicle_and_dock/10)
        if distance_between_vehicle_and_dock < 1: # Adds reward for angle if close enough
            reward += 50*np.exp(-abs(angular_difference_between_vehicle_and_dock)/10)
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

    if print_information == True:
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
    number_of_epochs = 256
    best_simulation_score = -np.inf
    all_final_rewards = []

    # Create the agents
    agent_alpha = Agent(input_dims=[NUMBER_OF_INPUTS], n_actions=5, epsilon=0)
    agent_bravo = Agent(input_dims=[NUMBER_OF_INPUTS], n_actions=5, epsilon=0.1)
    agent_charlie = Agent(input_dims=[NUMBER_OF_INPUTS], n_actions=5, epsilon=0.25)
    agent_delta = Agent(input_dims=[NUMBER_OF_INPUTS], n_actions=5, epsilon=0.5)
    agent_echo = Agent(input_dims=[NUMBER_OF_INPUTS], n_actions=5, epsilon=0.75)
    agent_foxtrot = Agent(input_dims=[NUMBER_OF_INPUTS], n_actions=5, epsilon=0.9)
    agent_golf = Agent(input_dims=[NUMBER_OF_INPUTS], n_actions=5, epsilon=1)

    list_of_agents = [agent_alpha, agent_bravo, agent_charlie, agent_delta, agent_echo, agent_foxtrot, agent_golf]

    starting_positions = np.array([#[27.5, -27.5, np.deg2rad(-135)],
                                   #[25, -25, np.deg2rad(-135)],
                                   #[20, -20, np.deg2rad(-112.5)],
                                   #[15, -15, np.deg2rad(-90)],
                                   #[10, -10, np.deg2rad(-45)],
                                   #[5, -5, np.deg2rad(-22.5)],
                                   [0, 0, 0],
                                   "random"],
                                   dtype=object)

    # Simulates with different starting positions
    for starting_position in starting_positions:

        # Beginning of the simulations
        for simulation_number in range(number_of_simulations):
            print("Starting simulation:", simulation_number + 1)

            # Make a simulation thread for every agent
            alpha_thread = return_result_thread(target=simulate, args=("otter", "dummy_dock", 0.1, 120, False, False, starting_position, "dq_agent", agent_alpha))
            bravo_thread = return_result_thread(target=simulate, args=("otter", "dummy_dock", 0.1, 120, False, False, starting_position, "dq_agent", agent_bravo))
            charlie_thread = return_result_thread(target=simulate, args=("otter", "dummy_dock", 0.1, 120, False, False, starting_position, "dq_agent", agent_charlie))
            delta_thread = return_result_thread(target=simulate, args=("otter", "dummy_dock", 0.1, 120, False, False, starting_position, "dq_agent", agent_delta))
            echo_thread = return_result_thread(target=simulate, args=("otter", "dummy_dock", 0.1, 120, False, False, starting_position, "dq_agent", agent_echo))
            foxtrot_thread = return_result_thread(target=simulate, args=("otter", "dummy_dock", 0.1, 120, False, False, starting_position, "dq_agent", agent_foxtrot))
            golf_thread = return_result_thread(target=simulate, args=("otter", "dummy_dock", 0.1, 120, False, False, starting_position, "dq_agent", agent_golf))
            determinist_thread = return_result_thread(target=simulate, args=("otter", "dummy_dock", 0.1, 120, False, False, starting_position, "deterministic", None))

            threads = [alpha_thread, bravo_thread, charlie_thread, delta_thread, echo_thread, foxtrot_thread, golf_thread, determinist_thread]

            # Start the simulations
            for thread in threads:
                thread.start()

            # Wait for all simulations to finish
            for thread in threads:
                thread.join()

                # Stores results in respective variables
                simulation_actions_taken = thread.result[0]
                simulation_vehicle_observations = thread.result[1]
                simulation_vehicle_next_observations = thread.result[2]
                simulation_rewards = thread.result[3]
                simulation_dones = thread.result[4]

                # Calculates intermediate rewards (temporal based)
                for n in range(len(simulation_rewards)):
                    simulation_rewards[-(n+1)] = simulation_rewards[-1]*(0.999**n)

                # Store memory
                for n in range(len(simulation_actions_taken)):
                    agent_alpha.store_transition(simulation_vehicle_observations[n, :], simulation_actions_taken[n], simulation_rewards[n], simulation_vehicle_next_observations[n, :], simulation_dones[n])

            # Prints final reward
            print("\n------------------------")
            print("Agent alpha final reward:")
            print(alpha_thread.result[3][-1])
            print("------------------------\n")
            all_final_rewards.append(alpha_thread.result[3][-1])
            """
            print("\n------------------------")
            print("Determinist final reward:")
            print(determinist_thread.result[3][-1])
            print("------------------------\n")
            """
            print("\n------------------------")
            print("Last 100 average rewards:")
            print(np.average(all_final_rewards[-100:]))
            print("------------------------\n")



            # Trains the agent
            print("\nLearning...\n")
            for epoch in range(number_of_epochs):
                # Train the network
                agent_alpha.learn()



            # Saves the network during training
            T.save(agent_alpha.Q_eval, "neural_network_models/trained_model.pt")
            T.save(agent_alpha.Q_next, "neural_network_models/q_next.pt")

            # Shares the learning among all agents
            for n in range(1, len(list_of_agents)):
                list_of_agents[n].Q_eval = T.load("neural_network_models/trained_model.pt")
                list_of_agents[n].Q_eval.eval()
                list_of_agents[n].Q_next = T.load("neural_network_models/q_next.pt")
                list_of_agents[n].Q_next.eval()



    # Shows the best reward
    print("\n------------------------")
    print("All simulations finished")
    """
    print("Best score:")
    print(best_simulation_score)
    print("Best final pose:")
    print(best_final_pose)
    print("Best simulation:")
    print(best_simulation_number)
    """
    print("------------------------\n")

    # Save the network after training
    T.save(agent_alpha.q_eval, "neural_network_models/final_trained_model.pt")
    print("Final trained model saved")





if __name__ == '__main__':





    NUMBER_OF_INPUTS = 5
    main()






























































#
