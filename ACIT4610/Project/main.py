import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from random import random
<<<<<<< HEAD
from scipy.stats import pearsonr


=======
>>>>>>> d85cf1b5c83d17c61dce3c15a51365b44bffdb03


# Essential variables
sampling_rate = 10000
dt = 1/sampling_rate
refractory_period = 0
learning_rate = 0.05  # Number between 0 and 1
<<<<<<< HEAD
minutes_to_sample = 1
number_of_steps = minutes_to_sample*60*sampling_rate  # Each recording lasts 30 min
number_of_electrodes = 60


def hamming(x, y):
    distance = 0
    for i in range(len(x)):
        if x[i] != y[i]:
            distance += 1
    return distance


# Import the data
data = np.loadtxt(r"Data/Dense - 2-1-20.spk.txt")
#print(np.size(data))
#print(np.shape(data))

# Count the number of times each neuron fires
times_fired_in_experiment = np.zeros([number_of_electrodes])
for n in range(len(data)):
    times_fired_in_experiment[int(data[n, 1])-1] += 1
#print(times_fired_in_experiment)

# Count the average firing rates
average_firing_rates_in_experiment = 1 / (times_fired_in_experiment / data[-1, 0])
#print(average_firing_rates_in_experiment)

# Make the spike train matrix
spike_trains = np.zeros([number_of_electrodes, number_of_steps])
for i in range(len(data)):
    x = int((data[i, 0] / len(data)) * number_of_steps)
    y = int(data[i, 1])
    spike_trains[y, x] += 1





# Make a network with 60 nodes
network = nx.Graph()
for n in range(number_of_electrodes):
    network.add_node(n)

# Add weighted edges between all nodes
# Using Hamming distance:
"""
biggest_distance = 0
distances = np.zeros([60, 60])
for i in range(number_of_electrodes-1):
    for j in range(i+1, number_of_electrodes):
        distance = hamming(spike_trains[i, :], spike_trains[j, :])
        distances[i, j] = distance
        if distance > biggest_distance:
            biggest_distance = distance

for i in range(number_of_electrodes-1):
    for j in range(i+1, number_of_electrodes):
        network.add_edge(i, j, weight=1-(distances[i, j])/biggest_distance)
"""
# Using Pearson correlation coefficient:
for i in range(number_of_electrodes-1):
    for j in range(i+1, number_of_electrodes):
        network.add_edge(i, j, weight=pearsonr(spike_trains[i, :], spike_trains[j, :])[0])
=======
number_of_steps = 30*60*sampling_rate  # Each recording lasts 30 min

# Make a network with 59 nodes
network = nx.Graph()
for n in range(60):
    network.add_node(n)

# Add weighted edges between all nodes
for i in range(60):
    for j in range(i+1, 60):
        network.add_edge(i, j, weight=random())
>>>>>>> d85cf1b5c83d17c61dce3c15a51365b44bffdb03

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

<<<<<<< HEAD
# Update weights
#network[0][59]['weight'] += (1-network[0][59]['weight']) * learning_rate



# Visualize the network

e1 = [(u, v) for (u, v, d) in network.edges(data=True) if 0 <= d["weight"] < 0.1]
e2 = [(u, v) for (u, v, d) in network.edges(data=True) if 0.1 <= d["weight"] < 0.2]
e3 = [(u, v) for (u, v, d) in network.edges(data=True) if 0.2 <= d["weight"] < 0.3]
e4 = [(u, v) for (u, v, d) in network.edges(data=True) if 0.3 <= d["weight"] < 0.4]
e5 = [(u, v) for (u, v, d) in network.edges(data=True) if 0.4 <= d["weight"] < 0.5]
e6 = [(u, v) for (u, v, d) in network.edges(data=True) if 0.5 <= d["weight"] < 0.6]
e7 = [(u, v) for (u, v, d) in network.edges(data=True) if 0.6 <= d["weight"] < 0.7]
e8 = [(u, v) for (u, v, d) in network.edges(data=True) if 0.7 <= d["weight"] < 0.8]
e9 = [(u, v) for (u, v, d) in network.edges(data=True) if 0.8 <= d["weight"] < 0.9]
e10 = [(u, v) for (u, v, d) in network.edges(data=True) if 0.9 <= d["weight"] < 1]


position = nx.spring_layout(network)
nx.draw_networkx_nodes(network, pos=position)

nx.draw_networkx_edges(network, pos=position, edgelist=e1, alpha = 0.1)
nx.draw_networkx_edges(network, pos=position, edgelist=e2, alpha = 0.2)
nx.draw_networkx_edges(network, pos=position, edgelist=e3, alpha = 0.3)
nx.draw_networkx_edges(network, pos=position, edgelist=e4, alpha = 0.4)
nx.draw_networkx_edges(network, pos=position, edgelist=e5, alpha = 0.5)
nx.draw_networkx_edges(network, pos=position, edgelist=e6, alpha = 0.6)
nx.draw_networkx_edges(network, pos=position, edgelist=e7, alpha = 0.7)
nx.draw_networkx_edges(network, pos=position, edgelist=e8, alpha = 0.8)
nx.draw_networkx_edges(network, pos=position, edgelist=e9, alpha = 0.9)
nx.draw_networkx_edges(network, pos=position, edgelist=e10, alpha = 1)


#nx.draw(network, pos=nx.circular_layout(network))
plt.show()
=======



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
>>>>>>> d85cf1b5c83d17c61dce3c15a51365b44bffdb03








<<<<<<< HEAD
=======
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
>>>>>>> d85cf1b5c83d17c61dce3c15a51365b44bffdb03



"""
Slagplan:

Fitness function:
Telle antall ganger hver av elektrodene er fyrt i eksperimentet
Telle antall ganger hver av elektrodene i simuleringen vår er fyrt
Ta antall ganger elektrodene i eksperimentet er fyrt, og trekk fra antall ganger våre er fyrt (for hver av nodene)

Bias:
Alle noder har en fast input (supernode/solen) som alltid gir inn 1
"""
