import numpy as np
from numpy import pi
from scipy.linalg import expm
import modern_robotics as mr





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

def mycobot_forward_kinematics_s(q):

    M = np.array([[1, 0, 0, 0.10999],
                 [0, 1, 0, 0],
                 [0, 0, 1, 0.35],
                 [0, 0, 0, 1]])

    S1 = np.array([0, 0, 1, 0, 0, 0])
    S2 = np.array([1, 0, 0, 0, 0.07042, 0])
    S3 = np.array([-1, 0, 0, 0, -0.18082, 0])
    S4 = np.array([1, 0, 0, 0, 0.27682, 0])
    S5 = np.array([0, 0, 1, 0, -0.06639, 0])
    S6 = np.array([1, 0, 0, 0, 0.35, 0])

    S1_bracket = bracket(S1)
    S2_bracket = bracket(S2)
    S3_bracket = bracket(S3)
    S4_bracket = bracket(S4)
    S5_bracket = bracket(S5)
    S6_bracket = bracket(S6)

    theta_1 = q[0]
    theta_2 = q[1]
    theta_3 = q[2]
    theta_4 = q[3]
    theta_5 = q[4]
    theta_6 = q[5]

    T_sb = np.dot(expm(S1_bracket*theta_1), expm(S2_bracket*theta_2))
    T_sb = np.dot(T_sb, expm(S3_bracket*theta_3))
    T_sb = np.dot(T_sb, expm(S4_bracket*theta_4))
    T_sb = np.dot(T_sb, expm(S5_bracket*theta_5))
    T_sb = np.dot(T_sb, expm(S6_bracket*theta_6))
    T_sb = np.dot(T_sb, M)

    return T_sb

def mycobot_forward_kinematics_b(q):

    M = np.array([[1, 0, 0, 0.10999],
                 [0, 1, 0, 0],
                 [0, 0, 1, 0.35],
                 [0, 0, 0, 1]])

    B1 = np.array([0, 0, 1, 0, 0.10999, 0])
    B2 = np.array([1, 0, 0, 0, -0.27958, 0])
    B3 = np.array([-1, 0, 0, 0, 0.16918, 0])
    B4 = np.array([1, 0, 0, 0, -0.07318, 0])
    B5 = np.array([0, 0, 1, 0, 0.0436, 0])
    B6 = np.array([1, 0, 0, 0, 0, 0])

    B1_bracket = bracket(B1)
    B2_bracket = bracket(B2)
    B3_bracket = bracket(B3)
    B4_bracket = bracket(B4)
    B5_bracket = bracket(B5)
    B6_bracket = bracket(B6)

    theta_1 = q[0]
    theta_2 = q[1]
    theta_3 = q[2]
    theta_4 = q[3]
    theta_5 = q[4]
    theta_6 = q[5]

    T_bs = np.dot(M, expm(B1_bracket*theta_1))
    T_bs = np.dot(T_bs, expm(B2_bracket*theta_2))
    T_bs = np.dot(T_bs, expm(B3_bracket*theta_3))
    T_bs = np.dot(T_bs, expm(B4_bracket*theta_4))
    T_bs = np.dot(T_bs, expm(B5_bracket*theta_5))
    T_bs = np.dot(T_bs, expm(B6_bracket*theta_6))

    return T_bs

def get_jacobian_from_s(joint_configurations):
    S = np.array([[0, 0, 1, 0, 0, 0],
                  [1, 0, 0, 0, 0.07042, 0],
                  [-1, 0, 0, 0, -0.18082, 0],
                  [1, 0, 0, 0, 0.27682, 0],
                  [0, 0, 1, 0, -0.06639, 0],
                  [1, 0, 0, 0, 0.35, 0]])
    S = S.T

    return mr.JacobianSpace(S, joint_configurations)



def get_jacobian_from_b(joint_configurations):
    B = np.array([[0, 0, 1, 0, 0.10999, 0],
                  [1, 0, 0, 0, -0.27958, 0],
                  [-1, 0, 0, 0, 0.16918, 0],
                  [1, 0, 0, 0, -0.07318, 0],
                  [0, 0, 1, 0, 0.0436, 0],
                  [1, 0, 0, 0, 0, 0]])
    B = B.T

    return mr.JacobianBody(B, joint_configurations)






def compute_torque(thetas):
    F_s = [0, 0, 0, 0, 0, 1.4715]
    return get_jacobian_from_s(thetas).T.dot(F_s)































"""
J_s = np.array([[0, 1, 0, 1, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [1, 0, 1, 0, 1, 0, 1],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0.34, 0, 0.74, 0, 1.14, 0],
                [0, 0, 0, 0, 0, 0, 0]])

thetas = np.ones([7])
for i in range(7):
    thetas[i] *= (i+1)*(np.pi/16)

J_st = mr.JacobianSpace(J_s, thetas)
#print(np.round(J_st, 2))

F_s = np.array([1, 1, 1, 1, 1, 1])

torque = np.dot(J_st.T, F_s)

#print(torque)

J_sw = J_st[:3, :]

A = J_sw.dot(J_sw.T)

eigenvalues = np.linalg.eig(A)[0]

my_2 = np.max(eigenvalues) / np.min(eigenvalues)

#print(my_2)

J_sv = J_st[3:, :]
A = J_sv.dot(J_sv.T)
eigenvalues = np.linalg.eig(A)[0]

my_2 = np.max(eigenvalues) / np.min(eigenvalues)

#print(my_2)

J_b = np.array([[0, 1, 0, 1, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [1, 0, 1, 0, 1, 0, 1],
                [0, 0, 0, 0, 0, 0, 0],
                [0, -0.95, 0, -0.55, 0, -0.15, 0],
                [0, 0, 0, 0, 0, 0, 0]])

J_bt = mr.JacobianBody(J_b, thetas)
#print(np.round(J_bt, 2))

torque = np.dot(J_bt.T, F_s)

#print(torque)

J_bw = J_bt[:3, :]
J_bv = J_bt[3:, :]

A = J_bw.dot(J_bw.T)
eigenvalues = np.linalg.eig(A)[0]
mu_2 = np.max(eigenvalues) / np.min(eigenvalues)

#print(mu_2)

A = J_bv.dot(J_bv.T)
eigenvalues = np.linalg.eig(A)[0]
mu_2 = np.max(eigenvalues) / np.min(eigenvalues)

#print(mu_2)






print("T_sb:")
print(mycobot_forward_kinematics_s([0, 0, 0, np.pi/2, 0, 0]).round(3))
print("")

print("T_bs:")
print(mycobot_forward_kinematics_b([0, 0, 0, np.pi/2, 0, 0]).round(3))
print("")

print(np.round(get_jacobian_from_s([0, 0, 0, 0, 0, 0]), 2))
print("")
print(np.round(get_jacobian_from_b([0, 0, 0, 0, 0, 0]), 2))


torque_needed = compute_torque([0, 0, 0, 0, 0, 0])
print(np.round(torque_needed, 2))













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

"""
