
# Standard libraries
import numpy as np
from numpy import pi
import matplotlib.pyplot as plt
import pandas as pd
import cv2
import os
from os import listdir
import time

# AI libraries
import torch
import torchvision











def get_image_frame():

    # Returns a sample image for now
    image = cv2.imread('datasets/ship_images/560394.jpg', cv2.IMREAD_UNCHANGED)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image



def check_for_obstacle(input_frame):

    # Check for obstacles in image frame
    result = obstacle_detection_model(input_frame)
    df = result.pandas().xyxy[0]

    # Check if the found obstacle is a boat
    if ('boat' in df['name'].unique()):
        found_obstacle = "boat"
    else:
        found_obstacle = None

    return found_obstacle














if __name__ == '__main__':

    # Need this for the model to work for some reason
    # Has something to do with varying input sizes
    torch.backends.cudnn.benchmark = True
    # The pre-trained yolov5 model (yolov5s)
    obstacle_detection_model = torch.hub.load("ultralytics/yolov5", "yolov5x")



    counter = 0
    boats_found = 0
    start_time = time.time()

    # Look for ships in ships dataset
    for images in os.listdir('datasets/ship_images'):
        image_path = 'datasets/ship_images/' + images

        result = check_for_obstacle(image_path)
        if result == 'boat':
            boats_found += 1
        counter += 1

    end_time = time.time()

    print("Scanned for ships")
    print("Found", boats_found, "in", counter, "images")
    print("Scanning took", end_time-start_time)



    counter = 0
    boats_found = 0
    start_time = time.time()

    # Look for ships in fish dataset
    for images in os.listdir('datasets/not_ship_images'):
        image_path = 'datasets/not_ship_images/' + images

        result = check_for_obstacle(image_path)
        if result == 'boat':
            boats_found += 1
        counter += 1

    end_time = time.time()

    print("\nScanned for fish")
    print("Found", boats_found, "in", counter, "images")
    print("Scanning took", end_time-start_time)














































#
