import matplotlib
matplotlib.use('TkAgg')
from pylab import *
import networkx as nx
import random as rd

alpha = 1
Dt = 0.01

def initialize():
    global g, nextg, pos
    g = nx.karate_club_graph()
    pos = nx.spring_layout(g)
    for i in g.nodes():
        g.nodes[i]['theta'] = 2 * pi * random()
        g.nodes[i]['omega'] = 1. + uniform(-0.05, 0.05)
    nextg = g.copy()

def update():
    global g, nextg
    for i in g.nodes():
        theta_i = g.nodes[i]['theta']
        nextg.nodes[i]['theta'] = theta_i + (g.nodes[i]['omega'] + alpha * ( \
        sum(sin(g.nodes[j]['theta'] - theta_i) for j in g.neighbors(i)) \
        / g.degree(i))) * Dt
    g, nextg = nextg, g

def observe():
    global g, nextg, pos
    cla()
    nx.draw(g, cmap = cm.hsv, vmin = -1, vmax = 1,
            node_color = [sin(g.nodes[i]['theta']) for i in g.nodes()],
            pos = pos)



import pycxsimulator
pycxsimulator.GUI().start(func=[initialize, observe, update])
