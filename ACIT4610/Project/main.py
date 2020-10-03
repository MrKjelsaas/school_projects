import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from random import random


# Essential variables
sampling_rate = 25000
dt = 1/sampling_rate
refractory_period = 0
learning_rate = 0.05  # Number between 0 and 1
number_of_steps = 30*60*sampling_rate  # Each step is 40us, and each epoke lasts 30 min

# Make a network with 59 nodes
network = nx.Graph()
for n in range(59):
    network.add_node(n+1)

# Add weighted edges between all nodes
for i in range(59):
    for j in range(i+1, 59):
        network.add_edge(i+1, j+1, weight=random())

"""
# Update weights
print(network[1][59]['weight'])
for i in range(10):
    network[1][59]['weight'] += (1-network[1][59]['weight']) * learning_rate
    print(network[1][59]['weight'])
"""



"""
# Visualize the network
nx.draw(network)
plt.show()
"""








# Import the data
data = np.loadtxt(r"Data/Dense - 2-1-20.spk.txt")
print(np.size(data))
print(np.shape(data))

# Count the number of times each neuron fires
occurences = np.zeros([59])
for n in range(len(data)):
    occurences[int(data[n, 1])-1] += 1
print(occurences)

# Count the average firing rates
space = 100000
for n in range(len(data)-1):
    time = abs(data[n, 0] - data[n+1, 0])
    if time != 0:
        if time < space:
            space = time
print(time)

"""
Slagplan:

Fitness function:
Telle antall ganger hver av elektrodene er fyrt i eksperimentet
Telle antall ganger hver av elektrodene i simuleringen vår er fyrt
Ta antall ganger elektrodene i eksperimentet er fyrt, og trekk fra antall ganger våre er fyrt (for hver av nodene)

Bias:
Alle noder har en fast input (supernode/solen) som alltid gir inn 1
"""
