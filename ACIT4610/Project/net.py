import numpy as np
import networkx as nx
import matplotlib
from pylab import *
import random as rd
from random import random
import pycxsimulator
from copy import deepcopy

number_of_electrodes = 60
sampling_rate = 1000
dt = 1/sampling_rate
minutes_to_sample = 10/60
seconds_to_sample = int(minutes_to_sample * 60)
number_of_steps = seconds_to_sample*sampling_rate  # Each recording lasts ca 45 min
generations = number_of_steps
training_iterations = 1000
initial_threshold = 100



# These functions are as basic as it gets right now
# But here we can experiment
def crossover(x, y, method="average"):
    if method == "average":
        return (x+y)/2

def mutate(x, method="random"):
    if method == "random":
        return x * (random() + 0.5)
    if method == "add_node":
        x.add_node(x.number_of_nodes(), charge=0, firing=0, threshold = initial_threshold,
                    refraction_period = 4, chance_of_self_poke = 10, times_fired=0)
        return x
    if method == "add_edge":
        x.add_edge(randint(0, x.number_of_nodes()-1), randint(0, x.number_of_nodes()-1), weight=1)
        return x

def fitness(x, y, method="squared_difference"):
    if method == "squared_difference":
        if type(x) is list:
            difference = 0
            for n in range(len(x)):
                difference += abs(x[n] - y[n])
            return difference
        return abs(sum(x - y))





def initialize(): # add atributes for evo
    network = nx.Graph()
    for n in range(number_of_electrodes):
        network.add_node(n, charge=0, firing=0, threshold = initial_threshold,
                        refraction_period = 4, chance_of_self_poke = 10, times_fired=0)

    #Create all nodes, bi directional = 3600
    for i in range(number_of_electrodes):
        for j in range(number_of_electrodes):
            network.add_edge(i, j, weight=1)

    return network



def fire(network):

    next_charges = np.zeros([number_of_electrodes])
    next_firings = np.zeros([number_of_electrodes])
    for node in range(number_of_electrodes):
        if 0 <= network.nodes[node]['firing'] < 1:
            network.nodes[node]['firing'] = 0
        if network.nodes[node]['firing'] == 1:
            network.nodes[node]['times_fired'] += 1
            next_firings[node] = -network.nodes[node]['refraction_period']
            next_charges[node] = 0
        elif network.nodes[node]['firing'] < 0:
            network.nodes[node]['firing'] += 1
        else:
            if network.nodes[node]['charge'] > network.nodes[node]['threshold']:
                next_firings[node] = 1
            else:
                next_charges[node] = network.nodes[node]['charge']
                if random()*100 > network.nodes[node]['chance_of_self_poke']:
                    next_charges[node] += random()
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
#print(times_fired_in_experiment)
# Count the average firing rates
#average_firing_rates_in_experiment = 1 / (times_fired_in_experiment / seconds_to_sample)
#print(average_firing_rates_in_experiment)

# Make the spike train matrix
spike_trains = np.zeros([number_of_electrodes, number_of_steps])
for i in range(number_of_steps):
    spike_trains[int(data[i, 1]), i] += 1
#print(spike_trains[:5, :10])


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






# Initialize network
fittest_network = initialize()

# Check fitness of initial network
print("Firing initial network")
for gen in range(generations):
    next_gen_model = fire(fittest_network)
    network_model = next_gen_model

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

# Mutate the networks
for mutated_network in mutated_networks:
    attribute_to_evolve = randint(1, 4)
    node_to_evolve = randint(0, 59)
    if attribute_to_evolve == 1:
        mutated_network.nodes[node_to_evolve]["threshold"] = mutate(mutated_network.nodes[node_to_evolve]["threshold"])
    if attribute_to_evolve == 2:
        mutated_network.nodes[node_to_evolve]["refraction_period"] = mutate(mutated_network.nodes[node_to_evolve]["refraction_period"])
    if attribute_to_evolve == 3:
        mutated_network.nodes[node_to_evolve]["chance_of_self_poke"] = mutate(mutated_network.nodes[node_to_evolve]["chance_of_self_poke"])
    if attribute_to_evolve == 4:
        neighbor_to_evolve = randint(0, 59)
        mutated_network[node_to_evolve][neighbor_to_evolve]['weight'] = mutate(mutated_network[node_to_evolve][neighbor_to_evolve]['weight'])



# Train the network
for training_iteration in range(training_iterations):
    print("Starting training iteration", training_iteration+1)
    fitness_results = np.zeros([len(mutated_networks)])

    # Fire the networks
    for n in range(len(mutated_networks)):
        #print("Firing mutated network", n)
        for node in range(number_of_electrodes):
            mutated_networks[n].nodes[node]['charge'] = 0
            mutated_networks[n].nodes[node]['times_fired'] = 0
            mutated_networks[n].nodes[node]['firing'] = 0

        network_model = fire(mutated_networks[n])
        for gen in range(generations):
            network_model = fire(network_model)

        # Calculate fitness
        times_fired_in_network = np.zeros([number_of_electrodes])
        for node in range(number_of_electrodes):
            times_fired_in_network[node] = network_model.nodes[node]['times_fired']
        fitness_results[n] = fitness(times_fired_in_network, times_fired_in_experiment)

    print("\nFitness results:\n", fitness_results)
    print("\n")
    print("Times fired in experiment:\n", times_fired_in_experiment)
    print("\nTimes fired in network:\n", times_fired_in_network)
    print("\n")

    # Stage the fittest network for mutation
    if min(fitness_results) < best_fitness_result:
        print("Found better model")
        fittest_network = deepcopy(mutated_networks[argmin(fitness_results)])
        best_fitness_result = min(fitness_results)
        for n in range(len(mutated_networks)):
            mutated_networks[n] = deepcopy(fittest_network)

    print("Best fitness: network number", best_fitness_result)




    # Mutate the networks
    for mutated_network in mutated_networks:
        attribute_to_evolve = randint(1, 4)
        node_to_evolve = randint(0, 59)
        if attribute_to_evolve == 1:
            mutated_network.nodes[node_to_evolve]["threshold"] = mutate(mutated_network.nodes[node_to_evolve]["threshold"])
        if attribute_to_evolve == 2:
            mutated_network.nodes[node_to_evolve]["refraction_period"] = mutate(mutated_network.nodes[node_to_evolve]["refraction_period"])
        if attribute_to_evolve == 3:
            mutated_network.nodes[node_to_evolve]["chance_of_self_poke"] = mutate(mutated_network.nodes[node_to_evolve]["chance_of_self_poke"])
        if attribute_to_evolve == 4:
            neighbor_to_evolve = randint(0, 59)
            mutated_network[node_to_evolve][neighbor_to_evolve]['weight'] = mutate(mutated_network[node_to_evolve][neighbor_to_evolve]['weight'])




















"""
- Copy the #fittest_network into all the slots in the mutated_networks list # Done
- Mutate all the networks in the mutated_networks list # Done
- Calculate the fitness function for all the networks in the mutated_networks list and the fittest_network
- Repeat

Optional: ?
- Copy the #fittest_network into all the slots in the mutated_networks list
- Mutate all the networks in the mutated_networks list
- Select the two networks with the best fitness
- Mate them
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
