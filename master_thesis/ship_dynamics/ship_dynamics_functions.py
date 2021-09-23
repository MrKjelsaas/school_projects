import numpy as np



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
