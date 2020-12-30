import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d





number_of_agents = 5
number_of_dimensions = 2
agent_starting_position = np.zeros(number_of_dimensions)
agent_starting_position[0] = 500
agent_starting_position[1] = 750
agent_starting_velocity = np.zeros(number_of_dimensions)
agent_starting_acceleration = np.zeros(number_of_dimensions)

optimal_distance_between_agents = 5
distance_between_agents_coefficient = 0.1
approach_line_coefficient = 0.1 # NEEDS A BETTER VARIABLE NAME





dt = 1
acceleration_coefficient = 0.1

number_of_steps = 100

live_visualisation = True




def distance_between(x, y):
    return np.sqrt(sum((x-y)**2))

def sigmoid(x):
    return 1/(1+np.exp(((-x))))




class Agent:
    def __init__(self):
        global agent_starting_position
        global agent_starting_velocity
        global agent_starting_acceleration
        self.position = agent_starting_position
        self.velocity = agent_starting_velocity
        self.acceleration = agent_starting_acceleration

    def update_velocity(self):
        global dt
        self.velocity += dt*self.acceleration

    def update_position(self):
        global dt
        self.position += dt*self.velocity

    def move_randomly(self, step=1):
        global number_of_dimensions
        for dimension in range(number_of_dimensions):
            self.position[dimension] += 2*step*np.random.random() - step






# Create agents
agents = [deepcopy(Agent()) for n in range(number_of_agents)]

# agent_positions the agents randomly spread out
for agent in agents:
    agent.move_randomly(step=5)

# Visualizes starting position of agents
if number_of_dimensions == 2:
    if live_visualisation == True:
        plt.ion()
        fig, ax = plt.subplots(1)
    else:
        fig = plt.figure()
        ax = plt.axes()
    for agent in agents:
        ax.scatter(agent.position[0], agent.position[1])
    plt.show()





# The main iteration
for step in range(number_of_steps):

    for agent in range(number_of_agents):

        x = np.ones([number_of_agents, 2])
        y = np.ones([number_of_agents, 1])

        for neighbor in range(len(x)):
            if neighbor == agent:
                x[neighbor, 0] = 0
                y[neighbor] = 0
            else:
                x[neighbor, 0] = agents[neighbor].position[0] - agents[agent].position[0]
                x[neighbor, 1] = 1
                y[neighbor] = agents[neighbor].position[1] - agents[agent].position[1]

        # Calculate least squares line
        a, c = np.linalg.lstsq(x, y, rcond=None)[0]
        b = -1
        # Calculates closes point of the least squares line
        x1 = (-a*c) / (a**2 + b**2)
        y1 = (-b*c) / (a**2 + b**2)
        # Placeholder for the next position
        to_move = np.array([x1, y1])
        to_move *= approach_line_coefficient
        # Moves the agent towards the line
        agents[agent].position[0] += to_move[0]
        agents[agent].position[1] += to_move[1]

        # Finds closest neighbor
        to_move = np.zeros([number_of_dimensions])
        neighbor_positions = np.zeros([number_of_agents, number_of_dimensions+1])
        for n in range(number_of_agents):
            neighbor_positions[n, 0] = distance_between(np.array([0, 0]), [x[n, 0], y[n, 0]])
            neighbor_positions[n, 1] = x[n, 0]
            neighbor_positions[n, 2] = y[n]

        shortest_distance = np.sort(neighbor_positions, axis=0)[1, 0]
        closest_neighbor = np.where(neighbor_positions == shortest_distance)[0][0]

        # Moves agent away from closest neighbor
        to_move = np.array([neighbor_positions[closest_neighbor, 1], neighbor_positions[closest_neighbor, 2]])
        factor = sigmoid(optimal_distance_between_agents - distance_between(np.array([0, 0]), to_move)) - 0.5
        to_move *= -factor * distance_between_agents_coefficient



        """ Moves the agent away from all other agents
        for neighbor in range(len(x)):
            if neighbor != agent:
                movement = np.zeros([number_of_dimensions])
                movement[0], movement[1] = x[neighbor, 0], y[neighbor]
                factor = sigmoid(optimal_distance_between_agents - distance_between(np.array([0, 0]), [x[neighbor, 0], y[neighbor, 0]]))
                movement *= -factor * 1
                to_move += movement
        """
        # Updates agent position
        agents[agent].position[0] += to_move[0]
        agents[agent].position[1] += to_move[1]






    # Used to print out information mainly for debuggin
    if step % (number_of_steps/10) == 0:
        pass

        for n in range(number_of_agents):
            print(agents[n].position)
        print("")
        for n in range(number_of_agents):
            print(distance_between(agents[0].position, agents[n].position))
        print("\n\n")

    # Updates position based on velocity and acceleration
    for agent in agents:
        agent.update_velocity()
        agent.update_position()

    # Views live plot of position
    if live_visualisation == True:
        for agent in agents:
            ax.scatter(agent.position[0], agent.position[1])

        ax.set_xlim([agent_starting_position[0] - number_of_agents*optimal_distance_between_agents/2, agent_starting_position[0] + number_of_agents*optimal_distance_between_agents/2])
        ax.set_ylim([agent_starting_position[1] - number_of_agents*optimal_distance_between_agents/2, agent_starting_position[1] + number_of_agents*optimal_distance_between_agents/2])

        plt.draw()
        plt.show()
        plt.pause(0.01)
        ax.clear()





if number_of_dimensions == 2:
    fig = plt.figure()
    ax = plt.axes()

    for agent in agents:
        ax.scatter(agent.position[0], agent.position[1])
    ax.set_xlabel('X Axis')
    ax.set_ylabel('Y Axis')

    plt.show()







"""
# Visualize the agent agent_positions
if number_of_dimensions == 3:
    fig = plt.figure()
    ax = plt.axes(projection="3d")

    for agent in agents:
        ax.scatter(agent.position[0], agent.position[1], agent.position[2])
    ax.set_xlabel('X Axis')
    ax.set_ylabel('Y Axis')
    ax.set_zlabel('Z Axis')

    plt.show()

if number_of_dimensions == 2:
    fig = plt.figure()
    ax = plt.axes()

    for agent in agents:
        ax.scatter(agent.position[0], agent.position[1])
    ax.set_xlabel('X Axis')
    ax.set_ylabel('Y Axis')

    plt.show()
"""
































































# Placeholder
