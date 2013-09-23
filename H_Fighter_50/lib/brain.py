"""So eventually this is supposed to be a evolution simulation
meets platform game but for now it's basically a brain"""

import random, math, pygame
from numpy import *
from pygame.locals import *



class Brain(object):
	"A neural network! You can make it, randomize it, or make it process stuff!"
	#import random

	def __init__(self, number_of_inputs, other_node_sizes, activation_functions = None):
		if activation_functions == None:
			activation_functions = [self.afunc, self.afunc]

		#[6,5,5,...] with the 6 for the 
		self._all_layer_sizes = [number_of_inputs + 1] + other_node_sizes

		#[ [0, 0, 0, ...], [0, 0, 0, ...], [0, 0, 0, ...], ... ]
		self.nodes = [ [0]*layer_size for layer_size in self._all_layer_sizes]

		#this is going to be a big jar of matrices
		self._all_edges = []
		for k in range(1,len(self.nodes)):
			height = len(self.nodes[k - 1]) + len(self.nodes[k])
			#because the width determines the size of the output, layer k!
			width = len(self.nodes[k])
			next_edges = [[2*random.random()-1 for w in range(width)] for h in range(height)]
			'''
			for h in range(height):
				for w in range(width):
					if h < len(self.nodes[k]):
						if h == w:
							next_edges[h][w] = -1
						else:
							next_edges[h][w] = random.random()*2-1
					else:
						next_edges[h][w] = random.random()*2-1
			'''

			self._all_edges.append(matrix(next_edges))
		self.nodes = [matrix(t) for t in self.nodes] # NOT ACTUALLY DUMMY NODES ANY MORE
		self.activation_functions = activation_functions
		self.mutationrate = [30,30,30]


	def tester(self):
		"returns zero-valued nodes and a list of matrices representing edges"
		return self.nodes, self._all_edges

	def afunc(self, blah):
		return 2/(1+math.e**-blah)-1

	def randomizenodes(self):
		self.nodes = [ matrix([random.random() for k in range(layer_size)]) for layer_size in self._all_layer_sizes]

	def compute(self, inp):
		"Take the input nodes and work out what happens at the output"
		self.nodes[0] = matrix(inp + [1])
		for i, edges in enumerate(self._all_edges):
			g = append(self.nodes[i+1], self.nodes[i], axis = 1)
			self.nodes[i + 1] = g*edges
			for k in range(self.nodes[i+1].shape[1]):
				self.nodes[i+1][0,k] = self.activation_functions[i](self.nodes[i+1][0,k])
			#self.nodes[i + 1][:] = self.activation_functions[i](self.nodes[i+1][:])
			'''
			#self._thoughts is literally a matrix shaped like a list.
			#I just want to apply a function and this worked.
			self.nodes = array(self.nodes)
			self.nodes = self.activation_functions[i](self.nodes)
			self.nodes = array(self._thoughts)[0]
			self._thoughts = list(self._thoughts)
			#self._thoughts = list(   array(  self.activation_functions[i]( array(self._thoughts) )  )[0]   )
			'''
		return array(self.nodes[-1])[0]

	def mutate(self):
		for layer in self._all_edges:
			s = layer.shape
			for r in range(s[0]):
				for c in range(s[1]):
					if 1:#random.random() >= 0.9**self.mutationrate[0]:
						layer[r,c] *= (random.random()*1) + 0.5
						layer[r,c] += (random.random()*0.1 - 0.05)
						if random.random() > 0.99:
							layer[r,c]*= -1
					#if random.random() >= 0.9**self.mutationrate[1]:
					#	layer[r,c] *= -1
					#if random.random() >= 0.9**self.mutationrate[2]:
					#	layer[r,c] = random.random()*2 - 1

		#self.mutationrate[0] += random.random()*0.2 - 0.1
		#self.mutationrate[1] += random.random()*0.2 - 0.1
		#self.mutationrate[2] += random.random()*0.2 - 0.1
