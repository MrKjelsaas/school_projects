import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from random import random
from scipy.stats import pearsonr



# Essential variables
sampling_rate = 10000
dt = 1/sampling_rate
minutes_to_sample = 1/60
seconds_to_sample = int(minutes_to_sample * 60)
number_of_steps = seconds_to_sample*sampling_rate  # Each recording lasts ca 45 min
generations = number_of_steps
number_of_electrodes = 60
training_iterations = 50

refractory_period = 3
firing_threshold = 10
learning_rate = 0.2  # Number between 0 and 1
#initial_charge = 0.1
background_noise = 0.01





def hamming(x, y):
    distance = 0
    for i in range(len(x)):
        if x[i] != y[i]:
            distance += 1
    return distance

def show_network(network):
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

    plt.show()





# Import the data
data = np.loadtxt(r"Data/Dense - 2-1-20.spk.txt")
#print(np.shape(data))

# Count the number of times each neuron fires
times_fired_in_experiment = np.zeros([number_of_electrodes])
initial_charges = np.zeros([number_of_electrodes])
for n in range(len(data)):
    if data[n, 0] > seconds_to_sample:
        break
    times_fired_in_experiment[int(data[n, 1])-1] += 1
self_charges = np.zeros([number_of_electrodes])
for n in range(number_of_electrodes):
    self_charges[n] = times_fired_in_experiment[n] / sum(times_fired_in_experiment)
#print(times_fired_in_experiment)
# Count the average firing rates
average_firing_rates_in_experiment = 1 / (times_fired_in_experiment / seconds_to_sample)
#print(average_firing_rates_in_experiment)

# Make the spike train matrix
spike_trains = np.zeros([number_of_electrodes, number_of_steps])
for i in range(len(data)):
    x = int((data[i, 0] / len(data)) * number_of_steps)
    y = int(data[i, 1])
    spike_trains[y, x] += 1

"""
number_of_steps = 100
# Visualize spikes
for i in range(number_of_electrodes):
    #print("Checking electrode", i)
    for j in range(number_of_steps):
        if spike_trains[i, j] >= 1:
            plt.scatter(j, i)
plt.show()
number_of_steps = minutes_to_sample*60*sampling_rate  # Each recording lasts ca 45 min
"""





"""
--------------------------------------------
INITIALIZE
--------------------------------------------
"""



# Make a network with 60 nodes
network = nx.Graph()
for n in range(number_of_electrodes):
    network.add_node(n)

# Add weighted edges between all nodes
# Using Hamming distance:
"""
print("Calculating hamming distance")
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

# Using Pearson correlation coefficient:
print("Calculating Pearson correlation coefficient")
for i in range(number_of_electrodes-1):
    for j in range(i+1, number_of_electrodes):
        network.add_edge(i, j, weight=pearsonr(spike_trains[i, :], spike_trains[j, :])[0])
"""
# Randomly generated
for i in range(number_of_electrodes):
    for j in range(number_of_electrodes):
        if not i == j:
            network.add_edge(i, j, weight=random())

# Set intial firing state
nx.set_node_attributes(network, 0, 'firing')

# Counts the number of times the node is fired
nx.set_node_attributes(network, 0, 'times_fired')

# Set initial charge
nx.set_node_attributes(network, 0, 'charge')

# Set one random node to fire
#network.nodes[int(np.round(random()*number_of_electrodes))]['firing'] = 1





"""
--------------------------------------------
FIRING
--------------------------------------------
"""

for iteration in range(training_iterations):
    print("Starting iteration", iteration+1)
    print("Firing threshold:", firing_threshold)

    for node in range(number_of_electrodes):
        network.nodes[node]['charge'] = initial_charges[n]
    times_fired_in_network = np.zeros([number_of_electrodes])

    # Placeholder for the next charges
    next_charges = np.zeros([number_of_electrodes])
    next_firings = np.zeros([number_of_electrodes])

    print("\nFiring network with", generations, "generations")
    for generation in range(generations):
        if generation % 1000 == 0:
            print("Generation", generation)
        for node in range(number_of_electrodes):
            if network.nodes[node]['firing'] == 1:
                next_firings[node] = -refractory_period
                next_charges[node] = 0
            elif network.nodes[node]['firing'] < 0:
                next_firings[node] += 1
            else:
                if network.nodes[node]['charge'] > firing_threshold:
                    next_firings[node] = 1
                    times_fired_in_network[node] += 1
                else:
                    next_charges[node] = network.nodes[node]['charge'] + self_charges[node]
                    for neighbor in range(number_of_electrodes):
                        if node != neighbor:
                            if network.nodes[neighbor]['firing'] == 1:
                                next_charges[node] += network[neighbor][node]['weight']
        for node in range(number_of_electrodes):
            network.nodes[node]['firing'] = next_firings[node]
            network.nodes[node]['charge'] = next_charges[node]

    #print("\nCurrent next charges:")
    #print(next_charges)



    """
    --------------------------------------------
    EVALUATE
    --------------------------------------------
    """



    print("\n")
    print("Times fired in experiment:\n", times_fired_in_experiment)
    print("\nTimes fired in network:\n", times_fired_in_network)
    print("\n")

    if sum(times_fired_in_network) > sum(times_fired_in_experiment):
        firing_threshold *= 1.2
    else:
        firing_threshold *= 0.8

    #gradients = times_fired_in_network - times_fired_in_experiment
    gradients = np.zeros([number_of_electrodes])
    #print("Gradients:")
    #print(gradients)
    for gradient in range(len(gradients)):
        if times_fired_in_network[gradient] < times_fired_in_experiment[gradient]:
            gradients[gradient] = 1 + learning_rate # 1 + (times_fired_in_network[gradient] / times_fired_in_experiment[gradient])
        elif times_fired_in_network[gradient] > times_fired_in_experiment[gradient]:
            gradients[gradient] = 1 - learning_rate # 1 - (times_fired_in_experiment[gradient] / times_fired_in_network[gradient])

    for i in range(number_of_electrodes):
        for j in range(number_of_electrodes):
            if i != j:
                network[j][i]['weight'] *= gradients[i]



"""
--------------------------------------------
VISUALIZATION
--------------------------------------------
"""









"""
# SOME HELPFUL DOCUMENTATION

# Make a network with 60 nodes
network = nx.Graph()
for n in range(number_of_electrodes):
    network.add_node(n)

# Add randomly weighted edges between all nodes
for i in range(number_of_electrodes-1):
    for j in range(i+1, number_of_electrodes):
        network.add_edge(i, j, weight=random())

# Update weights
print(network[0][59]['weight'])
for i in range(10):
    network[0][59]['weight'] += (1-network[0][59]['weight']) * learning_rate
    print(network[0][59]['weight'])

# Set initial firing state
nx.set_node_attributes(network, 0, 'firing')
#print(network.nodes[0])

# Change firing state
network.nodes[0]['firing'] = 1
#print(network.nodes[0])
network.nodes[0]['firing'] = 0
#print("Node 0 firing status:", network.nodes[0]['firing'])

# Iterate over all neighbors of node 0
for edge in network.edges(0):
    #print(edge[1])

# Calculate sum of weights for each node
for node_number in range(number_of_electrodes):
    weight_sum = 0
    for i in range(number_of_electrodes):
        if i != node_number:
            weight_sum += network[node_number][i]['weight']
    print("Node:", node_number, "Weight sum:", weight_sum)

# Visualize the entire network
nx.draw(network)
plt.show()
# Visualizing the network with spring layout and alpha
#show_network(network)
"""








"""
Slagplan:

Fitness function:
Telle antall ganger hver av elektrodene er fyrt i eksperimentet
Telle antall ganger hver av elektrodene i simuleringen vår er fyrt
Ta antall ganger elektrodene i eksperimentet er fyrt, og trekk fra antall ganger våre er fyrt (for hver av nodene)

Bias:
Alle noder har en fast input (supernode/solen) som alltid gir inn 1
"""
