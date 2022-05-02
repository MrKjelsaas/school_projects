
# Standard libraries
import numpy as np
from numpy import pi
import matplotlib.pyplot as plt

# AI libraries
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from dq_learning import Agent, DeepQNetwork

# These files were collected from https://github.com/cybergalactic/PythonVehicleSimulator
from functions import plotVehicleStates, plotControls, simulate, gnc
from vehicles import otter

from auto_docking_trainer import simulate




test_agent = Agent(gamma=0.99, epsilon=0, lr=0.001, input_dims=[5], batch_size=64, n_actions=5)
test_agent.Q_eval = T.load("neural_network_models/trained_model.pt")
test_agent.Q_eval.eval()

simulate(starting_position="fixed", visualize=True, print_information=True, movement_method="dq_agent", movement_model=test_agent)
