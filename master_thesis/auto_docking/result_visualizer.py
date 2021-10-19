
# Standard libraries
import numpy as np
from numpy import pi
import matplotlib.pyplot as plt

# AI libraries
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

# These files were collected from https://github.com/cybergalactic/PythonVehicleSimulator
from functions import plotVehicleStates, plotControls, simulate, gnc
from vehicles import otter

from auto_docking_trainer import simulate, Agent, DeepQNetwork



test_agent = Agent(gamma=0.99, epsilon=0, lr=0.001, input_dims=[10], batch_size=32, n_actions=5)
test_agent.Q_eval = T.load("neural_network_models/final_trained_model_AI.pt")
test_agent.Q_eval.eval()

simulate(starting_position="fixed", sample_time=0.1, number_of_steps=601, visualize=True, print_information=True, movement_method="dq_agent", movement_model=test_agent)
