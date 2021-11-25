


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import pymap3d as pm

import torch
import torchvision





def get_drone_image():
    image = cv2.imread('datasets/gopro_images/GOPR0453.jpg', cv2.IMREAD_UNCHANGED)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image



def rotate_z(T, theta):
    z = np.array([[np.cos(theta), -np.sin(theta), 0, 0],
                   [np.sin(theta), np.cos(theta), 0, 0],
                   [0, 0, 1, 0],
                   [0, 0, 0, 1]])

    return np.dot(T, z)



def get_drone_orientation():
    return -np.pi/2

def get_drone_position():
    return [59.90897578167315, 10.72095760297823]

def get_drone_pitch():
    return -3

def get_drone_altitude():
    return 4

def get_ASV_orientation():
    return 3*np.pi/4

def get_ASV_position():
    return [59.90922258403363, 10.72233674180989]



def get_angle_in_gopro_image(position):
    theta_x = -(position[0] * (92/5184) - 46)
    theta_y = position[1] * (61/3888) - 30.5

    return [theta_x, theta_y]

OceanLab_base_coordinates = [59.90871159701298, 10.719516359283432]
























# Set base pose
T_base = np.eye(4)

# Load data
# Need this for the model to work for some reason
# Has something to do with varying input sizes
torch.backends.cudnn.benchmark = True
# The pre-trained yolov5 model (yolov5s)
model = torch.hub.load("ultralytics/yolov5", "yolov5l")
print("\n\n")





# Determine drone position and orientation
T_drone = np.eye(4)
y, x = get_drone_position()

drone_pose = pm.geodetic2enu(y, x, get_drone_altitude(), OceanLab_base_coordinates[0], OceanLab_base_coordinates[1], 0)

T_drone[0, -1] = drone_pose[0]
T_drone[1, -1] = drone_pose[1]
T_drone[2, -1] = drone_pose[2]
T_drone = rotate_z(T_drone, get_drone_orientation())
#print(np.round(T_drone, 2))





# Capturing an image
img = get_drone_image()

# Perform inference
result = model(img)

# Display results
#result.print()
#result.show()

# Image predictions (tensor)
#print(result.xyxy[0])

# Image predictions (pandas)
#print(result.pandas().xyxy[0])

# Saves the position of the found boats in a list
positions_of_boats_found = []
for index, row in result.pandas().xyxy[0].iterrows():
    if row['name'] == 'boat':
        positions_of_boats_found.append([(row['xmin']+row['xmax'])/2, 3888-row['ymax']])

"""
for position in positions_of_boats_found:
    print(position)
"""

# Calculate angle of the found boats
angles_of_boats_found = []
for n in range(len(positions_of_boats_found)):
    angles_of_boats_found.append(get_angle_in_gopro_image(positions_of_boats_found[n]))

"""
for angle in angles_of_boats_found:
        print(angle)
        print("")
"""

# Calculates translation matrix from drone to boats
T_drone_boats = []
for boat_angle in angles_of_boats_found:
    T = np.eye(4)
    d_l = T_drone[2, -1] * np.tan( (np.pi/2) + np.deg2rad(boat_angle[1]))
    T[1, -1] = d_l
    T[0, -1] = -d_l * np.tan(np.deg2rad(boat_angle[0]))
    T[2, -1] = -T_drone[2, -1]

    T_drone_boats.append(T)

"""
print("T_base_boat:")
for T in T_drone_boats:
    print(np.round(T_drone.dot(T), 2))
    print("")

print("T_drone:")
print(np.round(T_drone, 2))
"""

# Relate position from drone to ASV
T_asv = np.eye(4)
y, x = get_ASV_position()

asv_pose = pm.geodetic2enu(y, x, 0, OceanLab_base_coordinates[0], OceanLab_base_coordinates[1], 0)

T_asv[0, -1] = asv_pose[0]
T_asv[1, -1] = asv_pose[1]
T_asv[2, -1] = asv_pose[2]

T_asv = rotate_z(T_asv, get_ASV_orientation())
#print(np.round(T_asv, 2))

# T_asv_boat = T_asv_base . T_base_drone . T_drone_boat
T_asv_boats = []
for T_drone_boat in T_drone_boats:
    T_asv_boat = np.linalg.inv(T_asv).dot(T_drone).dot(T_drone_boat)
    T_asv_boats.append(T_asv_boat)

"""
for T_asv_boat in T_asv_boats:
    print(T_asv_boat)
    print("")
"""

# Convert cartesian position to euler position (distance and angle)
distances = []
angles = []
for T_asv_boat in T_asv_boats:
    d = np.hypot(T_asv_boat[0, -1], T_asv_boat[1, -1])
    theta = np.arctan2(T_asv_boat[1, -1], T_asv_boat[0, -1]) - np.pi/2

    distances.append(d)
    angles.append(theta)



print("Distances and angles to detected boats from ASV:\n")
for n in range(len(distances)):
    print("Distance:", distances[n])
    print("Angle:", np.rad2deg(angles[n]))
    print("")



















print("--------------------\n")











# Determine drone position and orientation
T_drone = np.eye(4)
y, x = 59.90731335971537, 10.722464754752805

drone_pose = pm.geodetic2enu(y, x, 4, OceanLab_base_coordinates[0], OceanLab_base_coordinates[1], 0)

T_drone[0, -1] = drone_pose[0]
T_drone[1, -1] = drone_pose[1]
T_drone[2, -1] = drone_pose[2]
T_drone = rotate_z(T_drone, -np.pi/2)

# Capturing an image
img = cv2.imread('datasets/gopro_images/GOPR0454.jpg', cv2.IMREAD_UNCHANGED)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Perform inference
result = model(img)

# Display results
#result.print()
#result.show()

# Image predictions (tensor)
#print(result.xyxy[0])

# Image predictions (pandas)
#print(result.pandas().xyxy[0])

# Saves the position of the found boats in a list
positions_of_boats_found = []
for index, row in result.pandas().xyxy[0].iterrows():
    if row['name'] == 'boat':
        positions_of_boats_found.append([(row['xmin']+row['xmax'])/2, 3888-row['ymax']])

# Calculate angle of the found boats
angles_of_boats_found = []
for n in range(len(positions_of_boats_found)):
    angles_of_boats_found.append(get_angle_in_gopro_image(positions_of_boats_found[n]))
    angles_of_boats_found[n][1] += get_drone_pitch()

# Calculates translation matrix from drone to boats
T_drone_boats = []
for boat_angle in angles_of_boats_found:
    T = np.eye(4)
    d_l = T_drone[2, -1] * np.tan( (np.pi/2) + np.deg2rad(boat_angle[1]))
    T[1, -1] = d_l
    T[0, -1] = -d_l * np.tan(np.deg2rad(boat_angle[0]))
    T[2, -1] = -T_drone[2, -1]

    T_drone_boats.append(T)







# Relate position from drone to ASV
T_asv = np.eye(4)
y, x = 59.90745966703175, 10.722088458725288

asv_pose = pm.geodetic2enu(y, x, 0, OceanLab_base_coordinates[0], OceanLab_base_coordinates[1], 0)

T_asv[0, -1] = asv_pose[0]
T_asv[1, -1] = asv_pose[1]
T_asv[2, -1] = asv_pose[2]

T_asv = rotate_z(T_asv, -(3/4)*np.pi)

# T_asv_boat = T_asv_base . T_base_drone . T_drone_boat
T_asv_boats = []
for T_drone_boat in T_drone_boats:
    T_asv_boat = np.linalg.inv(T_asv).dot(T_drone).dot(T_drone_boat)
    T_asv_boats.append(T_asv_boat)

# Convert cartesian position to euler position (distance and angle)
distances = []
angles = []
for T_asv_boat in T_asv_boats:
    d = np.hypot(T_asv_boat[0, -1], T_asv_boat[1, -1])
    theta = np.arctan2(T_asv_boat[1, -1], T_asv_boat[0, -1]) - np.pi/2

    distances.append(d)
    angles.append(theta)



print("Distances and angles to detected boats from ASV:\n")
for n in range(len(distances)):
    print("Distance:", distances[n])
    print("Angle:", np.rad2deg(angles[n]))
    print("")






















print("--------------------\n")








# Determine drone position and orientation
T_drone = np.eye(4)
y, x = 59.90731335971537, 10.722464754752805

drone_pose = pm.geodetic2enu(y, x, 4, OceanLab_base_coordinates[0], OceanLab_base_coordinates[1], 0)

T_drone[0, -1] = drone_pose[0]
T_drone[1, -1] = drone_pose[1]
T_drone[2, -1] = drone_pose[2]
T_drone = rotate_z(T_drone, -(3/4)*np.pi)

# Capturing an image
img = cv2.imread('datasets/gopro_images/GOPR0456.jpg', cv2.IMREAD_UNCHANGED)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Perform inference
result = model(img)

# Display results
#result.print()
#result.show()

# Image predictions (tensor)
#print(result.xyxy[0])

# Image predictions (pandas)
#print(result.pandas().xyxy[0])

# Saves the position of the found boats in a list
positions_of_boats_found = []
for index, row in result.pandas().xyxy[0].iterrows():
    if row['name'] == 'boat':
        positions_of_boats_found.append([(row['xmin']+row['xmax'])/2, 3888-row['ymax']])

# Calculate angle of the found boats
angles_of_boats_found = []
for n in range(len(positions_of_boats_found)):
    angles_of_boats_found.append(get_angle_in_gopro_image(positions_of_boats_found[n]))
    angles_of_boats_found[n][1] += get_drone_pitch()

# Calculates translation matrix from drone to boats
T_drone_boats = []
for boat_angle in angles_of_boats_found:
    T = np.eye(4)
    d_l = T_drone[2, -1] * np.tan( (np.pi/2) + np.deg2rad(boat_angle[1]))
    T[1, -1] = d_l
    T[0, -1] = -d_l * np.tan(np.deg2rad(boat_angle[0]))
    T[2, -1] = -T_drone[2, -1]

    T_drone_boats.append(T)

# Relate position from drone to ASV
T_asv = np.eye(4)
y, x = 59.90745966703175, 10.722088458725288

asv_pose = pm.geodetic2enu(y, x, 0, OceanLab_base_coordinates[0], OceanLab_base_coordinates[1], 0)

T_asv[0, -1] = asv_pose[0]
T_asv[1, -1] = asv_pose[1]
T_asv[2, -1] = asv_pose[2]

T_asv = rotate_z(T_asv, -(3/4)*np.pi)

# T_asv_boat = T_asv_base . T_base_drone . T_drone_boat
T_asv_boats = []
for T_drone_boat in T_drone_boats:
    T_asv_boat = np.linalg.inv(T_asv).dot(T_drone).dot(T_drone_boat)
    T_asv_boats.append(T_asv_boat)

# Convert cartesian position to euler position (distance and angle)
distances = []
angles = []
for T_asv_boat in T_asv_boats:
    d = np.hypot(T_asv_boat[0, -1], T_asv_boat[1, -1])
    theta = np.arctan2(T_asv_boat[1, -1], T_asv_boat[0, -1]) - np.pi/2

    distances.append(d)
    angles.append(theta)



print("Distances and angles to detected boats from ASV:\n")
for n in range(len(distances)):
    print("Distance:", distances[n])
    print("Angle:", np.rad2deg(angles[n]))
    print("")

















































#
