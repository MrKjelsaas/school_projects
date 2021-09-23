
import time
import socket
import select
import numpy as np



def checksum(message):
    checksum = 0
    for character in message:
        checksum ^= ord(character)
    return hex(checksum)[2:]







class otter_usv:

    # Socket for TCP communication
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Constants
    home_coordinates = [("N", 59, 54.492, 0), ("E", 10, 43.180, 0)]
    home_coordinates_decimal = (59.9082, 10.719666666666667)

    top_speed = 0 #m/s

    #Variables
    current_position = home_coordinates
    current_time = 0
    current_angle = 0
    current_speed = 2
    fuel_capacity = 0


    #Used to check whether the Otter SHOULD be connected
    connection_status = False

    last_message_received = ""



    #Initialises a TCP connection
    def establish_connection(self, destination_ip = "192.168.53.xx", destination_port = 2009):
        destination_ip = 'localhost'
        try:
            self.sock.connect((destination_ip, destination_port))
            self.connection_status = True
            return True
        except:
            print("Could not connect to Otter")
            return False



    #Closes the TCP connection
    def close_connection(self):
        try:
            self.sock.close()
            self.connection_status = False
            return True
        except:
            print("Error when disconnecting from Otter")
            return False



    #Checks whether the Otter SHOULD be connected (not if it really is)
    def should_be_connected(self):
        return self.connection_status



    def read_message(self, timeout = 10):
        print("Listening to message from Otter")
        self.sock.setblocking(0)
        ready = select.select([self.sock], [], [], timeout)
        if ready[0]:
            received_message = self.sock.recv(1024).decode()
            self.last_message_received = received_message
            return received_message

        else:
            return ""




    def send_message(self, message):
        print("Sending message:", message)
        try:
            self.sock.sendall(message.encode())
            return True
        except:
            print("Couldn't send message to Otter")
            return False



    def drift(self):
        print("Otter entering drift mode")
        message_to_send = "$PMARABT\r\n"
        return self.send_message(message_to_send)



    def set_autopilot_mode(self, cross_track_error_magnitude, direction_to_steer, cross_track_units, bearing_from_origin_to_destination):
        return False



    def set_manual_control_mode(self, force_x, torque_z):
        print("Otter entering manual control mode with X force:", force_x, "Z torque:", torque_z)
        force_x = str(np.round(force_x, 2))
        torque_z = str(np.round(torque_z, 2))

        message_to_send = "$PMARMAN," + force_x + "," + torque_z + '*'
        message_to_send += checksum(message_to_send[1:-1])
        message_to_send += "\r\n"

        return self.send_message(message_to_send)



    def set_course_mode(self, angle, speed = current_speed):
        print("Otter entering course mode with angle:", angle, "speed:", speed)
        message_to_send = "$PMARCRS," + str(angle) + "," + str(np.round(speed, 2)) + "*"
        message_to_send += checksum(message_to_send[1:-1])
        message_to_send += "\r\n"

        return self.send_message(message_to_send)



    def set_leg_mode(self, origin_coordinates, destination_coordinates, speed = current_speed):
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



    def set_station_mode(self, destination_coordinates, speed = current_speed):
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

        self.set_manual_control_mode(-1, 0, 0)

        while self.current_speed > 0:
            pass

        print("Otter stopped")
        print("Entering drift mode")

        self.drift()







































































# placeholder
