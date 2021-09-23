import numpy as np
from ship_dynamics import ship_dynamics_functions




class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position



def a_star(maze, start, end):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end
    while len(open_list) > 0:

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1] # Return reversed path

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]] != 0:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue

            # Add the child to the open list
            open_list.append(child)



def find_route(current_position, destination):

    #NE: N59° 55", E10° 44.5"
    #NE: 59.916666666666664, 10.741666666666667
    #SW: N59° 54", E10° 41.0"
    #SW: 59.9, 10.683333333333334
    #Map size: 100 x 350

    x = current_position[0] - 59.9
    x /= 59.916666666666664 - 59.9
    x *= 100
    x = 100 - x
    x = np.round(x, 0)
    x = int(x)

    y = current_position[1] - 10.683333333333334
    y /= 10.741666666666667 - 10.683333333333334
    y *= 350
    y = np.round(y, 0)
    y = int(y)

    scaled_current_position = (x, y)


    x = destination[0] - 59.9
    x /= 59.916666666666664 - 59.9
    x *= 100
    x = 100 - x
    x = np.round(x, 0)
    x = int(x)

    y = destination[1] - 10.683333333333334
    y /= 10.741666666666667 - 10.683333333333334
    y *= 350
    y = np.round(y, 0)
    y = int(y)

    scaled_destination = (x, y)

    oslofjord_binary_map = np.loadtxt("path_planning/oslofjord_binary_map.csv")

    route = a_star(oslofjord_binary_map, scaled_current_position, scaled_destination)

    descaled_route = []
    for n in range(len(route)):
        x = 100 - route[n][0]
        x /= 100
        x *= 59.916666666666664 - 59.9
        x += 59.9

        y = route[n][1]
        y /= 350
        y *= 10.741666666666667 - 10.683333333333334
        y += 10.683333333333334


        descaled_route.append((x, y))

    for n in range(len(descaled_route)):
        descaled_route[n] = ship_dynamics_functions.decimal_to_degrees_minutes_seconds(descaled_route[n])

    return descaled_route









if __name__ == "__main__":

    #NE: 5955.000, 1044.500
    #SW: 5954.000, 1041.000

    oslofjord_binary_map = np.loadtxt("oslofjord_binary_map.csv")
    #print(oslofjord_binary_map)
    #print(oslofjord_binary_map.shape) 1000, 3500

    a_star_solution = a_star(oslofjord_binary_map, (0, 0), (750, 250))
    print("A star path solution:", a_star_solution)
