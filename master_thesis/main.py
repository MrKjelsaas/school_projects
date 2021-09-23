
import numpy as np
import time
import socket

from otter import otter
from ship_dynamics import ship_dynamics_functions
from path_planning import a_star_algorithm
from obstacle_detection import obstacle_detector
from auto_docking import auto_docker

ocean_lab_dock_coordinates = [("N", 59, 54.492, 0), ("E", 10, 43.180, 0)]
tjuvholmen_swimming_pier_coordinates = [("N", 59, 54.359, 0), ("E", 10, 43.101, 0)]
bygdoeynes_dock_coordinates = [("N", 59, 54.275, 0), ("E", 10, 42, 0)]

ocean_lab_dock_decimal_coordinates = ship_dynamics_functions.degrees_minutes_seconds_to_decimal(ocean_lab_dock_coordinates)
tjuvholmen_swimming_pier_decimal_coordinates = ship_dynamics_functions.degrees_minutes_seconds_to_decimal(tjuvholmen_swimming_pier_coordinates)
bygdoeynes_dock_decimal_coordinates = ship_dynamics_functions.degrees_minutes_seconds_to_decimal(bygdoeynes_dock_coordinates)

print("Original coordinates:")
print("Ocean lab:", ocean_lab_dock_coordinates)
print("Tjuvholmen swimming pier:", tjuvholmen_swimming_pier_coordinates)
print("Bygdøynes dock:", bygdoeynes_dock_coordinates)
print("")

print("Converted to decimal:")
print("Ocean lab:", ocean_lab_dock_decimal_coordinates)
print("Tjuvholmen swimming pier:", tjuvholmen_swimming_pier_decimal_coordinates)
print("Bygdøynes dock:", bygdoeynes_dock_decimal_coordinates)
print("")

final_destination = tjuvholmen_swimming_pier_decimal_coordinates














print("Initializing Otter")
the_otter = otter.otter_usv()

print("Connecting to Otter over TCP")
the_otter.establish_connection()

# TODO: Set a radius for waypoints at 5m
# Also, write the method that sets the waypoint radius

print("Finding route to destination...")
route = a_star_algorithm.find_route(ship_dynamics_functions.degrees_minutes_seconds_to_decimal(the_otter.current_position), final_destination)
print("Found a route")
print(route)
print("")

destination_reached = False

while destination_reached == False:

    for next_waypoint in route:

        #Check for obstacles
        found_obstacle = obstacle_detector.check_for_obstacle()

        if found_obstacle == None:
            print("No obstacle detected")
            print("Now heading for:", next_waypoint)
            the_otter.set_station_mode(next_waypoint)
            #Wait for Otter to arrive at waypoint
            #Do something in the meantime
            #Read messages? Check for obstacles?
            print("Waypoint reached\n")

        else:
            print("Found an obstacle")

            print("Recalculating route\n")
            route = a_star_algorithm.find_route(ship_dynamics_functions.degrees_minutes_seconds_to_decimal(the_otter.current_position), final_destination)
            continue

        #Check if this is the final destination
        if next_waypoint == route[-1]:
            destination_reached = True
            print("Final Waypoint reached")
            print("Beginning docking sequence\n")



print("Closing connection to Otter")
the_otter.close_connection()

















"""

print("Original coordinates:")
print(ocean_lab_dock_coordinates)
print(tjuvholmen_swimming_pier_coordinates)
print(bygdoeynes_dock_coordinates)
print("")

ocean_lab_dock_decimal_coordinates = ship_dynamics_functions.degrees_minutes_seconds_to_decimal(ocean_lab_dock_coordinates)
tjuvholmen_swimming_pier_decimal_coordinates = ship_dynamics_functions.degrees_minutes_seconds_to_decimal(tjuvholmen_swimming_pier_coordinates)
bygdoeynes_dock_decimal_coordinates = ship_dynamics_functions.degrees_minutes_seconds_to_decimal(bygdoeynes_dock_coordinates)

print("Converted to decimal:")
print(ocean_lab_dock_decimal_coordinates)
print(tjuvholmen_swimming_pier_decimal_coordinates)
print(bygdoeynes_dock_decimal_coordinates)
print("")

ocean_lab_dock_degrees_coordinates = ship_dynamics_functions.decimal_to_degrees_minutes_seconds(ocean_lab_dock_decimal_coordinates)
tjuvholmen_swimming_pier_degrees_coordinates = ship_dynamics_functions.decimal_to_degrees_minutes_seconds(tjuvholmen_swimming_pier_decimal_coordinates)
bygdoeynes_dock_degrees_coordinates = ship_dynamics_functions.decimal_to_degrees_minutes_seconds(bygdoeynes_dock_decimal_coordinates)

print("Converted back to degrees:")
print(ocean_lab_dock_degrees_coordinates)
print(tjuvholmen_swimming_pier_degrees_coordinates)
print(bygdoeynes_dock_degrees_coordinates)
print("")


print("Finding route from Ocean Lab to Tjuvolmen bathing place...")
route_to_destination = a_star_algorithm.find_route(ocean_lab_dock_decimal_coordinates, tjuvholmen_swimming_pier_decimal_coordinates)
print("Route to destination:")
print(route_to_destination)

"""
