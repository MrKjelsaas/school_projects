import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d





number_of_agents = 5
number_of_dimensions = 2
agent_starting_position = np.zeros(number_of_dimensions)
agent_starting_position[0] = 500
agent_starting_position[1] = -500
agent_starting_velocity = np.zeros(number_of_dimensions)
agent_starting_acceleration = np.zeros(number_of_dimensions)

dt = 1
acceleration_coefficient = 0.1

number_of_steps = 75

live_visualisation = True




def distance_between(x, y):
    return np.sqrt(sum((x-y)**2))



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

# Positions the agents randomly spread out
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

    for i in range(number_of_agents):

        x = np.ones([number_of_agents, 2])
        y = np.ones([number_of_agents, 1])

        for n in range(len(x)):
            if n == i:
                x[n, 0] = 0
                y[n] = 0
            else:
                x[n, 0] = agents[n].position[0] - agents[i].position[0]
                x[n, 1] = 1
                y[n] = agents[n].position[1] - agents[i].position[1]


        a, c = np.linalg.lstsq(x, y, rcond=None)[0]
        b = -1

        x1 = (-a*c) / (a**2 + b**2)
        y1 = (-b*c) / (a**2 + b**2)


        agents[i].position[0] += x1/10
        agents[i].position[1] += y1/10






        """
        distances = np.zeros([number_of_agents])
        for n in range(number_of_agents):
            if n != i:
                distances[n] = agents[n].position[0] - agents[i].position[0]

        distances = np.sort(distances)
        index = np.where(distances == 0)[0]
        if index != 0 and index != 4:
            movement = (distances[index-1] + distances[index+1]) / 2
            agents[i].position[0] += movement
            agents[i].position[1] += a*movement
        """



    # Used to print out information mainly for debuggin
    if step % (number_of_steps/5) == 0:
        pass

    # Updates position based on velocity and acceleration
    for agent in agents:
        agent.update_velocity()
        agent.update_position()

    # Views live plot of position
    if live_visualisation == True:
        for agent in agents:
            ax.scatter(agent.position[0], agent.position[1])

        ax.set_xlim([494.5, 505.5])
        ax.set_ylim([-494.5, -505.5])

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
# Visualize the agent positions
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
