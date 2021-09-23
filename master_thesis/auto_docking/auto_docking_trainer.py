
import matplotlib.pyplot as plt

# These files were collected from https://github.com/cybergalactic/PythonVehicleSimulator
from functions import plotVehicleStates, plotControls, simulate, gnc
from vehicles import *





def degrees_to_radians(x):
    return x * np.pi / 180



def radians_to_degrees(x):
    return x * 180 / np.pi



def rotate_z(p, theta):
    R_z = np.array([[np.cos(theta), -np.sin(theta), 0],
                  [np.sin(theta), np.cos(theta),  0],
                  [0,             0,              1]])

    return np.dot(R_z, p)



# Returns a list of x-y coordinates of the corners of the Otter
def get_otter_corners(eta):
    otter_length = 2.0
    otter_width = 1.08

    x = eta[1]
    y = eta[0]
    yaw = -eta[5]
    left_back_corner = rotate_z(np.array([-otter_width/2, -otter_length/2, 0]), yaw)[:2] + np.array([x, y])
    left_front_corner = rotate_z(np.array([-otter_width/2, otter_length/2, 0]), yaw)[:2] + np.array([x, y])
    right_front_corner = rotate_z(np.array([otter_width/2, otter_length/2, 0]), yaw)[:2] + np.array([x, y])
    right_back_corner = rotate_z(np.array([otter_width/2, -otter_length/2, 0]), yaw)[:2] + np.array([x, y])

    return [left_back_corner, left_front_corner, right_front_corner, right_back_corner]



# Draws the position of the Otter on a matplotlib figure
def plot_otter_position(eta, plot_show = False, draw_center = False):
    otter_length = 2.0
    otter_width = 1.08

    x = eta[1]
    y = eta[0]
    yaw = -eta[5]
    left_back_corner = rotate_z(np.array([-otter_width/2, -otter_length/2, 0]), yaw)[:2] + np.array([x, y])
    left_front_corner = rotate_z(np.array([-otter_width/2, otter_length/2, 0]), yaw)[:2] + np.array([x, y])
    right_front_corner = rotate_z(np.array([otter_width/2, otter_length/2, 0]), yaw)[:2] + np.array([x, y])
    right_back_corner = rotate_z(np.array([otter_width/2, -otter_length/2, 0]), yaw)[:2] + np.array([x, y])
    two_meters_ahead = rotate_z(np.array([0, 2, 0]), yaw)[:2] + np.array([x, y])

    if draw_center == True:
        plt.scatter(x, y)

    plt.plot([left_back_corner[0], left_front_corner[0]], [left_back_corner[1], left_front_corner[1]])
    plt.plot([left_front_corner[0], right_front_corner[0]], [left_front_corner[1], right_front_corner[1]])
    plt.plot([right_front_corner[0], right_back_corner[0]], [right_front_corner[1], right_back_corner[1]])
    plt.plot([right_back_corner[0], left_back_corner[0]], [right_back_corner[1], left_back_corner[1]])
    plt.plot([x, two_meters_ahead[0]], [y, two_meters_ahead[1]])

    if plot_show == True:
        plt.show()



# Draws a sample dock on a matplotlib figure
def plot_dock(dock = "dummy_dock", plot_show = False, draw_center = True):

    if dock == "dummy_dock":
        point_0 = [0, -50]
        point_1 = [23.75, -26.25]
        point_2 = [28.75, -31.25]
        point_3 = [31.25, -28.75]
        point_4 = [26.25, -23.75]
        point_5 = [50, 0]
        dock_center = [27.5, -27.5]

        if draw_center == True:
            plt.scatter(dock_center[0], dock_center[1])

        """
        plt.scatter(point_0[0], point_0[1])
        plt.scatter(point_1[0], point_1[1])
        plt.scatter(point_2[0], point_2[1])
        plt.scatter(point_3[0], point_3[1])
        plt.scatter(point_4[0], point_4[1])
        plt.scatter(point_5[0], point_5[1])
        """

        plt.plot([point_0[0], point_1[0]], [point_0[1], point_1[1]])
        plt.plot([point_1[0], point_2[0]], [point_1[1], point_2[1]])
        plt.plot([point_2[0], point_3[0]], [point_2[1], point_3[1]])
        plt.plot([point_3[0], point_4[0]], [point_3[1], point_4[1]])
        plt.plot([point_4[0], point_5[0]], [point_4[1], point_5[1]])

        if plot_show == True:
            plt.show()

        return

    if dock == "tjuvholmen_swimming_pier":
        return

    if dock == "oslomet_oceanlab_dock":
        return



# Taken from https://en.wikipedia.org/wiki/Geographic_coordinate_system
# Standard value is for OsloMet Oceanlab
def distance_at_longitude(degrees, phi = 10.719278575838432):
    phi = degrees_to_radians(phi)
    return degrees * (11412.84*np.cos(phi) - 93.5*np.cos(3*phi) + 0.118*np.cos(5*phi))



# Taken from https://en.wikipedia.org/wiki/Geographic_coordinate_system
# Standard value is for OsloMet Oceanlab
def distance_at_latitude(degrees, phi = 59.90865634998943):
    phi = degrees_to_radians(phi)
    return degrees * (111132.92 - 559.82*np.cos(2*phi) + 1.175*np.cos(4*phi) - 0.0023*np.cos(6*phi))



# Returns distance in meters between two decimal coordinates
def map_distance(start, end):
    lat_distance = distance_at_latitude(end[0]-start[0], np.average([start[0], end[0]]))
    lon_distance = distance_at_longitude(end[1]-start[1], np.average([start[1], end[1]]))
    distance = np.hypot(lat_distance, lon_distance)
    return distance



def find_otter_position_in_map(global_coordinates, dock = "dummy_dock"):
    # dock is the name of the map we want to find the position in
    x = 0
    y = 0
    return [x, y]










# Simulation parameters: sample time and number of samples
number_of_simulations = 2
simulation_sample_time = 0.02
simulation_sample_time = 0.1
number_of_simulation_steps = 9010
number_of_simulation_steps = 4500
number_of_simulation_steps = 1000
visualize_otter = True
print_information = True
random_starting_position = True
















for simulation_number in range(number_of_simulations):
    print("Starting simulation", simulation_number + 1)

    # Initiate the vehicle class
    the_otter = otter()

    # (Initial) position and attitude of otter
    eta = np.array([0, 0, 0, 0, 0, 0], float)
    if random_starting_position == True:
        eta[0] = 20*np.random.rand() - 10
        eta[1] = 20*np.random.rand() - 10
    """x, y, z, roll, pitch, yaw
    Positive x axis is straight ahead
    Positive y axis is towards starboard
    Positive z axis is into the ocean"""

    # Setting initial parameters
    nu = the_otter.nu # Velocity
    u_actual = the_otter.u_actual # Actual inputs, defined by otter class (that's what Fossen wrote)
    u_control = np.array([0, 0], float) # Step input on thrusters. Max +- 100
    previous_otter_surge = 0 # Used for calculating acceleration
    previous_otter_sway = 0 # Used for calculating acceleration
    previous_otter_heave = 0 # Used for calculating acceleration





    # The reward given at the end of the simulation
    simulation_reward = 0

    # The simulation loop
    for simulation_step in range(number_of_simulation_steps):
        t = simulation_step * simulation_sample_time

        # Sets the force on the left and right thrusters

        if t == 10:
            u_control = np.array([90, -90], float)
        if t == 20:
            u_control = np.array([0, 0], float)
        if t == 30:
            u_control = np.array([90, 90], float)
        if t == 40:
            u_control = np.array([0, 0], float)
        if t == 50:
            u_control = np.array([-30, 30], float)
        if t == 60:
            u_control = np.array([0, 0], float)
        if t == 70:
            u_control = np.array([60, 60], float)
        if t == 80:
            u_control = np.array([0, 0], float)





        # Apply the actual dynamics by integrating
        [nu, u_actual]  = the_otter.dynamics(eta, nu, u_actual, u_control, simulation_sample_time)
        eta = gnc.attitudeEuler(eta, nu, simulation_sample_time)



        # Gather relevant data
        otter_x_position = eta[1]
        otter_y_position = eta[0]
        otter_surge = nu[0]
        otter_sway = nu[1]
        otter_heave = nu[2]
        otter_total_speed = np.sqrt(nu[0]**2 + nu[1]**2 + nu[2]**2)
        otter_surge_acceleration = nu[0] - previous_otter_surge
        otter_sway_acceleration = nu[1] - previous_otter_sway
        otter_heave_acceleration = nu[2] - previous_otter_heave
        otter_yaw = -eta[5]

        dock_position = [27.5, -27.5]
        dock_angle = degrees_to_radians(-135)

        distance_between_otter_and_dock = np.hypot(dock_position[0]-otter_x_position, dock_position[1]-otter_y_position)
        angular_difference_between_otter_and_dock = dock_angle - otter_yaw
        while angular_difference_between_otter_and_dock > np.pi:
            angular_difference_between_otter_and_dock -= 2*np.pi
        while angular_difference_between_otter_and_dock <= -np.pi:
            angular_difference_between_otter_and_dock += 2*np.pi

        previous_otter_position = [eta[1], eta[0]]
        previous_otter_surge = nu[0]
        previous_otter_sway = nu[1]
        previous_otter_heave = nu[2]
        previous_otter_yaw = -eta[5]




        # Prints information on the Otter (speed etc)
        if print_information == True:
            if t % 10 == 0:
                print("t:", t)
                print("u_control:", u_control)
                print("")
                print("Surge:", nu[0])
                print("Sway:", nu[1])
                print("Heave:", nu[2])
                print("Total speed:", np.sqrt(nu[0]**2 + nu[1]**2 + nu[2]**2))
                print("")
                print("x:", eta[0])
                print("y:", eta[1])
                print("z:", eta[2])
                print("")
                print("Roll:", eta[3])
                print("Pitch:", eta[4])
                print("Yaw:", eta[5])
                print("Angular difference:", angular_difference_between_otter_and_dock)

                print("\n")


        # Visualizes the vessel's position and orientation
        if visualize_otter == True:
            plt.clf()
            plt.ion()
            plt.xlim(-50, 50)
            plt.ylim(-50, 50)
            plot_otter_position(eta)

            plot_dock()

            plt.draw()
            plt.pause(0.001)















        # Ends simulation if Otter is out of bounds
        if not (-50 < eta[0] < 50 and -50 < eta[1] < 50):
            print("\n")
            print("------------------------")
            print("Otter went out of bounds")
            print("Ending simulation")
            print("------------------------")
            simulation_reward = -1
            break

        # Ends simulation if time is reached
        #if t >= 180:
        if t == (number_of_simulation_steps*simulation_sample_time) - simulation_sample_time:
            print("\n")
            print("------------------------")
            print("Reached time limit")
            print("Ending simulation")
            print("------------------------")
            simulation_reward = (np.hypot(100, 100) - distance_between_otter_and_dock)/np.hypot(100, 100) + (np.pi - abs(angular_difference_between_otter_and_dock))/np.pi
            break



        # Check if Otter crashed with the dock
        otter_crashed = False
        otter_corners = get_otter_corners(eta)

        for corner in otter_corners:
            x, y = corner[0], corner[1]
            if 28.75 <= x < 31.35:
                if y < x-60:
                    otter_crashed = True

            if 0 <= x < 28.75:
                if (y < x-50) and (y < -x-2.5):
                    otter_crashed = True

            if 26.25 <= x < 50:
                if (y < x-50) and (y > -x+2.5):
                    otter_crashed = True

        if otter_crashed == True:
            print("\n")
            print("------------------------")
            print("Otter crashed into the dock")
            print("Ending simulation")
            print("------------------------")
            simulation_reward = -0.5*otter_total_speed**2
            break



    print("")
    print("------------------------")
    print("Simulation reward:")
    print(simulation_reward)
    print("------------------------")
    print("\n")

































#





"""
Plan of attack:

- Set up an environment for the agent to train in
 - A map of the docking area
 - A way to simulate the otter

- State
 - GPS position
 - Speed
 - Yaw
 - Camera feed
 - Lidar?

- Control the inputs
 - Thruster power allocation
  - Increase left thruster, increase right thruster
  - Increase left thruster, no change right thruster
  - Increase left thruster, decrease right thruster
  - No change left thruster, increase right thruster
  - No change left thruster, no change right thruster
  - No change left thruster, decrease right thruster
  - Decrease left thruster, increase right thruster
  - Decrease left thruster, no change right thruster
  - Decrease left thruster, decrease right thruster

- Session ends if:
 - Vessel docked
 - Vessel crashes
 - Timeout
 - Vessel out of bounds

- Positive reward:
 - Ongoing
  - Heading in right direction? (We can do this in the beginning to train it, then remove it when it performs okay)
 - Final
  - How close the vessel is to the destination
  - Correct orientation

- Negative reward:
 - Crashes
 - Time
 - Fuel consumption?





"""
