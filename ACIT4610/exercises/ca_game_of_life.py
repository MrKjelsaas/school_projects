import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("TkAgg")
from pylab import *
import random as rd

n = 100  # size of space: n x n
p = 0.1  # probability of initially alive individuals
steps = 100
population = []
plotsize = n


def initialize():
    global config, nextconfig
    config = zeros([n, n])
    for x in range(n):
        for y in range(n):
            config[x, y] = 1 if random() < p else 0
    nextconfig = zeros([n, n])


def observe():
    global config, nextconfig, t

    # plt.ion()
    plt.clf()
    plt.xlim(-plotsize, plotsize)
    plt.ylim(-plotsize, plotsize)
    plt.xlabel("Step: " + str(t))

    plt.plot(config)
    plt.draw()
    plt.pause(0.0001)


def update():
    global config, nextconfig, population
    population.append(0)
    for x in range(n):
        for y in range(n):
            population[-1] += config[x, y]
            # Check for reproduction
            if config[x, y] == 0:  # If dead
                count = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if [dx, dy] != [0, 0]:
                            count += config[(x + dx) % n, (y + dy) % n]

                if count == 3:
                    nextconfig[x, y] = 1
                else:
                    nextconfig[x, y] = 0

            elif config[x, y] == 1:  # If alive
                # Check for loneliness
                count = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if [dx, dy] != [0, 0]:
                            count += config[(x + dx) % n, (y + dy) % n]

                if count < 2:
                    nextconfig[x, y] = 0
                # Check for overcrowding
                elif count > 3:
                    nextconfig[x, y] = 0
                # Check for happiness
                else:
                    nextconfig[x, y] = 1

    config, nextconfig = nextconfig, config


t = 0
initialize()
observe()
for t in range(steps):
    update()
    observe()
