import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("TkAgg")
from pylab import *
import random as rd

n = 1000  # number of particles
sd = 0.1  # standard deviation of Gaussian noise
steps = 1000  # number of steps to iterate over
plotsize = 10  # size of plot window


def initialize():
    global xlist, ylist
    xlist = []
    ylist = []
    for i in range(n):
        xlist.append(rd.gauss(0, 1))
        ylist.append(rd.gauss(0, 1))


def observe():
    global xlist, ylist, t

    # plt.ion()
    plt.clf()
    plt.xlim(-plotsize, plotsize)
    plt.ylim(-plotsize, plotsize)
    plt.xlabel("Step: " + str(t))

    plt.plot(xlist, ylist, ".")
    plt.draw()
    plt.pause(0.0001)


def update():
    global xlist, ylist
    for i in range(n):
        xlist[i] += rd.gauss(0, sd)
        ylist[i] += rd.gauss(0, sd)


plt.ion()

t = 0
initialize()
observe()
for t in range(steps):
    update()
    observe()


plt.ioff()
plt.clf()
plt.xlim(-plotsize, plotsize)
plt.ylim(-plotsize, plotsize)
plt.xlabel("Step: " + str(t))

plt.plot(xlist, ylist, ".")
plt.show()
