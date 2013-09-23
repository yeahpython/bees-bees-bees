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

#gravity = matrix([[0, 0.00001]])
jumpspeed = 0.13
jumpvel = matrix([[0, -jumpspeed]])
maxvel = 1
vert = matrix([[1, 0]])
ignoreinvisible = 1

screencenter = matrix([graphics.screen_w / 2, graphics.screen_h / 2])


class Physical(object):
	def __init__(self, room):
		self.xy = matrix([500,500])
		self.vxy = matrix([[0.,0.]])
		self.grounded = 0 # If not equal to zero, this stores the normal of the side you've been pushed out of...
		self.room = room
		self.dt = 0 # Think of as time remaining to process information since it changes over the course of a frame.
		self.normals = []
		self.visual_tag = 0
		self.stationary = 0
		self.visible = 0
		self.color = (0,0,0)
		self.topbar = room.topbar
		self.radius = 0
		self.name = ""
		self.health = 1

	def randomize_color(self):
		self.color = (int(random.random()*255), int(random.random()*255), int(random.random()*255) )

	def randomize_position(self, dist = 1):
		self.xy[0,0] += (random.random()*2 - 1)*graphics.world_w*dist
		self.xy[0,1] += (random.random()*2 - 1)*graphics.world_h*dist

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
		test.add_sticky("push")
		self.xy += self.vxy*self.dt
		r = 0
		if self.name == "Harold":
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

		tiles_to_search = self.tiles_that_cover_me(r)
		for x,y in tiles_to_search:
			test.tiles.append((x,y))
			x0 = x# % graphics.world_tw
			y0 = y# % graphics.world_th
			try:
				c = self.room.convex_directory[x0][y0]
			except:
				continue
			if c:
				w = c.repel(circle = self, radius = r, corners = corners)
				self.health -= linalg.norm(w) / 1000
				if w[0,1] < 0: #and abs(w[0,1]) > 2*abs(w[0,0]):
					self.grounded = 1
					self.normals.append(w / linalg.norm(w))
				self.xy += w
		test.record("yeahbuddy")
		test.remove_sticky("push")

	def project(self):
		'''Moves point forward while modifying velocity and grounded information'''
		test.add_sticky('project')
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

		if self.name == "Harold" or 1:
			self.push()
			test.remove_sticky("project")
			return
		

		test.remove_sticky("project")
		
	def tiles_that_cover_me(self, radius = -1):
		if radius < 0:
			radius = self.radius
		tiles_to_search = []
		myleft = (self.xy[0,0] - radius) / bw
		myright = (self.xy[0,0] + radius) / bw
		mytop = (self.xy[0,1] - radius) / bh
		mybottom = (self.xy[0,1] + radius) / bh

		myleft, myright, mytop, mybottom = int(myleft), int(myright), int(mytop), int(mybottom)

		world_tw = graphics.world_w / bw
		world_th = graphics.world_h / bh


		for x in range( myleft, myright + 1):
			for y in range(mytop, mybottom + 1):
				#print y, y%world_th
				#test.tiles.append((x%world_tw, y%world_th))
				tiles_to_search.append( (x, y) )

		return tiles_to_search

			
	def draw(self, surface):
		if not self.visible:
			return








