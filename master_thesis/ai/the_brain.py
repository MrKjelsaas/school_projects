import numpy as np
import networkx as nx
import matplotlib.pyplot as plt













# 1. Initiate an "empty" neural network

# 2. Use deep reinforcement learning to train the neural network

# 3. Use NEAT + EA hybrid to evolve the neural network
# - Can this be done by making 5 copies(mutations) and then NEAT-mutating?

# 4. Evaluate "mutations" with some metric (how they score on a test scenario for example)
# 5. Take the x(1?) best one(s) and keep reinforcement learning them

# Repeat steps 2-5






































"""
synthetic_nervous_system = nx.DiGraph()

synthetic_nervous_system.add_nodes_from(['A', 'B', 'C', 'D'], value = 0)

print("Current nodes:")
print(synthetic_nervous_system.nodes)

synthetic_nervous_system.add_edges_from([('A', 'C'), ('A', 'D'), ('B', 'C'), ('B', 'D')], weight=1)

print("Current edges:")
print(synthetic_nervous_system.edges)

print("Weight between A and C:")
print(synthetic_nervous_system.edges['A', 'C']['weight'])




#Fire A
print("\nTesting firing")
next_values = np.zeros([len(synthetic_nervous_system['A'])])
#print(len(synthetic_nervous_system['A'])) Number of neighbors

for neighbor_node in synthetic_nervous_system['A']:
    print("A", neighbor_node)
    synthetic_nervous_system.nodes[neighbor_node]['value'] = synthetic_nervous_system.edges['A', neighbor_node]['weight']

print("\nNetwork node values:")
for node in synthetic_nervous_system.nodes:
    print("Node:", node)
    print(synthetic_nervous_system.nodes[node]['value'])
    print("")




exit()



pos = nx.spring_layout(synthetic_nervous_system)
nx.draw(synthetic_nervous_system, pos, with_labels=True)
labels = {e: synthetic_nervous_system.edges[e]['weight'] for e in synthetic_nervous_system.edges}
nx.draw_networkx_edge_labels(synthetic_nervous_system, pos, edge_labels=labels)
plt.show()

synthetic_nervous_system.edges['A', 'C']['weight'] = 0.9
print("Weight between A and C:")
print(synthetic_nervous_system.edges['A', 'C']['weight'])

pos = nx.spring_layout(synthetic_nervous_system)
nx.draw(synthetic_nervous_system, pos, with_labels=True)
labels = {e: synthetic_nervous_system.edges[e]['weight'] for e in synthetic_nervous_system.edges}
nx.draw_networkx_edge_labels(synthetic_nervous_system, pos, edge_labels=labels)
plt.show()
"""
