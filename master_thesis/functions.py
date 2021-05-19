import numpy as np



def froude_number(U, L):
    return U / np.sqrt(9.81*L)






print(froude_number(3, 2)) # Values for the Otter at max speed
