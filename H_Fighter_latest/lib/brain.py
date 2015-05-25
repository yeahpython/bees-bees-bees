# module representing the brain of a bee

import random, math, pygame

import numpy as np
#from numpy import *
from numpy import matrix, array, linalg
from pygame.locals import *
import graphics
from test import add_sticky, remove_sticky
from copy import deepcopy
import messages
from numpy import linalg, dot
from game_settings import *
from scipy.special import expit

font = pygame.font.SysFont("Droid Serif", 30)


'''
force = 0.5
specialforcerules = {
						"wall above right" : matrix([force, -force, -force]),
						"wall below right" : matrix([force, force, -force]),
						"wall above left" : matrix([-force, -force, -force]),
						"wall below left" : matrix([-force, force, -force]),
						"go up" : matrix([0, -force, force]),
						"go down" : matrix([0, force, force]),
						"go left" : matrix([-force, 0, force]),
						"go right" : matrix([force, 0, force]),
						}

for message in specialforcerules:
	specialforcerules[message][0,2] *= 2

#specialforcerules["wall above right"] = matrix([force,-force, 0])
#specialforcerules["wall below right"= matrix([force,force, 0]),


off = 2000
specialdrawinglines = {
						"wall above right" : [off, -off],
						"wall below right" : [off, off],
						"wall above left" : [-off, -off],
						"wall below left" : [-off, off],
						"go up" : [0, -off],
						"go down" : [0, off],
						"go left" : [-off, 0],
						"go right" : [off, 0],
						}
'''


include_cycles = False	

def afunc(x):
	if settings[BRAIN_ACTIVATION] == 1:
		return x / 10
	elif settings[BRAIN_ACTIVATION] == 2:
		return x > 0
	else:
		return 1/(1+math.e**(-x))

def welp(x):
	return 2/(1+math.e**-x) - 1


class Brain(object):
	def __init__(self, number_of_inputs, other_node_sizes, activation_functions = None):
		self.nodetags = {}

		if activation_functions:
			self.activation_functions = activation_functions
		else:
			#activation_functions = [expit, expit, expit, expit, expit, expit]
			self.activation_functions = [afunc, afunc, afunc, afunc, afunc, afunc]

		self._layer_sizes = [number_of_inputs + 1] + other_node_sizes
		
		self.nodes = None
		self.randomizenodes()

		self._all_edges = None
		self.randomizeconnections()

		self.mutationrate = [30,30,30]


	def randomizenodes(self):
		self.nodes = [ matrix(np.random.random( (1, layer_size) ) - 0.5) for layer_size in self._layer_sizes]

	def randomizeconnections(self):
		self._all_edges = []
		for first, second in zip(self._layer_sizes, self._layer_sizes[1:]):
			self._all_edges.append(matrix(10 * np.random.random((first + include_cycles * second, second)) - 5))
		'''for layer in self._all_edges:
			s = layer.shape
			for r in range(s[0]):
				for c in range(s[1]):
					layer[r,c] = random.random()*10 - 5'''

	def loadinputs(self, inp):
		for i in range(len(inp)):
			self.nodes[0][0,i] = inp[i]

	def compute(self, inp, use_memory = 1):
		prefix = 'bee:update:thinking:compute:'
		"Take the input nodes and work out what happens at the output"
		#settings[BRAIN_BIAS]
		add_sticky(prefix + "1")
		self.loadinputs(inp + [settings[BRAIN_BIAS]])
		#self.nodes[0] = matrix(inp + [settings[BRAIN_BIAS]])
		remove_sticky(prefix + "1")
		
		
		for i, edges in enumerate(self._all_edges):
			add_sticky(prefix + 'multiplication')
			if include_cycles:
				'''combine current and previous layer'''
				add_sticky(prefix + 'multiplication:appending')
				g = append( settings[MEMORY_STRENGTH] * use_memory * self.nodes[i+1], self.nodes[i], axis = 1)
				remove_sticky(prefix + 'multiplication:appending')
				#g = append( use_memory * self.nodes[i+1], self.nodes[i], axis = 1)
				dot(g,edges, out=self.nodes[i+1])
				#self.nodes[i + 1] = g*edges
			else:
				dot(self.nodes[i], edges, out=self.nodes[i+1])
			remove_sticky(prefix + 'multiplication')
			add_sticky(prefix + 'activation')
			'''apply activation function'''
			expit(self.nodes[i+1], out = self.nodes[i+1])
			remove_sticky(prefix + 'activation')
		return self.nodes[-1] #output is now a matrix; used to be a list

	def mutate(self):
		#print self._all_edges
		for layer in self._all_edges:
			s = layer.shape
			for r in range(s[0]):
				for c in range(s[1]):
					if random.random() < settings[MUTATION_CHANCES]:
						layer[r,c] *= (random.random()*2 - 1) * settings[SCALING_MUTATION]  + 1
						layer[r,c] += (random.random()*2 - 1) * settings[ADDITIVE_MUTATION_RATE]
						if random.random() < settings[INVERT_MUTATION_RATE]:
							layer[r,c]*= -1
						#if layer[r,c] > 5:
						#	layer[r,c] = 5.0
						#if layer[r,c] < -5:
						#	layer[r,c] = -5.0
					#if random.random() >= 0.9**self.mutationrate[1]:
					#	layer[r,c] *= -1
					#if random.random() >= 0.9**self.mutationrate[2]:
					#	layer[r,c] = random.random()*2 - 1

		#self.mutationrate[0] += random.random()*0.2 - 0.1
		#self.mutationrate[1] += random.random()*0.2 - 0.1
		#self.mutationrate[2] += random.random()*0.2 - 0.1


	# Non-fundamental function:
	def drawfromlocationtable(self, locations, sf, scalefactor = 1.0, translation = matrix([0.0,0.0,0.0]), detailed = 1, rotation = 0, shownegatives = 1, showlines = 1, time = -1):
		mindepth = locations[(0,0)][0,2] * 1
		maxdepth = locations[(0,0)][0,2] * 1
		for i, layer in enumerate(self.nodes):
			for j in range(layer.shape[1]):
				mindepth = min(mindepth, locations[(i,j)][0,2])
				maxdepth = max(maxdepth, locations[(i,j)][0,2])
		
		if detailed:
			minconnection, maxconnection = get_connection_strength_range(self._all_edges)

			selected = None
			x,y = pygame.mouse.get_pos()
			for node, vector in locations.iteritems():
				position = array(vector / scalefactor - translation)[0]
				pos2d = get2DPoint(position, rotation)
				if (pos2d[0] - x) ** 2 + (pos2d[1] - y) ** 2 < 100:
					selected = node


			for i, layer in enumerate(self._all_edges):
				if selected and (i not in [selected[0]-1, selected[0]]):
					continue
				s = layer.shape
				for j1 in range(s[0]):
					#fir is an array representing the first node
					

					fir = 0
					if j1 < self.nodes[i].shape[1]:
						fir = array(locations[(i,j1)] / scalefactor - translation)[0]
					elif include_cycles and j1 < self.nodes[i].shape[1] + self.nodes[i+1].shape[1]:
						fir = array(locations[(i+1,j1 - self.nodes[i].shape[1])] / scalefactor - translation)[0]
					else:
						break
					for j2 in range(s[1]):
						'''iterating over all connected neurons first = (i, j1) second = (i+1, j2)'''
						# sec is an array representing the first node
						if selected and ((i, j1) != selected) and ((i+1, j2) != selected):
							continue
						sec = array(locations[(i+1,j2)] / scalefactor - translation)[0] * 1


						#v = 2*afunc(layer[j1, j2]) - 1
						v = layer[j1, j2]
						color = 0
						if v > 0:
							intensity = v/maxconnection
							#if intensity < 0.1:
							#	continue
							color = [0,intensity*255,0]
						else:
							#if v > 0.1 * minconnection:
							#	continue
							if shownegatives:
								intensity = v/minconnection
								color = [intensity*255, 0, 0]
							else:
								continue
						#if j1 < self.nodes[i].shape[1]:
						#	secondpoint = (secondpoint + firstpoint) / 2
						
						pieces = 1

						'''lightup = []
						if time != -1:
							t = time / 2
							lightup = [t]
							lightup = [-x % pieces for x in lightup]'''

							

						for index in range(pieces):
							a = index * 1.0 / pieces
							b = 1 - a

							a2 = (index + 1.0) / pieces
							b2 = 1 - a2

							firstpoint = a*fir + b*sec
							secondpoint = a2*fir + b2*sec

							width = 1 + index

							offset = secondpoint - firstpoint

							mid = (secondpoint[2] + firstpoint[2]) /2

							offx = offset[0] / linalg.norm(matrix(offset))
							offx = (offx + 3) / 4
							
							#this makes brighness dependent on angle
							zscale = 1

							brightnessbyproximity = 0
							if brightnessbyproximity:
								if maxdepth > mindepth:
									zscale = (mid - mindepth) / (maxdepth - mindepth)
									zscale = 0.5 * (zscale + 1)
									color = [x * zscale for x in color]
								else:
									print "whaat"

							color = [max(0, x) for x in color]
							color = [min(255, x) for x in color]

							one2D = get2DPoint(firstpoint, rotation)
							two2D = get2DPoint(secondpoint, rotation)


							if 0 and index in lightup:
								m = max(color[0], color[1])
								pygame.draw.line(sf, [m, m, 0], one2D, two2D, int(width))
							else:
								pygame.draw.line(sf, color, one2D, two2D, int(width))

		'''circles!'''
		for i, layer in enumerate(self.nodes):
			for j in range(layer.shape[1]):
				#locations[(i,j)] += velocities[(i,j)]
				pt3D = array(locations[(i,j)] / scalefactor - translation)[0]
				color = graphics.colorcycle[i%5]
				c = [layer[0,j] * x for x in color]
				c = [ int(x) for x in color]
				pt = get2DPoint(pt3D, rotation)
				pt = [int(x) for x in pt]
				z = locations[(i,j)][0,2] * 1
				z = (z - mindepth) / (maxdepth - mindepth)
				z += 1
				pygame.draw.circle(sf, c, pt, int(5 * z), 0)
				if (i,j) in self.nodetags:
					kind, message = self.nodetags[i,j]
					if kind == "vector": 
						if showlines:
							x,y = message
							offset = matrix([x,y,0])
							pt3D[0] += offset[0,0]
							pt3D[1] += offset[0,1]
							otherpoint = get2DPoint(pt3D, rotation)
							#otherpoint = [original + diff for original, diff in zip(pt, offset)]
							pygame.draw.line(sf, (255, 255, 255), pt, otherpoint, 1)
					elif kind == "verbatim":
						text = font.render(message, 1, [200,200,200])
						textpos = text.get_rect(left = pt[0] + 10, centery = pt[1])
						if pt[0] < graphics.screen_w/2:
							textpos = text.get_rect(right = pt[0] - 10, centery = pt[1])
						sf.blit(text, textpos)
					'''if 1 or message not in ["wall above right", "wall below right", "wall above left", "wall below left", "go up", "go down", "go left", "go right"]:
						text = font.render(message, 1, [200,200,200])
						textpos = text.get_rect(left = pt[0] + 10, centery = pt[1])
						if pt[0] < graphics.screen_w/2:
							textpos = text.get_rect(right = pt[0] - 10, centery = pt[1])
						sf.blit(text, textpos)'''
					
		pygame.display.flip()

	def evaluate(self, locations):
		total = 0
		for i, layer in enumerate(self._all_edges):
			s = layer.shape
			for j1 in range(s[0]):
				if j1 == self.nodes[i].shape[1]:
					break;
				for j2 in range(s[1]):
					#firstpoint = (i*hscale + hoff, j1*vscale + voff)
					#secondpoint = ((i+1)*hscale + hoff, j2*vscale + voff)
					one = locations[(i,j1)]
					two = locations[(i+1,j2)]
					distance = linalg.norm(one-two)
					f = distance * distance

					influence = abs(layer[j1, j2])
					total -= f * influence # quality is decreased when connected things are far apart
		
		for _, v in locations:
			for _, v2 in locations:
				if v != v2:
					d = linalg.norm(v - v2)
					total += 1000 / d # this is like electric potential


		return total

	def computevelocities(self, velocities, locations):
		for i, layer in enumerate(self._all_edges):
			s = layer.shape
			for j1 in range(s[0]):
				if j1 == self.nodes[i].shape[1]:
					break;
				for j2 in range(s[1]):
					#firstpoint = (i*hscale + hoff, j1*vscale + voff)
					#secondpoint = ((i+1)*hscale + hoff, j2*vscale + voff)

					p1 = (i,j1)
					p2 = (i+1,j2)

					one = locations[p1]
					two = locations[p2]

					d = one-two
					nd = linalg.norm(d)


					v = layer[j1, j2]
					# attractive for is only on connections
					springconstant = abs(v) / 2000
					positive_connections_only = 0
					if positive_connections_only and v < 0:
						springconstant = 0

					if abs(v) < 0.5:
						continue
					velocities[p1] += springconstant * -d
					velocities[p2] += springconstant * d

		#Iterating through all pairs of locations
		for n1, l1 in locations.iteritems():
			#apply special forces to some nodes
			if n1 in self.nodetags:
				kind, message = self.nodetags[n1]
				if kind == "vector":
					x,y = message
					velocities[n1] += array([x, y, -1000]) * 0.1

			for n2, l2 in locations.iteritems():
				away = l1 - l2
				nd = linalg.norm(away)

				if not nd:
					continue
				# electrostatic repulsion
				# applied between all nodes
				
				# now applying criterion based on which layer / position the nodes is in
				'''i1, ji = n1[0],  n1[1]
				i2, j2 = n2[0], n2[1]

				#separating layers with repulsion
				similarity = 0

				differentlayerrepulsion = 0
				if i1 != i2:
					differentlayerrepulsion = 1
				else:
					if i2 < len(self._all_edges):
						similarity = (self._all_edges[i2][j1] * self._all_edges[i2][j2].T)[0,0]
						if similarity > 0:
							velocities[n1] += similarity * -away
							print similarity
				'''

				#repulsion from different layers
				#repulsion = 1 + differentlayerrepulsion# - 0.05 * similarity
				repulsion = 10000
				velocities[n1] += repulsion * away / nd / nd / nd


			speed = linalg.norm(velocities[n1])
			cap = 0.2
			if speed > cap:
				velocities[n1] /= speed
				velocities[n1] *= cap

			velocities[n1] *= 0.9
			#if linalg.norm(velocities[n1]) < 0.01:
			# 	velocities[n1]*=0

	def visualize(self, surface):
		background = pygame.Surface((graphics.screen_w, graphics.screen_h))
		background.fill((0, 0, 0))

		tosay = [
				"left / right: turn around",
				"up / down: move around",
				"z: zoom out",
				"x: zoom in",
				"c: reset zoom",
				"s: toggle negatives",
				"l: toggle lines",
				"p: toggle physics simulation",
				"q: quit",
				"o: back"
				]

		for i, message in enumerate(tosay):
			messages.say(message, time = 0, down = i, surface = background, color = [255,255,255], size = "small")

		hscale = 700 / 4
		vscale = 30
		hoff = 100
		voff = 100
		sf = pygame.display.get_surface()
		locations = {}
		velocities = {}
		scalefactor = 1
		translation = matrix([0,0, 0])
		rotation = 0
		for i, layer in enumerate(self.nodes):
			for j in range(layer.shape[1]):
				#locations[(i,j)] = matrix([i*hscale + hoff, j*vscale + voff])
				locations[(i,j)] = matrix([ i * 200, j * 10,  random.random()*10 - 5])
				theta = random.random() * 2 * 3.1415926
				velocities[(i,j)] = 0.1 * matrix([math.cos(theta),math.sin(theta), random.random() * 2 - 1])
		
		self.drawfromlocationtable(locations, sf, 1, translation)
		#pygame.draw.circle(sf, (0, 255, 255), (100, 100), int(50 * random.random()) + 10, 1)

		clock = pygame.time.Clock()
		done = 0
		currmax = self.evaluate(locations)
		n = 0
		simulatephysics = True
		scalerate = 1.3
		#a = raw_input('type "1" for low res, "2" for high res \n')
		shownegatives = 1
		showlines = 0
		quit = 0
		previous_key_states = []
		key_downs = []

		consecutive_no_improvement = 0



		while not (done or pygame.event.get(pygame.QUIT)):
			n += 1
			clock.tick(60)
			key_presses = pygame.event.get(pygame.KEYDOWN)
			key_states = pygame.key.get_pressed()

			if previous_key_states:
				key_downs = [new and not old for new, old in zip(key_states, previous_key_states)]
			else:
				previous_key_states = [0 for key in key_states]
				key_downs = [0 for key in key_states]


			if key_states[pygame.K_q]:
				quit = 1
				done = 1

			if key_downs[pygame.K_s]:
				shownegatives = not shownegatives

			

			if key_downs[pygame.K_p]:
				simulatephysics = not simulatephysics

			if key_downs[pygame.K_l]:
				showlines = not showlines

			stepsize = 100

			moving = False
			if key_states[pygame.K_z]:
				moving = True
				scalefactor *= scalerate
				avelocs(locations,scalefactor)

			if key_states[pygame.K_x]:
				moving = True
				scalefactor /= scalerate
				avelocs(locations,scalefactor)

			if key_downs[pygame.K_c]:
				moving = True
				scalefactor = 1.0
				translation *= 0

			if key_states[pygame.K_UP]:
				moving = True
				translation[0,1] -= stepsize
				avelocs(locations,scalefactor)

			if key_states[pygame.K_DOWN]:
				moving = True
				translation[0,1] += stepsize
				avelocs(locations,scalefactor)

			pi = 3.1415926

			if key_states[pygame.K_LEFT]:
				moving = True
				rotation += 0.05 * pi

				#translation[0,0] -= stepsize
			if key_states[pygame.K_RIGHT]:
				moving = True
				rotation -= 0.05 * pi


			


			

			
			if simulatephysics and not moving:
				'''
				# random improvement
				for _ in range(5):
					oldlocations = deepcopy(locations)
					for k in locations:
						locations[k] += matrix(5 * np.random.random((1,3)) - 3)
					if not (pygame.key.get_pressed()[pygame.K_z] or pygame.key.get_pressed()[pygame.K_x]):
						scalefactor = scalefactor**0.8 * automaticscale(locations)**0.2
					avelocs(locations,scalefactor)
					new_value = self.evaluate(locations)
					if new_value > currmax:
						locations = oldlocations
						currmax = new_value
						consecutive_no_improvement = 0
						
					else:
						consecutive_no_improvement += 1
						if consecutive_no_improvement > 1000:
							simulatephysics = False'''

				

				

				for i, layer in enumerate(self.nodes):
					for j in range(layer.shape[1]):
						locations[(i,j)] += velocities[(i,j)] * 100
				self.computevelocities(velocities, locations)
				for i, layer in enumerate(self.nodes):
					for j in range(layer.shape[1]):
						locations[(i,j)] += velocities[(i,j)] * 100
				if not (pygame.key.get_pressed()[pygame.K_z] or pygame.key.get_pressed()[pygame.K_x]):
					scalefactor = scalefactor**0.8 * automaticscale(locations)**0.2
				avelocs(locations,scalefactor)
				if all_nodes_stationary(velocities, scalefactor):
					simulatephysics = False
					for i, layer in enumerate(self.nodes):
						for j in range(layer.shape[1]):
							velocities[(i,j)] *= 0


			detailed = 0
			if 1 or n % 10 == 0 or key_states[pygame.K_SPACE]:
				detailed = 1

			activekeys = [pygame.K_l, pygame.K_s, pygame.K_z, pygame.K_c, pygame.K_x, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
			if 1 or simulatephysics or any(key_states[key] for key in activekeys):
				sf.blit(background, (0,0))
				self.drawfromlocationtable(locations, sf, scalefactor, translation, detailed, rotation, shownegatives, showlines, time = n)
				#messages.say("scaling is " + str(scalefactor), 0, down = 20, size = "small")
				pygame.display.flip()
			if key_states[pygame.K_o]:
				done = 1

			previous_key_states = key_states[:]
		return quit

# this is for visualization of brain
basicallynotmoving = 0.015
def all_nodes_stationary(velocities, scalefactor):
	#return all(linalg.norm(v) < basicallynotmoving * scalefactor for k,v in velocities.iteritems())
	for k, v in velocities.iteritems():
		n = linalg.norm(v)
		if n > basicallynotmoving * scalefactor:
			return False
	return True

def avelocs(locations, scalefactor):
	count=0
	total = matrix([0,0,0])

	for key, value in locations.iteritems():
		total += value
		count += 1
	ave = total / count
	for key, value in locations.iteritems():
		locations[key] -= ave

def automaticscale(locations):
	maximum = 0
	for k, v in locations.iteritems():
		p = array(v)[0]
		dist = linalg.norm(v - matrix([graphics.screen_w, graphics.screen_h, 0]))
		maximum = max(dist, maximum)
	return maximum / 2000

def get2DPoint(Point3D, theta):
	rotation = matrix([[math.cos(theta),0,-math.sin(theta)],[0,1,0],[math.sin(theta),0,math.cos(theta)]])
	p = matrix(Point3D) * rotation.T
	p = array(p)[0]
	a = [p[0],p[1]]
	a[1] += 0.2 * p[2]
	a[0] += graphics.screen_w / 2
	a[1] += graphics.screen_h / 2
	'''
	distortion = p[2] / 500
	if distortion > 0.5:
		distortion = 0.5
	if distortion < -0.5:
		distortion = -0.5
	a[0] *= 1 + distortion'''
	return a

def get_connection_strength_range(edges):
	maxconnection = 0
	minconnection = 0
	for i, layer in enumerate(edges):
		s = layer.shape
		for j1 in range(s[0]):
			for j2 in range(s[1]):
				#weight = 2*afunc(layer[j1, j2]) - 1
				weight = layer[j1, j2]
				if weight > 0:
					maxconnection = max(weight, maxconnection)
				elif weight < 0:
					minconnection = min(weight, minconnection)
	return minconnection, maxconnection
