import numpy as np
import networkx as nx
import matplotlib
from pylab import *
import random as rd
from random import random
import pycxsimulator
from copy import deepcopy
from networkx.readwrite import json_graph



seconds_to_sample = 10
max_mutations = 25
training_iterations = 1000

#seconds_to_sample = int(input("Enter seconds to sample: "))
#training_iterations = int(input("Enter number of training iterations: "))

number_of_electrodes = 60
sampling_rate = 1000
dt = 1/sampling_rate

minutes_to_sample = int(seconds_to_sample)
number_of_steps = seconds_to_sample*sampling_rate  # Each recording lasts ca 45 min
generations = number_of_steps
initial_self_charge = 0.1
initial_charge = 0
initial_threshold = 100





def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def crossover(x, y, method="average"):
    if method == "average":
        return (x+y)/2

def mutate(x, method="random"):
    if method == "random":
        return x * (random()/5 + 0.9)
    if method == "add_node":
        x.add_node(x.number_of_nodes(), charge=initial_charge, firing=0, threshold = initial_threshold,
                        refraction_period = 4, self_charge = initial_self_charge, times_fired=0)
        return x
    if method == "add_edge":
        x.add_edge(randint(0, x.number_of_nodes()), randint(0, x.number_of_nodes()), weight=random())
        return x
    if method == "random_attribute":
        attribute_to_evolve = randint(1, 5)
        node_to_evolve = randint(0, x.number_of_nodes())
        if attribute_to_evolve == 1:
            x.nodes[node_to_evolve]["threshold"] = mutate(x.nodes[node_to_evolve]["threshold"])
        if attribute_to_evolve == 2:
            x.nodes[node_to_evolve]["refraction_period"] = mutate(x.nodes[node_to_evolve]["refraction_period"])
        if attribute_to_evolve == 3:
            x.nodes[node_to_evolve]["self_charge"] = mutate(x.nodes[node_to_evolve]["self_charge"])
        if attribute_to_evolve == 4:
            neighbor_to_evolve = randint(0, x.number_of_nodes())
            x[node_to_evolve][neighbor_to_evolve]['weight'] = mutate(x[node_to_evolve][neighbor_to_evolve]['weight'])
        return x
    if method == "random_weight":
        node_to_evolve = randint(0, x.number_of_nodes())
        neighbor_to_evolve = randint(0, x.number_of_nodes())
        x[node_to_evolve][neighbor_to_evolve]['weight'] = mutate(x[node_to_evolve][neighbor_to_evolve]['weight'])
        return x
    if method == "all_attributes":
        for node in range(x.number_of_nodes()):
            x.nodes[node]["threshold"] = mutate(x.nodes[node]["threshold"])
            x.nodes[node]["refraction_period"] = mutate(x.nodes[node]["refraction_period"])
            x.nodes[node]["self_charge"] = mutate(x.nodes[node]["self_charge"])
            for neighbor in range(x.number_of_nodes()):
                if node != neighbor:
                    x[node][neighbor]['weight'] = mutate(x[node][neighbor]['weight'])
        return x

def fitness(x, y, method="absolute_difference"):
    if method == "absolute_difference":
        if type(x) is list or type(x) is np.ndarray:
            difference = 0
            for n in range(len(x)):
                difference += abs(x[n] - y[n])
            return difference
        return abs(sum(x - y))

    if method == "squared_difference":
        if type(x) is list or type(x) is np.ndarray:
            difference = 0
            for n in range(len(x)):
                difference += (x[n] - y[n]) ** 2
            return difference
        return (x - y) ** 2

def initialize(): # Create network with nodes
    network = nx.DiGraph()
    for n in range(number_of_electrodes):
        network = mutate(network, method="add_node")

    #Create all edges, bi directional = 3600
    for i in range(number_of_electrodes):
        for j in range(number_of_electrodes):
            if i != j:
                network.add_edge(i, j, weight=random())

    return network

def fire(network):
    next_charges = np.zeros([number_of_electrodes])
    next_firings = np.zeros([number_of_electrodes])

    for node in range(number_of_electrodes):
        if 0 < network.nodes[node]['firing'] < 1:
            network.nodes[node]['firing'] = 0
        if network.nodes[node]['firing'] == 1:
            network.nodes[node]['times_fired'] += 1
            next_firings[node] = -network.nodes[node]['refraction_period']
        elif network.nodes[node]['firing'] < 0:
            network.nodes[node]['firing'] += 1
        else:
            if network.nodes[node]['charge'] > network.nodes[node]['threshold']:
                next_firings[node] = 1
            else:
                next_charges[node] = network.nodes[node]['charge'] + network.nodes[node]['self_charge']
                for neighbor in range(number_of_electrodes):
                    if node != neighbor:
                        if network.nodes[neighbor]['firing'] == 1:
                            next_charges[node] += network[neighbor][node]['weight']

    for node in range(number_of_electrodes):
        network.nodes[node]['firing'] = next_firings[node]
        network.nodes[node]['charge'] = next_charges[node]
        #print("Next firing:", next_firings[node])
        #print("Next charges:", next_charges[node])

    return network

def show_network(network):
    max_weight = 0
    for node in range(network.number_of_nodes()):
        for neighbor in range(network.number_of_nodes()):
            if node != neighbor:
                if network[node][neighbor]['weight'] > max_weight:
                    max_weight = network[node][neighbor]['weight']
    e1 = [(u, v) for (u, v, d) in network.edges(data=True) if 0 <= d["weight"] < 0.1*max_weight]
    e2 = [(u, v) for (u, v, d) in network.edges(data=True) if 0.1*max_weight <= d["weight"] < 0.2*max_weight]
    e3 = [(u, v) for (u, v, d) in network.edges(data=True) if 0.2*max_weight <= d["weight"] < 0.3*max_weight]
    e4 = [(u, v) for (u, v, d) in network.edges(data=True) if 0.3*max_weight <= d["weight"] < 0.4*max_weight]
    e5 = [(u, v) for (u, v, d) in network.edges(data=True) if 0.4*max_weight <= d["weight"] < 0.5*max_weight]
    e6 = [(u, v) for (u, v, d) in network.edges(data=True) if 0.5*max_weight <= d["weight"] < 0.6*max_weight]
    e7 = [(u, v) for (u, v, d) in network.edges(data=True) if 0.6*max_weight <= d["weight"] < 0.7*max_weight]
    e8 = [(u, v) for (u, v, d) in network.edges(data=True) if 0.7*max_weight <= d["weight"] < 0.8*max_weight]
    e9 = [(u, v) for (u, v, d) in network.edges(data=True) if 0.8*max_weight <= d["weight"] < 0.9*max_weight]
    e10 = [(u, v) for (u, v, d) in network.edges(data=True) if 0.9*max_weight <= d["weight"] < max_weight]

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
data = np.loadtxt(r"Data/Sparse - 7-4-35.spk.txt")
#print(np.shape(data))

# Count the number of times each neuron fires
times_fired_in_experiment = np.zeros([number_of_electrodes])
initial_charges = np.zeros([number_of_electrodes])
for n in range(len(data)):
    if data[n, 0] > seconds_to_sample:
        break
    times_fired_in_experiment[int(data[n, 1])] += 1
#print(times_fired_in_experiment)
# Count the average firing rates
#average_firing_rates_in_experiment = 1 / (times_fired_in_experiment / seconds_to_sample)
#print(average_firing_rates_in_experiment)

# Make the spike train matrix
spike_trains = np.zeros([number_of_electrodes, number_of_steps])
for i in range(number_of_steps):
    spike_trains[int(data[i, 1]), i] += 1
#print(spike_trains[:5, :10])





# Initialize network
fittest_network = initialize()

# Check fitness of initial network
print("Firing initial network")
network_model = fire(fittest_network)
for gen in range(generations):
    network_model = fire(network_model)

# Calculate fitness
times_fired_in_network = np.zeros([number_of_electrodes])
for node in range(number_of_electrodes):
    times_fired_in_network[node] = network_model.nodes[node]['times_fired']
best_fitness_result = fitness(times_fired_in_network, times_fired_in_experiment)
print("Initial network fitness", best_fitness_result)

# Initialize mutated networks
mutated_networks = [None, None, None, None, None]
for n in range(len(mutated_networks)):
    mutated_networks[n] = deepcopy(fittest_network)

# Train the network
time_since_last_mutation = 0
for training_iteration in range(training_iterations):
    print("\nStarting training iteration", training_iteration+1)
    fitness_results = np.zeros([len(mutated_networks)])
    times_fired_in_network = np.zeros([len(mutated_networks)+1, number_of_electrodes])

    # Fire the networks
    for n in range(len(mutated_networks)):
        print("Firing network", n)
        for node in range(number_of_electrodes):
            mutated_networks[n].nodes[node]['charge'] = initial_charge
            mutated_networks[n].nodes[node]['times_fired'] = 0
            mutated_networks[n].nodes[node]['firing'] = 0

        for gen in range(generations):
            mutated_networks[n] = fire(mutated_networks[n])

        # Calculate fitness
        for node in range(number_of_electrodes):
            times_fired_in_network[n, node] = mutated_networks[n].nodes[node]['times_fired']
        fitness_results[n] = fitness(times_fired_in_network[n], times_fired_in_experiment)

    print("\nFitness results:\n", fitness_results)

    # Stage the fittest network for mutation
    if min(fitness_results) < best_fitness_result:
        print("\nFound better model")
        best_fitness_result = min(fitness_results)
        fittest_network = deepcopy(mutated_networks[argmin(fitness_results)])
        for n in range(len(mutated_networks)):
            mutated_networks[n] = deepcopy(fittest_network)
        time_since_last_mutation = 0
    else:
        time_since_last_mutation +=1
    if time_since_last_mutation > max_mutations:
        print("\nMax mutations reached, resetting mutations")
        for n in range(len(mutated_networks)):
            mutated_networks[n] = deepcopy(fittest_network)
        time_since_last_mutation = 0

    # Display times fired in fittest network
    for node in range(number_of_electrodes):
        times_fired_in_network[len(mutated_networks), node] = fittest_network.nodes[node]['times_fired']
    print("\n")
    print("Times fired in experiment:")
    print(times_fired_in_experiment)
    print("\nTimes fired in fittest network:")
    print(times_fired_in_network[len(mutated_networks), :])
    print("\nBest fitness:", best_fitness_result)
    print("\n")

    if best_fitness_result == 0:
        print("\nFound optimal model!!\n")
        break

    # Mutate the networks
    for n in range(len(mutated_networks)):
        for node in range(mutated_networks[n].number_of_nodes()):
            mutated_networks[n].nodes[node]["threshold"] *= (sigmoid(times_fired_in_network[n, node] - times_fired_in_experiment[node]) + 0.5)
            mutated_networks[n].nodes[node]["refraction_period"] *= (sigmoid(times_fired_in_experiment[node] - times_fired_in_network[n, node]) + 0.5)
            mutated_networks[n].nodes[node]["self_charge"] *= (sigmoid(times_fired_in_experiment[node] - times_fired_in_network[n, node]) + 0.5)
            for neighbor in range(mutated_networks[n].number_of_nodes()):
                if node != neighbor:
                    mutated_networks[n][neighbor][node]['weight'] *= (sigmoid(times_fired_in_experiment[node] - times_fired_in_network[n, node]) + 0.5)

        mutated_networks[n] = mutate(mutated_networks[n], method="all_attributes")


# Shows the network info
#print(json_graph.node_link_data(fittest_network))

# Saves the network
nx.write_gml(fittest_network, r"Models/fittest_network.gml")
# Loads the network
#test_network = nx.read_gml(r"Models/fittest_network.gml")



for n in range(number_of_electrodes):
    if times_fired_in_network[len(mutated_networks), n] == times_fired_in_experiment[n]:
        plt.scatter(n, times_fired_in_experiment[n], c='g')
    else:
        plt.scatter(n, times_fired_in_network[len(mutated_networks), n], c='r')
        plt.scatter(n, times_fired_in_experiment[n], c='b')
plt.xlabel("Electrode number")
plt.ylabel("Times fired")
plt.legend(["Network", "Experiment", "Both"])
plt.show()



#show_network(fittest_network)










"""
Initially:
- Make a network
- Calculate the gradients of the network and update attributes

Repeat:
- Copy the updated network to the 5 mutated_networks slots
- Mutate the 5 networks randomly
- Fire the 5 networks and calculate fitness_results
- Select the best network and copy it to "fittest network"

Finally:
- Present or visualize the network in some form
"""

"""
To do:
- Make the gradient function
    - How to calculate gradient for all attribues (and weights)?
        - x *= sigmoid(y - x) + 0.5
"""





"""
nx.draw(network)
plt.show()

#print("List Nodes: ", list(network.nodes.data()))
#print("List Edges: ", list(network.edges.data()))
#print("List adjesent edges: ", list(network.adj[1]))
#print("Nubmer of nodes: ", network.number_of_nodes())
#print("Number of edges: ", network.number_of_edges())
#print("List adjesent edges: ", list(network.adj[1]))

"""
