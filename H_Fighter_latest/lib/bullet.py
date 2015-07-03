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
from graphics import bw, bh, world_tw, world_th


class Bullet(physical.Physical):
	def __init__(self, player, room, direction = matrix([1.0]) ):
		super(Bullet, self).__init__(room)

		self.visual_tag = 1
		if linalg.norm(direction) == 0:
			print "randomized direction"
			direction = matrix([random.random()*2-1,random.random()*2-1])
		self.vxy = direction
		if linalg.norm(self.vxy) < 0.1:
			self.vxy /= linalg.norm(self.vxy)
			self.vxy *= 0.1
		self.initialspeed = linalg.norm(self.vxy)
		self.player = player
		self.randomize_position()
		self.radius = 20
		self.kind = "bullet"
		self.age = 0
		print "bullet initiated!"

	def disappear(self):
		print "bullet disappearing"
		try:
			self.room.bullets.remove(self)
		except:
			print "tried to disappear but I wasn't in the room's list"

	def hit_player(self):
		if linalg.norm(self.xy - self.player.xy) < self.radius + self.player.radius:
			self.player.randomize_color()
			self.disappear()

	def hit_bee(self,b):
		b.health -= 2
		b.die()

	def update(self, dt, key_states, key_presses):
		super(Bullet, self).update(dt, key_states, key_presses)
		self.age += dt
		if self.age > 10000:
			self.disappear()

		for phys in self.objectsinview:
			#if phys.kind == "player":
			#	self.hit_player()
			if phys.kind == "bee":
				self.hit_bee(phys)

		#collision testing and further modification of position and velocity
		self.xy += self.vxy * self.dt
		
		#stay in the box
		self.xy[0,0] = self.xy[0,0]%graphics.world_w
		self.xy[0,1] = self.xy[0,1]%graphics.world_h

		if self.room.pointcheck((int(self.xy[0,0]), int(self.xy[0,1]))):
			self.disappear()


	def draw(self, surface):
		super(Bullet, self).draw(surface)
		ixy = self.xy.astype(int)
		self.radius = max(self.radius, 3)
		for x in range(-1, 2, 1):
			for y in range(-1, 2, 1):
				px = ixy[0,0] + x*graphics.world_w
				py = ixy[0,1] + y*graphics.world_h

				
				pygame.draw.circle(surface, [0,255,50], (px, py), self.radius, 1)
				try:
					disp = self.vxy / linalg.norm(self.vxy) * self.radius * 0.9
					start = (self.xy+disp)[0,0], (self.xy + disp)[0,1]
					end = (self.xy-disp)[0,0], (self.xy-disp)[0,1]
					pygame.draw.line(surface, [255,0,0], start, end, 5)
				except:
					pass


		#		surface.blit(self.appearance, (px, py))



		# My velocity
		#endxy = ixy+numpy.round_(self.vxy*10)
		#pygame.draw.line(surface, (255, 255, 0), array(ixy)[0], array(endxy)[0], 1)



