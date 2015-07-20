import numpy as np
from numpy import matrix, fmax, dot, zeros, tanh
from scipy.special import expit
import random


# Each block of nodes has a final block and buffer block,
# in different rows of a matrix.
N_BLOCKS = 3
FINAL_ROW = 0
ADD_ROW = 1
MULTIPLY_ROW = 2

# Fixed names of cluster nodes
CLUSTER_INPUT = 0
CLUSTER_INTERMEDIATE = 1
CLUSTER_OUTPUT = -1

# Activations
EXPIT = 0
RELU = 1
TANH = 2


class ComputationUnit(object):
    # parametrizes a family of operations on clusters.
    # it is a container for matrices, not for vectors.

    def __init__(self, input_info, output_info, activation=TANH):
        # input_info is a list of name-size tuples
        # output is a string-size tuple
        self.input_info = input_info
        self.output_name, self.output_size = self.output_info = output_info
        self.matrices = {name: matrix(zeros((input_size, self.output_size)))
                         for (name, input_size) in self.input_info}
        self.dropout_matrices = {name: matrix(zeros((input_size, self.output_size)))
                                 for (name, input_size) in self.input_info}
        self.activation = activation
        for i in range(120):
            self.mutate()
        self.counter = 0
        self.randomize_dropout(0.5)

    def loginformation(self, clusters):
        print "Logging brain cluster state."
        print "inputs:"
        for input_name, input_size in self.input_info:
            print "--[", input_name, "]:", clusters[input_name][FINAL_ROW, :]
        print "output:"
        print "--[add]:", clusters[self.output_name][ADD_ROW, :]
        print "--[multiply]:", clusters[self.output_name][MULTIPLY_ROW, :]
        print "--[final]:", clusters[self.output_name][FINAL_ROW, :]

    def randomize_dropout(self, p):
        for n, m in self.dropout_matrices.iteritems():
            s, t = m.shape
            if random.random() < 0.5:
                # use averaged model
                for i in range(s):
                    for j in range(t):
                        m[i, j] = self.matrices[n][i, j] * p
            else:
                # use dropout model
                for i in range(s):
                    if random.random() < p:
                        for j in range(t):
                            m[i, j] = self.matrices[n][i, j]
                    else:
                        for j in range(t):
                            m[i, j] = 0

    # tried hard here to not require creation of additional arrays
    def compute(self, clusters):
        self.counter += 1
        self.counter %= 50
        if self.counter == 0:
            self.randomize_dropout(0.5)
        # clusters are a dictionary of arrays of brain data.

        # this is where we leave the products of multiplications
        output_multiply_vector = clusters[self.output_name][MULTIPLY_ROW, :]

        # this is where we sum up various products of multiplications
        output_add_vector = clusters[self.output_name][ADD_ROW, :]
        output_add_vector.fill(0.0)

        # for each input to our block
        for input_name, input_size in self.input_info:
            input_vector = clusters[input_name][FINAL_ROW, :]
            # multiply
            dot(input_vector, self.dropout_matrices[input_name],
                out=output_multiply_vector)
            # add
            output_add_vector += output_multiply_vector

        # apply sigmoid function
        output_final_vector = clusters[self.output_name][FINAL_ROW, :]

        np.clip(output_add_vector, -100, 100, out=output_add_vector)

        if (self.activation == EXPIT):
            expit(output_add_vector, out=output_final_vector)
        elif (self.activation == TANH):
            tanh(output_add_vector, out=output_final_vector)
        elif (self.activation == RELU):
            fmax(output_add_vector, 0.0, out=output_final_vector)
        elif (self.activation is None):
            output_final_vector[:] = output_add_vector
        else:
            raise NotImplementedError("Invalid activation", self.activation)

        if np.isnan(output_final_vector).any():
            self.loginformation(clusters)
            raise Exception("Activation produced nans.")

    def mutate(self):
        mutation_weight = 0.1
        for n, m in self.matrices.iteritems():
            self.matrices[n] += mutation_weight * \
                (2 * np.random.random(m.shape) - 1)


class ComplexBrain(object):

    def __init__(self, n_inputs, n_hidden, n_outputs):
        self.nodetags = {}  # here for code compatibility only
        self.n_inputs = n_inputs
        self.n_hidden = n_hidden
        self.n_outputs = n_outputs
        self.clusters = {
            CLUSTER_INPUT: matrix(zeros((N_BLOCKS, self.n_inputs))),
            CLUSTER_INTERMEDIATE: matrix(zeros((N_BLOCKS, self.n_hidden))),
            CLUSTER_OUTPUT: matrix(zeros((N_BLOCKS, self.n_outputs)))
        }

        unit_1 = self.set_up_unit((CLUSTER_INPUT,), CLUSTER_INTERMEDIATE,
                                  activation=RELU)
        unit_2 = self.set_up_unit((CLUSTER_INTERMEDIATE,), CLUSTER_OUTPUT,
                                  activation=EXPIT)

        self.computation_units = [unit_1, unit_2]

    def set_up_unit(self, input_names, output_name, activation=None):
        input_info = [(name, self.clusters[name].shape[1])
                      for name in input_names]
        output_info = (output_name, self.clusters[output_name].shape[1])
        return ComputationUnit(input_info, output_info, activation)

    def set_inputs(self, inputs):
        self.clusters[CLUSTER_INPUT][FINAL_ROW, :] = inputs[0, :]

    def randomizenodes(self):  # here for code compatibility
        for name, vector in self.clusters.iteritems():
            vector += 1 * np.random.random(vector.shape) - 0.5

    def compute(self, inputs):
        self.set_inputs(matrix(inputs))
        for comp_unit in self.computation_units:
            comp_unit.compute(self.clusters)

    def get_outputs(self, outputs):
        outputs[:, :] = self.clusters[CLUSTER_OUTPUT][FINAL_ROW, :]

    def mutate(self):
        for unit in self.computation_units:
            unit.mutate()
