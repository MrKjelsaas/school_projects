import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from random import random


# Essential variables
sampling_rate = 10000
dt = 1/sampling_rate
refractory_period = 0
learning_rate = 0.05  # Number between 0 and 1
number_of_steps = 30*60*sampling_rate  # Each recording lasts 30 min

# Make a network with 59 nodes
network = nx.Graph()
for n in range(60):
    network.add_node(n)

# Add weighted edges between all nodes
for i in range(60):
    for j in range(i+1, 60):
        network.add_edge(i, j, weight=random())

# Set initial firing state
nx.set_node_attributes(network, 0, 'firing')
#print(network.nodes[0])

# Change firing state
network.nodes[0]['firing'] = 1
#print(network.nodes[0])
network.nodes[0]['firing'] = 0
#print("Node 0 firing status:", network.nodes[0]['firing'])

# Iterate over all neighbors of a node
for edge in network.edges(0):
    pass
    #print(edge[1])




"""
# Update weights
print(network[0][59]['weight'])
for i in range(10):
    network[0][59]['weight'] += (1-network[0][59]['weight']) * learning_rate
    print(network[0][59]['weight'])
"""



"""
# Visualize the network
nx.draw(network)
plt.show()
"""








# Import the data
data = np.loadtxt(r"Data/Dense - 2-1-20.spk.txt")
#print(np.size(data))
#print(np.shape(data))

# Count the number of times each neuron fires
times_fired_in_experiment = np.zeros([60])
for n in range(len(data)):
    times_fired_in_experiment[int(data[n, 1])-1] += 1
#print(times_fired_in_experiment)

# Count the average firing rates
average_firing_rates_in_experiment = 1 / (times_fired_in_experiment / data[-1, 0])
#print(average_firing_rates_in_experiment)



"""
Slagplan:

Fitness function:
Telle antall ganger hver av elektrodene er fyrt i eksperimentet
Telle antall ganger hver av elektrodene i simuleringen vår er fyrt
Ta antall ganger elektrodene i eksperimentet er fyrt, og trekk fra antall ganger våre er fyrt (for hver av nodene)

Bias:
Alle noder har en fast input (supernode/solen) som alltid gir inn 1
"""
