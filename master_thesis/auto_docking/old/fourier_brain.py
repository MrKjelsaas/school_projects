


import numpy as np
from numpy import sin, cos, pi, tanh





class brain:

    def __init__(self, number_of_inputs, number_of_outputs):

        self.number_of_inputs = number_of_inputs
        self.number_of_outputs = number_of_outputs

        # Topology and predictions
        self.input_amplitudes = np.ones(number_of_inputs, dtype=np.float64)
        self.input_periods = 2*pi*np.ones(number_of_inputs, dtype=np.float64)
        self.input_offsets = 2*pi*np.ones(number_of_inputs, dtype=np.float64)

        self.neuron_layers = [1]
        self.amplitudes = [np.array([1], dtype=np.float64)]
        self.periods = [np.array([2*pi], dtype=np.float64)]
        self.offsets = [np.array([2*pi], dtype=np.float64)]

        self.output_amplitudes = np.ones(number_of_outputs, dtype=np.float64)
        self.output_periods = 2*pi*np.ones(number_of_outputs, dtype=np.float64)
        self.output_offsets = 2*pi*np.ones(number_of_outputs, dtype=np.float64)

        # Weights
        self.weights = [np.ones([self.number_of_inputs+1, self.neuron_layers[0]]),
                        np.ones([self.neuron_layers[0]+1, self.number_of_outputs])]

        # Add weight: self.weights.insert(np.array([a, b]))

        # Mutations
        self.mutation_rate = 0.01
        self.mutation_types = ["random", "add_layer", "add_node", "topology", "alter_weight", "alter_amplitude", "alter_period", "alter_offset"]



    def forward(self, inputs, activation = "relu"):

        x = inputs

        # Feed through the layers
        for layer in range(len(self.weights)):
            try:
                x = np.append(1, x) # Add bias node
                x = np.dot(x, self.weights[layer])
            except ValueError:
                x = np.append(1, x)
                x = np.dot(x, self.weights[layer].T)

            if layer != len(self.weights):
                if activation == "relu":
                    x[x<0] = 0
                elif activation == "tanh":
                    x = tanh(x)

        return x



        """
        output = inputs

        # Feed through the layers
        for layer in range(len(self.neuron_layers)):
            next_output = np.zeros(self.neuron_layers[layer])
            for next_node in range(self.neuron_layers[layer]):
                for node in range(len(output)):
                    next_output[next_node] += self.amplitudes[layer][next_node] * sin(output[node] * self.periods[layer][next_node] + self.offsets[layer][next_node])

            output = next_output

        # Feed through final layer
        next_output = np.zeros(self.number_of_outputs)
        for next_node in range(self.number_of_outputs):
            for node in range(len(output)):
                next_output[next_node] += self.output_amplitudes[next_node] * sin(output[node] * self.output_periods[next_node] + self.output_offsets[next_node])

        return next_output
        """



    def mutate(self, mutation_type="random", place="random", method="standard"):

        if mutation_type == "random":
            mutation_type = np.random.choice(self.mutation_types[3:])

            self.mutate(mutation_type)

        elif mutation_type == "everything":
            for n in range(self.number_of_inputs):
                self.mutate("alter_amplitude", ["input_layer", n])
                self.mutate("alter_period", ["input_layer", n])
                self.mutate("alter_offset", ["input_layer", n])

            for layer in range(len(self.neuron_layers)):
                for node in range(self.neuron_layers[layer]):
                    self.mutate("alter_amplitude", [layer, node])
                    self.mutate("alter_period", [layer, node])
                    self.mutate("alter_offset", [layer, node])

            for n in range(self.number_of_outputs):
                self.mutate("alter_amplitude", ["output_layer", n])
                self.mutate("alter_period", ["output_layer", n])
                self.mutate("alter_offset", ["output_layer", n])
            return

        elif mutation_type == "add_layer":
            if place == "random":
                new_layer_pos = np.random.randint(len(self.neuron_layers))+1
            if new_layer_pos == len(self.neuron_layers):
                self.neuron_layers.append(1)
                self.amplitudes.append(np.array([1], dtype=np.float64))
                self.periods.append(np.array([2*pi], dtype=np.float64))
                self.offsets.append(np.array([2*pi], dtype=np.float64))
                self.weights.append(np.ones([self.neuron_layers[-1]+1, self.number_of_outputs]))
                self.weights[-2] = self.weights[-2][:, :self.neuron_layers[-1]]
            else:
                self.neuron_layers.insert(new_layer_pos, 1)
                self.amplitudes.insert(new_layer_pos, np.array([1], dtype=np.float64))
                self.periods.insert(new_layer_pos, np.array([2*pi], dtype=np.float64))
                self.offsets.insert(new_layer_pos, np.array([2*pi], dtype=np.float64))
                if new_layer_pos == 0:
                    self.weights.insert(new_layer_pos, np.ones([self.number_of_inputs+1], self.neuron_layers[1]))
                    self.weights[1] = self.weights[1][:, :self.neuron_layers[0]+1, :]
                else:
                    self.weights.insert(new_layer_pos, np.ones([self.neuron_layers[new_layer_pos-1]+1, self.neuron_layers[new_layer_pos]]))
                    self.weights[new_layer_pos+1] = self.weights[new_layer_pos+1][:self.neuron_layers[new_layer_pos]+1, :]

        elif mutation_type == "add_node":
            if place == "random":
                layer_to_add_node_to = np.random.randint(len(self.neuron_layers))
            else:
                layer_to_add_node_to = place

            self.neuron_layers[layer_to_add_node_to] += 1
            self.amplitudes[layer_to_add_node_to] = np.append(self.amplitudes[layer_to_add_node_to], np.array([1], dtype=np.float64))
            self.periods[layer_to_add_node_to] = np.append(self.periods[layer_to_add_node_to], np.array([2*pi], dtype=np.float64))
            self.offsets[layer_to_add_node_to] = np.append(self.offsets[layer_to_add_node_to], np.array([2*pi], dtype=np.float64))
            if layer_to_add_node_to == 0:
                self.weights[layer_to_add_node_to] = np.hstack((self.weights[layer_to_add_node_to], np.ones([self.number_of_inputs+1, 1])))
                self.weights[layer_to_add_node_to+1] = np.vstack((self.weights[layer_to_add_node_to+1], np.ones(np.shape(self.weights[layer_to_add_node_to+1])[1])))
            else:
                self.weights[layer_to_add_node_to] = np.hstack((self.weights[layer_to_add_node_to], np.ones([np.shape(self.weights[layer_to_add_node_to-1])[1]+1, 1])))
                self.weights[layer_to_add_node_to+1] = np.vstack((self.weights[layer_to_add_node_to+1], np.ones(np.shape(self.weights[layer_to_add_node_to+1])[1])))

        elif mutation_type == "alter_weight":

            # How strong the mutation will be
            mutation_strength = np.random.rand() * (2*self.mutation_rate) - self.mutation_rate

            if place == "random":
                layer_to_mutate = np.random.randint(len(self.weights))
                a = np.random.randint(np.shape(self.weights[layer_to_mutate])[0])
                b = np.random.randint(np.shape(self.weights[layer_to_mutate])[1])

            if method == "flip":
                self.weights[layer_to_mutate][a, b] *= -1

            self.weights[layer_to_mutate][a, b] *= (1 + mutation_strength)


        elif mutation_type == "alter_amplitude":
            # How strong the mutation will be
            mutation_strength = np.random.rand() * (2*self.mutation_rate) - self.mutation_rate

            if place == "random":
                if np.random.rand() < 1/(len(self.neuron_layers)+2):
                    node_to_mutate = np.random.randint(len(self.output_amplitudes))
                    self.output_amplitudes[node_to_mutate] *= (1 + mutation_strength)
                    return
                elif np.random.rand() < 1/(len(self.neuron_layers)+2):
                    node_to_mutate = np.random.randint(len(self.input_amplitudes))
                    self.input_amplitudes[node_to_mutate] *= (1 + mutation_strength)
                    return
                else:
                    layer_to_mutate = np.random.randint(len(self.neuron_layers))
                    node_to_mutate = np.random.randint(self.neuron_layers[layer_to_mutate])
            else:
                [layer_to_mutate, node_to_mutate] = place

            if layer_to_mutate == "output_layer":
                self.output_amplitudes[node_to_mutate] *= (1 + mutation_strength)
                return
            elif layer_to_mutate == "input_layer":
                self.input_amplitudes[node_to_mutate] *= (1 + mutation_strength)
                return

            # The actual mutation
            self.amplitudes[layer_to_mutate][node_to_mutate] *= (1 + mutation_strength)

        elif mutation_type == "alter_period":
            # How strong the mutation will be
            mutation_strength = np.random.rand() * (2*self.mutation_rate) - self.mutation_rate

            if place == "random":
                if np.random.rand() < 1/(len(self.neuron_layers)+2):
                    node_to_mutate = np.random.randint(len(self.output_periods))
                    self.output_periods[node_to_mutate] *= (1 + mutation_strength)
                    return
                elif np.random.rand() < 1/(len(self.neuron_layers)+2):
                    node_to_mutate = np.random.randint(len(self.input_periods))
                    self.input_periods[node_to_mutate] *= (1 + mutation_strength)
                    return
                else:
                    layer_to_mutate = np.random.randint(len(self.neuron_layers))
                    node_to_mutate = np.random.randint(self.neuron_layers[layer_to_mutate])

            else:
                [layer_to_mutate, node_to_mutate] = place

            if layer_to_mutate == "output_layer":
                self.output_periods[node_to_mutate] *= (1 + mutation_strength)
                return
            elif layer_to_mutate == "input_layer":
                self.input_periods[node_to_mutate] *= (1 + mutation_strength)
                return

            # The actual mutation
            self.periods[layer_to_mutate][node_to_mutate] *= (1 + mutation_strength)

        elif mutation_type == "alter_offset":
            # How strong the mutation will be
            mutation_strength = np.random.rand() * (2*self.mutation_rate) - self.mutation_rate

            if place == "random":
                if np.random.rand() < 1/(len(self.neuron_layers)+2):
                    node_to_mutate = np.random.randint(len(self.output_offsets))
                    self.output_offsets[node_to_mutate] *= (1 + mutation_strength)
                    return
                elif np.random.rand() < 1/(len(self.neuron_layers)+2):
                    node_to_mutate = np.random.randint(len(self.input_offsets))
                    self.input_offsets[node_to_mutate] *= (1 + mutation_strength)
                    return
                else:
                    layer_to_mutate = np.random.randint(len(self.neuron_layers))
                    node_to_mutate = np.random.randint(self.neuron_layers[layer_to_mutate])
            else:
                [layer_to_mutate, node_to_mutate] = place

            if layer_to_mutate == "output_layer":
                self.output_offsets[node_to_mutate] *= (1 + mutation_strength)
                return
            elif layer_to_mutate == "input_layer":
                self.input_offsets[node_to_mutate] *= (1 + mutation_strength)
                return

            # The actual mutation
            self.offsets[layer_to_mutate][node_to_mutate] *= (1 + mutation_strength)

        elif mutation_type == "topology":
            chance_to_add_layer = 1/(len(self.neuron_layers)+1)
            if np.random.rand() < chance_to_add_layer:
                mutation_type = "add_layer"
            else:
                mutation_type = "add_node"
            self.mutate(mutation_type)

        else:
            print("Invalid mutation method")
            print("The following are valid:")
            for n in range(len(self.mutation_types)):
                print(" -", self.mutation_types[n])




    def print_info(self):
        print("Neuron layers:")
        print(self.neuron_layers, "\n")
        print("Amplitudes:")
        print(self.amplitudes, "\n")
        print("Periods:")
        print(self.periods, "\n")
        print("Offsets")
        print(self.offsets, "\n")

















if __name__ == '__main__':

    test_brain = brain(number_of_inputs=17, number_of_outputs=2)

    test_brain.mutate("add_layer")
    test_brain.mutate("add_node")
    test_brain.mutate("add_node")

    test_brain.mutate("alter_amplitude")

    for n in range(100):
        test_brain.mutate()

    #test_brain.print_info()
    #print("\nInfo done\n\n")

    result = test_brain.forward(np.ones(17))
    print(result)

    test_brain.mutate()
    print("\n")

    result = test_brain.forward(np.ones(17))
    print(result)


















