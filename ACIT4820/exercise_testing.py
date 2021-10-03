import numpy as np
from numpy import pi
from scipy.linalg import expm



def skew(W):

    M = np.array([[0, -W[2], W[1]],
                  [W[2], 0, -W[0]],
                  [-W[1], W[0], 0]])

    return M

def bracket(S):

    M = np.zeros([4, 4])
    M[:3, :3] = skew(S[:3])
    M[:3, 3] = S[3:]

    return M

def kinova_forward_kinematics_s(q):
    L1 = 2.755
    L2 = 4.1
    L3 = 2.073
    L4 = 1

    M = np.array([[1, 0, 0, 0],
                 [0, 1, 0, L1+L2+L3+L4],
                 [0, 0, 1, -0.098],
                 [0, 0, 0, 1]])

    S1 = np.array([0, 1, 0, 0, 0, 0])
    S2 = np.array([0, 0, 1, L1, 0, 0])
    S3 = np.array([0, 0, 1, L1+L2, 0, 0])
    S4 = np.array([0, 1, 0, 0, 0, 0])

    S1_bracket = bracket(S1)
    S2_bracket = bracket(S2)
    S3_bracket = bracket(S3)
    S4_bracket = bracket(S4)

    theta_1 = q[0]
    theta_2 = q[1]
    theta_3 = q[2]
    theta_4 = q[3]

    T_sb = np.dot(expm(S1_bracket*theta_1), expm(S2_bracket*theta_2))
    T_sb = np.dot(T_sb, expm(S3_bracket*theta_3))
    T_sb = np.dot(T_sb, expm(S4_bracket*theta_4))
    T_sb = np.dot(T_sb, M)

    return T_sb



L1 = 2.755
L2 = 4.1
L3 = 2.073
L4 = 1

M = np.array([[1, 0, 0, 0],
             [0, 1, 0, L1+L2+L3+L4],
             [0, 0, 1, -0.098],
             [0, 0, 0, 1]])

print("M:")
print(M)
print("")



print("T_sb:")
print(kinova_forward_kinematics_s([2*pi, 2*pi, 2*pi, 2*pi]).round(3))
print("")
