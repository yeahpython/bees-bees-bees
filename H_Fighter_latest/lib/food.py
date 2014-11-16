import random
import pygame
import graphics
import math
import collision
from numpy import linalg, matrix, array
import numpy
import test
import itertools
import physical
import brain
import random
from time import time
import copy

gravity = matrix([[0, 0.0006]])
jumpspeed = 0.4
jumpvel = matrix([[0, -jumpspeed]])
maxvel = 0.5
maxvelx = 0.3
groundacc = 0.02
airacc = 0.02
airresist = 0.0000001
friction = 0.001

afunc = lambda blah: 2/(1+math.e**-blah)-1
bfunc = lambda blah: 255/(1+math.e**-blah)

class Food(physical.Physical):
	def __init__(self, room, color = [255,0,0], radius = 50, health = 0.5):
		super(Food, self).__init__(room)
		self.color = color
		self.radius = radius
		self.health = health
		self.visual_tag = 1
		self.kind = "food"
		#self.appearance = pygame.Surface((2*self.radius, 2*self.radius))
		#pygame.draw.circle(self.appearance, [int(p) for p in self.color], (int(self.radius), int(self.radius)), int(self.radius))
		#pygame.draw.circle(self.appearance, (255,255,0), (int(self.radius), int(self.radius)), int(self.radius*0.7))
		#pygame.draw.circle(self.appearance, (255,255,255), (int(self.radius), int(self.radius)), int(self.radius*0.4))
		#self.appearance.convert()
		#self.appearance.set_colorkey((0,0,0))

	def findplayer(self,p):
		self.player = p

	def update(self, dt, key_states, key_presses):
		super(Food, self).update(dt, key_states, key_presses)

		if self.radius < 4:
			'''
			b = bee.Bee(r, radius = 5)
			b.xy = f.xy
			b.randomize_color()
			b.findplayer(p)
			r.bees.append(b)
			numbees += 1
			'''
			self.room.food.remove(self)

		if self.stationary:
			return
		#modify velocity
		self.vxy += gravity*dt

		if self.grounded:
			self.vxy -= friction*self.vxy*dt # Friction
		else:
			self.vxy -= airresist*self.vxy*dt # Air resistance

		if abs(self.vxy[0,0]) > maxvelx:
			self.vxy[0,0] *= maxvelx / abs(self.vxy[0,0])

		#if linalg.norm(self.vxy) > maxvel:
		#	self.vxy /= linalg.norm(self.vxy)
		#	self.vxy *= maxvel

		#collision testing and further modification of position and velocity
		self.grounded = 0
		num_deflections = 0
		self.normals = []
		self.project() # This will consume dt
		
		#stay in the box
		self.xy[0,0] = self.xy[0,0]%graphics.world_w
		self.xy[0,1] = self.xy[0,1]%graphics.world_h


	def draw(self, surface):
		super(Food, self).draw(surface)
		ixy = self.xy.astype(int)
		self.radius = max(self.radius, 3)
		for x in range(-1, 2, 1):
			for y in range(-1, 2, 1):
				px = ixy[0,0] + x*graphics.world_w
				py = ixy[0,1] + y*graphics.world_h
				pygame.draw.circle(surface, [int(p) for p in self.color], (px, py), int(self.radius), 2)


		#		surface.blit(self.appearance, (px, py))



		# My velocity
		#endxy = ixy+numpy.round_(self.vxy*10)
		#pygame.draw.line(surface, (255, 255, 0), array(ixy)[0], array(endxy)[0], 1)



