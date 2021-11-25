import numpy as np
import pymap3d as pm



def degrees_minutes_seconds_to_decimal(cardinal_direction, degrees=0, minutes=0, seconds=0):

    if isinstance(cardinal_direction, list):
        return (degrees_minutes_seconds_to_decimal(cardinal_direction[0]), degrees_minutes_seconds_to_decimal(cardinal_direction[1]))

    if isinstance(cardinal_direction, tuple):
        return degrees_minutes_seconds_to_decimal(cardinal_direction[0], cardinal_direction[1], cardinal_direction[2], cardinal_direction[3])

    if cardinal_direction not in ["N", "S", "E", "W"]:
        print("Invalid cardinal direction")
        print("Valid inputs are N, S, E, W")
        exit()

    decimal_coordinate = float(degrees) + float(minutes)/60 + float(seconds)/3600

    if cardinal_direction == "S" or cardinal_direction == "W":
        decimal_coordinate *= -1

    return decimal_coordinate



def decimal_to_degrees_minutes_seconds(decimal, return_seconds = False):

    degrees_minutes_seconds = []

    if decimal[0] < 0:
        cardinal_direction = "S"
    else:
        cardinal_direction = "N"

    degrees = int(decimal[0])

    minutes = (decimal[0] - int(decimal[0])) * 60
    minutes = np.round(minutes, 3)

    seconds = 0

    if return_seconds == True:
        seconds = (minutes - int(minutes)) * 60
        seconds = np.round(seconds, 3)
        minutes = int(minutes)

    degrees_minutes_seconds.append((cardinal_direction, degrees, minutes, seconds))



    if decimal[1] < 0:
        cardinal_direction = "W"
    else:
        cardinal_direction = "E"

    degrees = int(decimal[1])

    minutes = (decimal[1] - int(decimal[1])) * 60
    minutes = np.round(minutes, 3)

    seconds = 0

    if return_seconds == True:
        seconds = (minutes - int(minutes)) * 60
        seconds = np.round(seconds, 3)
        minutes = int(minutes)

    degrees_minutes_seconds.append((cardinal_direction, degrees, minutes, seconds))



    return degrees_minutes_seconds



def knots_to_meters_per_second(knots):
    return knots*1.852/3.6



def meters_per_second_to_knots(meters_per_second):
    return meters_per_second*3.6/1.852


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



# Returns distance in meters between two decimal coordinates
def map_distance(start, end):
    lat_distance = distance_at_latitude(end[0]-start[0], np.average([start[0], end[0]]))
    lon_distance = distance_at_longitude(end[1]-start[1], np.average([start[1], end[1]]))
    distance = np.hypot(lat_distance, lon_distance)
    return distance
