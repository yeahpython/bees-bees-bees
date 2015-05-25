import random
import pygame
import graphics
import math
import collision
from numpy import linalg, matrix, array
import numpy
import test
import itertools
from graphics import bw, bh
from game_settings import *

#gravity = matrix([[0, 0.00001]])
jumpspeed = 0.13
jumpvel = matrix([[0, -jumpspeed]])
maxvel = 1
vert = matrix([[1, 0]])
ignoreinvisible = 1

screencenter = matrix([graphics.screen_w / 2, graphics.screen_h / 2])


def randomize(x, r):
	return x + (random.random()*2 -1)*r

def fixcolor(c):
	c = [int(x) for x in c]
	c = [max(x, 100) for x in c]
	c = [min(x, 255) for x in c]
	return c

class Physical(object):
	def __init__(self, room):
		self.xy = matrix([500,500])
		self.vxy = matrix([[0.,0.]])
		self.grounded = 0 # If not equal to zero, this stores the normal of the side you've been pushed out of...
		self.room = room
		self.randomize_position()
		self.dt = 0 # Think of as time remaining to process information since it changes over the course of a frame.
		self.normals = []
		self.visual_tag = 0
		self.stationary = 0
		self.visible = 0
		self.color = graphics.creature
		self.radius = 0
		self.name = ""
		self.health = 1
		self.objectsinview = []
		self.lastnonwall = 0
		self.updategroundedness = 1

	def randomize_color(self):
		self.color = [randomize(x,2) for x in self.color]
		self.color = fixcolor(self.color)
		#self.color = [int(random.random()*255), int(random.random()*255), int(random.random()*255)]

	def randomize_position(self, dist = 0):
		self.updategroundedness = 1
		for x in range(100):
			if dist:
				self.xy[0,0] += (2*random.random()-1)*dist
				self.xy[0,1] += (2*random.random()-1)*dist
			else:
				r,c = random.choice(self.room.freespots)
				self.xy[0,0] = bw * c
				self.xy[0,1] = bh * r

			self.xy[0,0] = self.xy[0,0] % graphics.world_w
			self.xy[0,1] = self.xy[0,1] % graphics.world_h
			c = int(self.xy[0,0] / bw)
			r = int(self.xy[0,1] / bw)
			if self.room.tiles[c][r].name == "empty":
				break


	def erase(self):
		#if self.name == "Harold":
		#	return
		for x in range(-1, 2, 1):
			for y in range(-1, 2, 1):
				g = pygame.Rect(0,0,self.radius*2,self.radius*2)
				g.centerx = self.xy[0,0] + x*graphics.world_w
				g.centery = self.xy[0,1] + y*graphics.world_h
				self.room.dirtyareas.append(g)

	def update(self, dt, key_states, key_presses):
		x = int(self.xy[0,0]/bw)
		y = int(self.xy[0,1]/bh)
		self.objectsinview = self.room.object_directory[x%graphics.world_tw][y%graphics.world_th]
		for c,r in self.tiles_that_cover_me():
			self.room.object_directory[c%graphics.world_tw][r%graphics.world_th].append(self)
			#test.tiles.append((c,r))

		#if not self.visible and ignoreinvisible:
		#	return
		self.dt = dt
		#if self.vxy[0,1] == 0 and abs(self.vxy[0,0]) < 0.000001 and self.grounded:
		#	self.vxy[0,0] = 0

		#if linalg.norm(self.vxy) == 0:
		#	for n in self.normals:
		#		if linalg.norm(vert - n) == 0:
		#			self.stationary = 1
		#			break
		#else:
		#	self.stationary = 0

	def place(self, position):
		self.xy = position

	def push(self):
		'''uses volume-based methods to remove the physical from surfaces.'''
		prefix = "bee:update:physics:project:push"
		test.add_sticky(prefix)
		test.add_sticky(prefix+":preliminaries")
		#wat
		if not self.grounded or self.vxy[0,0]**2 + self.vxy[0,1]**2 > 0.2:
			self.xy += self.vxy*self.dt
		r = 0
		if self.kind == "player":
			r = -1
			corners = 1
		else:
			r = -1
			corners = 0

		#disp = self.xy- self.room.player.xy
		#if disp[0,0]**2 + disp[0,1]**2 > 332800:
		#	return
		#r = -1
		#corners = 0

		test.remove_sticky(prefix+":preliminaries")
		
		test.add_sticky(prefix+":repel_loop")
		for x,y in self.tiles_that_cover_me(r):
			try:
				c = self.room.convex_directory[x][y]
			except:
				continue
			if c:
				test.add_sticky(prefix+":repel_loop:repel")
				w = c.repel(circle = self, radius = r, corners = corners)
				test.remove_sticky(prefix+":repel_loop:repel")
				if linalg.norm(w) > 0:
					test.tiles.append((x,y))

				self.health -= (linalg.norm(w) + 2) / 1000
				if w[0,1] < -0.1: #and abs(w[0,1]) > 2*abs(w[0,0]):
					self.grounded = 1
					l = linalg.norm(w)
					assert l != 0
					assert not math.isnan(l)
					assert l not in (float('infinity'), -float('infinity'))
					self.normals.append(w / l)
				p1 = (int(self.xy[0,0]), int(self.xy[0,1]) )
				self.xy += w
				p2 = (int(self.xy[0,0]), int(self.xy[0,1]) )
				test.lines.append((p1, p2))
				


				'''test.add_sticky('repel')
				w = c.repel(circle = self, radius = r, corners = corners)
				test.record()
				test.remove_sticky('repel')

				distance = linalg.norm(w)
				if not distance:
					continue
				#self.health -= (distance + 2) / 1000
				if self.kind == "bee" and settings[STICKY_WALLS]:
					if 0 < settings[STICKY_WALLS] < 1:
						self.vxy *= (1 - settings[STICKY_WALLS])

				normalizednormal = w / distance
				if normalizednormal[0,1] < -0.7: #and abs(w[0,1]) > 2*abs(w[0,0]):
					self.grounded = 1
				self.normals.append(normalizednormal)
				self.xy += w '''
		test.remove_sticky(prefix+":repel_loop")
		
		test.remove_sticky(prefix)

	def project(self):
		'''Moves point forward while modifying velocity and grounded information'''
		test.add_sticky('bee:update:physics:project')
		#if self.name == "Harold":
		#	self.xy += self.vxy*self.dt
		#	self.push()
		#	test.remove_sticky('project')
		#	return
		#if not self.visible and ignoreinvisible:
		#	return
		#if self.stationary:
		#	return
		num_deflections = 0
		num_stationary = 0

		self.push()
		test.remove_sticky("bee:update:physics:project")
		
	def tiles_that_cover_me(self, radius = -1):
		if radius < 0:
			radius = self.radius
		myleft = int(self.xy[0,0] - radius) / bw
		myright = int(self.xy[0,0] + radius) / bw
		mytop = int(self.xy[0,1] - radius) / bh
		mybottom = int(self.xy[0,1] + radius) / bh

		return ( (x,y) for x in range(myleft, myright + 1) for y in range(mytop, mybottom + 1))

			
	def draw(self, surface):
		if not self.visible:
			return








