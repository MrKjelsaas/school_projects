import numpy as np
import networkx as nx
import matplotlib
from pylab import *
import random as rd
from random import random
import pycxsimulator
from copy import deepcopy

number_of_electrodes = 60
node_dies_when_refraction_period = 2



# These functions are as basic as it gets right now
# But here we can experiment
def crossover(x, y, method="average"):
    if method == "average":
        return (x+y)/2

def mutate(x, method="random"):
    if method == "random":
        return x * (random() + 0.5)
    if method == "add_node":
        x.add_node(x.number_of_nodes(), charge=rd.random(), spike=rd.randint(0,1), rest_period=0,
                        weighted_sum=0, threshold = 1000.00, refraction_period = 4, chance_of_self_poke = 30)
        return x
    if method == "add_edge":
        x.add_edge(randint(0, x.number_of_nodes()-1), randint(0, x.number_of_nodes()-1), weight=random())
        return x

def fitness(x, y, method="squared_difference"):
    if method == "squared_difference":
        if type(x) is list:
            difference = 0
            for n in range(len(x)):
                difference += (x[n] - y[n])**2
            return difference
        return sum((x - y)**2)





def initialize(): # add atributes for evo
    network = nx.Graph()
    for n in range(number_of_electrodes):
        network.add_node(n, charge=rd.random(), spike=rd.randint(0,1), rest_period=0,
                        weighted_sum=0, threshold = 1000.00, refraction_period = 4, chance_of_self_poke = 30)

    # Coordinate spike rand and rest period, remove after actuall data--------------------
    for node in network.nodes:
        if network.nodes[node]["spike"] == 1:
            network.nodes[node]["rest_period"] = network.nodes[node]["refraction_period"]
    #-------------------------------------------------------------------------------------
    #Create all nodes, bio directional = 3600
    for i in range(number_of_electrodes):
        for j in range(number_of_electrodes):
            network.add_edge(i, j, weight=random())

    return network



def fire(network):

    # Check if node has lived to long    FIX THIS CHECK IF ITS ALIVE FIRST MAYBE
    for node_number in network.nodes:
        if network.nodes[node_number]["rest_period"] == node_dies_when_refraction_period: # variable to evolve
            network.nodes[node_number]["spike"] = 0

    # Sum weights pr. node from all shared nodes that are on
    for node_number in range(number_of_electrodes):
        for edge_number in range(number_of_electrodes):
            if (node_number == edge_number or edge_number == node_number): # skip self connection (if not node_number == edge_number): didnt work for some fucking reason
                pass
            elif network.nodes[node_number]["rest_period"] == 0: # only input weights when the node refraction period is over
                network.nodes[node_number]["weighted_sum"] += (network.edges[node_number,edge_number]["weight"] * network.nodes[edge_number]["spike"])

    # Accumulate charge based on sum adjacent weights from nodes that are on
    for node_number in network.nodes:
        network.nodes[node_number]["charge"] += network.nodes[node_number]["weighted_sum"] #

    # Node spike based on conditions
    for node_number in network.nodes:
        if  ( (network.nodes[node_number]["charge"] > threshold) and (network.nodes[node_number]["spike"] == 0) and (network.nodes[node_number]["rest_period"] == 0) ): # WTF happens if its in rest and the other bitches start poking it
            network.nodes[node_number]["spike"] = 1
            network.nodes[node_number]["rest_period"] = refraction_period
            network.nodes[node_number]["charge"] = 0

    # Random self poke % chance.
    if rd.randint(0,100) < chance_of_self_poke:
        network.nodes[node_number]["spike"] = 1
        network.nodes[node_number]["rest_period"] = refraction_period
        network.nodes[node_number]["charge"] = 0

    # Count down rest period for each node pr gen, stop at 0
    for node_number in network.nodes:
        if network.nodes[node_number]["rest_period"] < 1:
            network.nodes[node_number]["rest_period"] = 0
        else: network.nodes[node_number]["rest_period"] -= 1

    return network





# Initialize networks
fittest_network = initialize()
mutated_networks = [None, None, None, None, None]
for n in range(len(mutated_networks)):
    mutated_networks[n] = deepcopy(fittest_network)

# Mutate the networks
for mutated_network in mutated_networks:
    # Evolve threshold
    # Evolve refraction_period
    # Evolve chance_of_self_poke
    for node_number in mutated_network.nodes:
        mutated_network.nodes[node_number]["threshold"] = mutate(mutated_network.nodes[node_number]["threshold"])
        mutated_network.nodes[node_number]["refraction_period"] = mutate(mutated_network.nodes[node_number]["refraction_period"])
        mutated_network.nodes[node_number]["chance_of_self_poke"] = mutate(mutated_network.nodes[node_number]["chance_of_self_poke"])
    # Evolve weights
    for i in range(number_of_electrodes):
        for j in range(number_of_electrodes):
            if i != j:
                mutated_network[i][j]['weight'] = mutate(mutated_network[i][j]['weight'])
    #mutated_networks[n] = mutated_network

# If you uncomment this section, you see that the weights have mutated
"""
print(fittest_network[10][20]['weight'])
print(mutated_networks[0][10][20]['weight'])
print(mutated_networks[1][10][20]['weight'])
print(mutated_networks[2][10][20]['weight'])
print(mutated_networks[3][10][20]['weight'])
print(mutated_networks[4][10][20]['weight'])
"""



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
for gen in range(100):

    next_gen_model_1 = fire(network_model_1)
    network_model_1 = next_gen_model_1

    print("Gen:", gen, "Node 20", network_model_1.nodes[20])
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




    next_gen_model_1 = fire(network_model_1)
    network_model_1 = next_gen_model_1
"""
