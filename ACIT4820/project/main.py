


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2

import torch
import torchvision



# Taken from https://en.wikipedia.org/wiki/Geographic_coordinate_system
# Standard value is for OsloMet Oceanlab
def distance_at_longitude(degrees, phi = 10.719278575838432):
    phi = np.deg2rad(phi)
    return degrees * (11412.84*np.cos(phi) - 93.5*np.cos(3*phi) + 0.118*np.cos(5*phi))



# Taken from https://en.wikipedia.org/wiki/Geographic_coordinate_system
# Standard value is for OsloMet Oceanlab
def distance_at_latitude(degrees, phi = 59.90865634998943):
    phi = np.deg2rad(phi)
    return degrees * (111132.92 - 559.82*np.cos(2*phi) + 1.175*np.cos(4*phi) - 0.0023*np.cos(6*phi))













"""
# Create webcam cv2 object
webcam = cv2.Videowebcamture(0)
while webcam.isOpened():
    # Grab a frame from the webcam
    ret, frame = webcam.read()

    # Make detections
    result = model(frame)

    # Display the result on the screen (with boxes)
    cv2.imshow('YOLO', np.squeeze(result.render()))

    # Exits the loop on 'q' key press
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# Cleanup
webcam.release()
cv2.destroyAllWindows()
"""









# Preparation:
# Collect data

# Set ASV/base/drone positions and orientations
"""
T_base = np.eye(4)
T_asv =
T_drone =
"""





# Setup:
# Load data

# Need this for the model to work for some reason
# Has something to do with varying input sizes
torch.backends.cudnn.benchmark = True
# The pre-trained yolov5 model (yolov5s)
model = torch.hub.load("ultralytics/yolov5", "yolov5l")

# Loading an image
img = 'datasets/ship_images/563043.jpg'





# Perform inference

# Inference (detecting objects)
result = model(img)


print("\n")

# Results
result.print()
result.show()

print("\n")

print(result.xyxy[0])  # Image predictions (tensor)
print("\n")
print(result.pandas().xyxy[0])  # Image predictions (pandas)




# Calculate position



# Convert position from drone to ASV



# Convert cartesian position to euler position (distance and angle)
"""
d = np.hypot(x, y)
theta = np.arctan2(y, x)
"""






















































#
