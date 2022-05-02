
import time
import socket
import select
import numpy as np
from numpy import round, pi
import cv2
import os
import pymap3d as pm
from copy import copy, deepcopy

import torch
import torchvision

from path_planning.a_star_algorithm import a_star




def checksum(message):
    checksum = 0
    for character in message:
        checksum ^= ord(character)
    checksum = hex(checksum)
    checksum = checksum[2:]
    if len(checksum) == 1:
        checksum = "0" + checksum
    return checksum



def coords_to_xy(coordinates):
    lat = coordinates[0]
    lon = coordinates[1]

    SW_lat = 59 + (54/60)
    SW_lon = 10 + (41/60)

    e, n, u = pm.geodetic2enu(lat, lon, 0, SW_lat, SW_lon, 0)

    return[int(round(e)), int(round(n))]



def xy_to_coords(xy):
    x = xy[0]
    y = xy[1]

    SW_lat = 59 + (54/60)
    SW_lon = 10 + (41/60)

    lat, lon, alt = pm.enu2geodetic(x, y, 0, SW_lat, SW_lon, 0)

    return [lat, lon]



# Used to find the difference between two angles
def smallest_signed_angle_between(x, y):
    a = (x - y) % (2*pi)
    b = (y - x) % (2*pi)
    return -a if a < b else b

















class otter_usv():
    def __init__(self):

        # Socket for TCP communication
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Constants
        self.home_coordinates = [59.908513, 10.719452]
        self.top_speed = 3.0 #m/s
        self.waypoint_acceptance_radius = 2.0

        # Variables
        self.current_position = [0.0, 0.0]
        self.previous_position = [0.0, 0.0]
        self.last_speed_update = time.time()
        self.current_course_over_ground = 0
        self.current_speed = 0
        self.current_fuel_capacity = 0
        self.current_orientation = [0, 0, 0] # roll, pitch, yaw
        self.yaw = smallest_signed_angle_between(0, np.deg2rad(-self.current_orientation[2]))
        self.current_rotational_velocities = [0, 0, 0] # roll, pitch, yaw

        # AI
        self.destination_dock_coordinates = [59.90895368229298, 10.722063882911693]
        self.destination_dock_entrance = [59.90899726728072, 10.721982441177916]
        e, n, u = pm.geodetic2enu(self.destination_dock_coordinates[0], self.destination_dock_coordinates[1], 0, \
                                  xy_to_coords(self.destination_dock_entrance)[0], xy_to_coords(self.destination_dock_entrance)[1], 0)
        self.destination_dock_angle = np.arctan2(n, e) - pi/2
        torch.backends.cudnn.benchmark = True # Need this for the model to work for some reason
                                              # Has something to do with varying input sizes
        self.obstacle_detection_model = torch.hub.load("ultralytics/yolov5", "yolov5x")

        self.waypoints = []
        self.waypoint_angles = []
        self.destination = [0, 0]
        self.destination_angle = 0

        self.distance_between_vehicle_and_destination = 0
        self.angular_difference_between_vehicle_and_destination = 0
        self.direction_to_destination = 0



        # Used to check whether the Otter SHOULD be connected
        self.connection_status = False

        # Stores the last message received from the Otter
        self.last_message_received = ""

        # Used to print messages for debugging/testing
        self.verbose = True



    # Initialises a TCP connection
    def establish_connection(self, destination_ip = "192.168.53.2", destination_port = 2009):
        #destination_ip = 'localhost'
        try:
            self.sock.connect((destination_ip, destination_port))
            self.connection_status = True
            self.camera = cv2.VideoCapture("rtsp://admin:pwd4hik!@192.168.53.5/Streaming/Channels/101")
            if not self.camera.isOpened():
                print("Error connecting to Otter camera")
                return False
            return True
        except:
            print("Could not connect to Otter")
            return False



    # Closes the TCP connection
    def close_connection(self):
        try:
            self.sock.close()
            self.connection_status = False
            self.camera.release()
            cv2.destroyAllWindows()
            return True
        except:
            print("Error when disconnecting from Otter")
            return False



    # Checks whether the Otter SHOULD be connected (not if it really is)
    def should_be_connected(self):
        return self.connection_status



    # Reads an image from the camera
    def get_camera_frame(self):
        if self.verbose:
            print("Grabbing image frame from Otter camera")
        ret, frame = self.camera.read()
        if ret == False:
            if self.verbose:
                print("Couldn't grab image frame from Otter camera")
            return ret
        else:
            return frame



    def read_message(self, timeout = 10):
        if self.verbose:
            print("Listening to message from Otter")
        self.sock.setblocking(0)
        ready = select.select([self.sock], [], [], timeout)
        if ready[0]:
            received_message = self.sock.recv(1024).decode()
            self.last_message_received = received_message
            return received_message

        else:
            return None



    # Listens to message from the Otter and updates:
    # position, speed, course over ground, orientation, rotational velocity, fuel capacity
    def update_values(self):
        msg = self.read_message()
        if msg is None:
            print("No message received from Otter")
            print("Check communication")
            return
        list = msg.split()

        # We skip the last one because it is usually incomplete
        list = list[:-1]

        # Get the newest messages
        gps_message = ""
        imu_message = ""
        mod_message = ""
        for message in list:
            if message[:8] == "$PMARGPS":
                gps_message = message
            elif message[:8] == "$PMARIMU":
                imu_message = message
            elif message[:8] == "$PMARMOD":
                mod_message = message

        # Check for checksum error
        if checksum(gps_message[1:-3]) != gps_message[-2:].lower():
            print("Checksum error in $PMARGPS message")
            return

        gps_message = gps_message.split("*")[0] # Removing checksum
        gps_message = gps_message.split(",")

        # Update position
        lat_msg = gps_message[2]
        lon_msg = gps_message[4]
        lat_deg = lat_msg[:2]
        lon_deg = lon_msg[:3]
        lat_min = lat_msg[2:]
        lon_min = lon_msg[3:]

        lat = float(lat_deg) + ( (float(lat_min)/100) / 0.6)
        lon = float(lon_deg) + ( (float(lon_min)/100) / 0.6)

        if gps_message[3] == "S":
            lat *= -1
        if gps_message[5] == "W":
            lon *= -1

        self.current_position = [lat, lon]



        # Update speed
        e, n, u = pm.geodetic2enu(self.current_position[0], self.current_position[1], 0, \
        self.previous_position[0], self.previous_position[1], 0)
        s = np.hypot(e, n)
        v = s / (time.time() - self.last_speed_update)
        #self.current_speed = float(gps_message[7])
        self.current_speed = v
        self.last_speed_update = time.time()
        self.previous_position = copy(self.current_position)


        # Update course over ground
        if gps_message[8] != "":
            self.current_course_over_ground = float(gps_message[8])
        else:
            print("Unable to read course over ground from Otter")

        # Check for checksum error
        if checksum(imu_message[1:-3]) != imu_message[-2:].lower():
            print("Checksum error in $PMARIMU message")
            return

        # Update orientation
        imu_message = imu_message.split("*")[0] # Removing checksum
        imu_message = imu_message.split(",")

        if imu_message[1] != "":
            self.current_orientation[0] = float(imu_message[1])
        if imu_message[2] != "":
            self.current_orientation[1] = float(imu_message[2])
        if imu_message[3] != "":
            self.current_orientation[2] = float(imu_message[3])
            self.yaw = smallest_signed_angle_between(0, np.deg2rad(-self.current_orientation[2]))

        # Update rotational velocities
        if imu_message[4] != "":
            self.current_rotational_velocities[0] = float(imu_message[4])
        if imu_message[5] != "":
            self.current_rotational_velocities[1] = float(imu_message[5])
        if imu_message[6] != "":
            self.current_rotational_velocities[2] = float(imu_message[6])

        # Check for checksum error
        if checksum(mod_message[1:-3]) != mod_message[-2:].lower():
            print("Checksum error in $PMARMOD message")
            return

        # Update fuel capacity
        mod_message = mod_message.split("*")[0] # Removing checksum
        mod_message = mod_message.split(",")

        self.current_fuel_capacity = mod_message[2]

        return



    # Sends a message to the Otter
    def send_message(self, message):
        if self.verbose:
            print("Sending message:", message)
        try:
            self.sock.sendall(message.encode())
            return True
        except:
            print("Couldn't send message to Otter")
            return False



    # Sends the drift command to the Otter
    # This basically means that both thrusters are at rest
    def drift(self):
        if self.verbose:
            print("Otter entering drift mode")
        message_to_send = "$PMARABT\r\n"
        return self.send_message(message_to_send)



    # Sends the autopilot command to the Otter
    # TODO
    def set_autopilot_mode(self, cross_track_error_magnitude, direction_to_steer, cross_track_units, bearing_from_origin_to_destination):
        return False



    # Send manual control mode command to Otter
    def set_manual_control_mode(self, force_x, force_y, torque_z):
        if self.verbose:
            print("Otter entering manual control mode with X force:", force_x, "Y force:", force_y, "Z torque:", torque_z)
        force_x = str(np.round(force_x, 2))
        force_y = str(np.round(force_y, 2))
        torque_z = str(np.round(torque_z, 2))

        message_to_send = "$PMARMAN," + force_x + "," + force_y + "," + torque_z + '*'
        message_to_send += checksum(message_to_send[1:-1])
        message_to_send += "\r\n"

        return self.send_message(message_to_send)

    # An attempt to set the thruster forces manually
    def set_thrusters(self, a, b):

        if self.verbose:
            print("Setting Otter thrusters to", a, b)

        # Calculate linear force
        CG = np.array([0.2, 0, -0.2])
        l_y = 0.395
        l_x = 2.0/2 + CG[0]
        alpha_a = pi/2 - np.arctan2(l_x, l_y)
        alpha_b = pi/2 - np.arctan2(l_x, -l_y)
        c_x = 1/(np.cos(alpha_a)+np.cos(alpha_b))

        F_x = c_x * (a * np.cos(alpha_a) + b * np.cos(alpha_b))

        # Calculate rotational force
        beta_a = pi/2 - alpha_a
        beta_b = pi/2 - alpha_b
        c_t = 1/(np.cos(beta_a)-np.cos(beta_b))

        F_z = c_t * (a * np.cos(beta_a) + b * (np.cos(beta_b)))

        return self.set_manual_control_mode(F_x, 0, F_z)



    # Sets the Otter to drive in a certain direction at a certain speed
    def set_course_mode(self, angle):
        if self.verbose:
            print("Otter entering course mode with angle:", angle, "speed:", speed)
        message_to_send = "$PMARCRS," + str(angle) + "," + str(np.round(speed, 2)) + "*"
        message_to_send += checksum(message_to_send[1:-1])
        message_to_send += "\r\n"

        return self.send_message(message_to_send)



    def set_leg_mode(self, origin_coordinates, destination_coordinates, speed):
        if self.verbose:
            print("Otter entering leg mode with origin:", origin_coordinates, "destination:", destination_coordinates, "speed:", speed)

        lat0 = origin_coordinates[0][1]
        lat0 *= 100
        lat0 += origin_coordinates[0][2]
        if origin_coordinates[0][0] == "S":
            lat0 *= -1
        lat0 = np.round(lat0, 3)

        lon0 = origin_coordinates[1][1]
        lon0 *= 100
        lon0 += origin_coordinates[1][2]
        if origin_coordinates[1][0] == "W":
            lon0 *= -1
        lon0 = np.round(lon0, 3)

        lat1 = destination_coordinates[0][1]
        lat1 *= 100
        lat1 += destination_coordinates[0][2]
        if destination_coordinates[0][0] == "S":
            lat1 *= -1
        lat1 = np.round(lat1, 3)

        lon1 = destination_coordinates[1][1]
        lon1 *= 100
        lon1 += destination_coordinates[1][2]
        if destination_coordinates[1][0] == "W":
            lon1 *= -1
        np.round(lon1, 3)

        message_to_send = "$PMARLEG," + str(lat0)
        message_to_send += ","
        message_to_send += str(lon0)
        message_to_send += ","
        message_to_send += str(lat1)
        message_to_send += ","
        message_to_send += str(lon1)
        message_to_send += ","
        message_to_send += str(np.round(speed, 2)) + "*"

        message_to_send += checksum(message_to_send[1:-1])
        message_to_send += "\r\n"

        return self.send_message(message_to_send)



    def set_station_mode(self, destination_coordinates, speed):
        if self.verbose:
            print("Otter entering station mode with destination:", destination_coordinates, "speed:", speed)

        latitude = destination_coordinates[0][1]
        latitude *= 100
        latitude += destination_coordinates[0][2]
        if destination_coordinates[0][0] == "S":
            latitude *= -1
        latitude = np.round(latitude, 3)

        longitude = destination_coordinates[1][1]
        longitude *= 100
        longitude += destination_coordinates[1][2]
        if destination_coordinates[1][0] == "W":
            longitude *= -1
        np.round(longitude, 3)


        message_to_send = "$PMARSTA," + str(latitude)
        message_to_send += ","
        message_to_send += str(longitude)
        message_to_send += ","
        message_to_send += str(np.round(speed, 2)) + "*"

        message_to_send += checksum(message_to_send[1:-1])
        message_to_send += "\r\n"

        return self.send_message(message_to_send)



    def set_parameters(lookahead_distance, radius_in, radius_out):
        return False



    def EMERGENCY_BRAKES(self):
        print("APPLYING EMERGENCY BRAKES")

        self.set_thrusters(-1, -1)

        while self.current_speed > 0:
            self.update_values()

        print("Otter stopped")
        print("Entering drift mode")

        self.drift()
















    def get_path_following_state(self):
        # Gathers observations
        self.xy_pos = coords_to_xy(self.current_position)
        self.distance_between_vehicle_and_destination = np.hypot(self.xy_pos[0]-self.destination[0], self.xy_pos[1]-self.destination[1])
        self.angular_difference_between_vehicle_and_destination = smallest_signed_angle_between(self.yaw, self.destination_angle)
        self.direction_to_destination = smallest_signed_angle_between(0, np.arctan2(self.destination[1]-self.xy_pos[1], self.destination[0]-self.xy_pos[0]) - pi/2 - self.yaw)

        state = np.array([self.current_speed, # Surge
                          self.distance_between_vehicle_and_destination, # Distance to next waypoint
                          self.angular_difference_between_vehicle_and_destination, # Angular difference between destination and vehicle (how parallel they are)
                          self.direction_to_destination, # Which direction the destination is in
                          ])

        state[0] /= 3
        state[1] /= 1
        state[2] /= pi
        state[3] /= pi

        return state



    def get_auto_docking_state(self):
        # Gathers observations

        e, n, u = pm.geodetic2enu(self.destination_dock_coordinates[0], self.destination_dock_coordinates[1], 0, \
                                  self.current_position[0], self.current_position[1], 0)
        self.distance_to_dock = np.hypot(e, n)
        self.angular_difference_between_vehicle_and_dock = smallest_signed_angle_between(self.yaw, self.destination_dock_angle)
        self.xy_pos = coords_to_xy(self.current_position)
        self.direction_to_destination = smallest_signed_angle_between(0, np.arctan2(self.destination[1]-self.xy_pos[1], self.destination[0]-self.xy_pos[0]) - pi/2 - self.yaw)

        state = np.array([self.current_speed, # Surge
                          self.current_rotational_velocities[2], # Yaw rate
                          self.distance_to_dock, # Distance to dock
                          self.angular_difference_between_vehicle_and_dock, # Angular difference between dock and vehicle (how parallel they are)
                          self.direction_to_destination, # Which direction the destination is in
                          ])

        state[0] /= 3
        state[1] /= 0.326
        state[2] /= 6.4
        state[3] /= pi
        state[4] /= pi

        return state



    def plan_route(self):
        x = int(np.round(coords_to_xy(self.current_position)[0]))
        y = int(np.round(coords_to_xy(self.current_position)[1]))

        # Can't calculate route if out of bounds
        if not 0 < x < self.planning_map.shape[0] or not 0 < y < self.planning_map.shape[1]:
            return

        # Won't bother calculating if we're standing on land since it's not gonna work anyway
        if not self.planning_map[x, y]:

            # Check if we are inside dock
            e, n, u = pm.geodetic2enu(self.destination_dock_coordinates[0], self.destination_dock_coordinates[1], 0, \
                                      self.current_position[0], self.current_position[1], 0)
            self.distance_to_dock = np.hypot(e, n)
            if self.distance_to_dock < 6.4: # Approximate distance from entrance to center of dock
                # Plan route to dock centre
                next_waypoints = np.asarray(a_star(self.planning_map, (x, y), tuple(coords_to_xy(self.destination_dock_coordinates))))
                if next_waypoints.size >= 2:
                    self.waypoints = next_waypoints

            else:
                # Plan route to dock entrance
                next_waypoints = np.asarray(a_star(self.planning_map, (x, y), tuple(coords_to_xy(self.destination_dock_entrance))))
                if next_waypoints.size >= 2:
                    self.waypoints = next_waypoints

        # Remove first waypoints that are closer than waypoint acceptance radius
        while True:
            if self.waypoints.size == 2:
                break
            d = np.hypot(x-self.waypoints[0, 0], y-self.waypoints[0, 1])
            if d < self.waypoint_acceptance_radius:
                    self.waypoints = self.waypoints[1:, :]
            else:
                break

        # Update waypoint angles and set destination
        self.set_waypoint_angles()
        self.set_next_destination()



    # Sets the current destination to the next waypoint
    def set_next_destination(self):
        #self.waypoints = self.waypoints[1:, :]
        self.destination = self.waypoints[0]
        #self.waypoint_angles = self.waypoint_angles[1:]
        self.destination_angle = self.waypoint_angles[0]



    # Calculates the angle from waypoints
    def set_waypoint_angles(self):
        self.waypoint_angles = []
        for n in range(len(self.waypoints)-1):
            x = self.waypoints[n+1][0] - self.waypoints[n][0]
            y = self.waypoints[n+1][1] - self.waypoints[n][1]
            angle = np.arctan2(y, x) - pi/2

            self.waypoint_angles.append(angle)

        self.waypoint_angles.append(self.destination_dock_angle)



    def check_for_obstacle(self):

        # Retrieve image frame
        img = self.get_camera_frame()

        # Check if we have a valid image
        if not isinstance(img, np.ndarray):
            return False

        # Scan for objects
        result = self.obstacle_detection_model(img)
        df = result.pandas().xyxy[0]

        # Check if the found object is a boat
        if ('boat' in df['name'].unique()):
            if self.verbose:
                print("Found a boat")

            # TODO:
            # Calculate position of obstacle

            # Update binary map with position of obstacle

            # Implement a timeout for removing obstacles from map?

            # Plan a new route
            self.plan_route()

            return True

        else:
            return False





    def generate_binary_map(self):
        # "Baseline" map, used for collision checking
        self.binary_map = np.loadtxt('path_planning/binary_map.csv')

        # Used for path planning
        # An added "safety margin" of ca two meters is added to each obstacle
        self.planning_map = np.loadtxt('path_planning/planning_map.csv')

        # Used for rendering
        self.render_map = copy(self.binary_map)















if __name__ == "__main__":

    otter = otter_usv()
    if not otter.establish_connection():
        exit()
    print("Otter connected")

    """
    time.sleep(3)

    otter.set_manual_control_mode(0.1, 0.1, 0)
    time.sleep(5)

    otter.set_manual_control_mode(-0.1, -0.1, 0)
    time.sleep(5)

    otter.drift()
    time.sleep(3)
    """

    """
    ret, frame = otter.get_camera_frame()

    cv2.imshow("OtterView", frame)

    cv2.waitKey(0)
    """

    """
    otter.update_values()
    """

    """
    time.sleep(1)
    print(otter.read_message())
    time.sleep(1)
    """



    otter.close_connection()


















































# placeholder
