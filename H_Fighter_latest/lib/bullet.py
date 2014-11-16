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
	def __init__(self, bee, player, room, direction = matrix([random.random()*2-1,random.random()*2-1]) ):
		super(Bullet, self).__init__(room)

		self.visual_tag = 1
		if linalg.norm(direction) == 0:
			direction = matrix([random.random()*2-1,random.random()*2-1])
		self.vxy = direction
		if linalg.norm(self.vxy) < 0.1:
			self.vxy /= linalg.norm(self.vxy)
			self.vxy *= 0.1
		self.initialspeed = linalg.norm(self.vxy)
		self.bee = bee
		self.player = player
		self.randomize_position()
		self.radius = 8
		self.kind = "bullet"

	def disappear(self):
		try:
			self.room.bullets.remove(self)
		except:
			print "tried to disappear but I wasn't in the room's list"

	def hit_player(self):
		if linalg.norm(self.xy - self.player.xy) < self.radius + self.player.radius:
			self.player.randomize_color()
			try:
				self.bee.health = 1.0
				self.bee.score += 1
			except:
				print "aww, I'm a bullet that hit the player but my bee died"
			self.disappear()

	def hit_bee(self,b):
		if self.bee != b:
			if linalg.norm(b.xy - self.xy) < b.radius + self.radius:
				b.health -= 0.1

	def update(self, dt, key_states, key_presses):
		super(Bullet, self).update(dt, key_states, key_presses)

		for phys in self.objectsinview:
			if phys.kind == "player":
				self.hit_player()
			if phys.kind == "bee":
				self.hit_bee(phys)

		#collision testing and further modification of position and velocity
		self.xy += self.vxy * self.dt
		
		#stay in the box
		self.xy[0,0] = self.xy[0,0]%graphics.world_w
		self.xy[0,1] = self.xy[0,1]%graphics.world_h

		x = (self.xy[0,0] / bw)%world_tw
		y = (self.xy[0,1] / bh)%world_th
		if self.room.tiles[x][y].name != 'empty':
			self.disappear()


	def draw(self, surface):
		super(Bullet, self).draw(surface)
		ixy = self.xy.astype(int)
		self.radius = max(self.radius, 3)
		for x in range(-1, 2, 1):
			for y in range(-1, 2, 1):
				px = ixy[0,0] + x*graphics.world_w
				py = ixy[0,1] + y*graphics.world_h

				try:
					disp = self.vxy / linalg.norm(self.vxy) * self.radius * 0.9
					start = (self.xy+disp)[0,0], (self.xy + disp)[0,1]
					end = (self.xy-disp)[0,0], (self.xy-disp)[0,1]
					print start, end
					pygame.draw.line(surface, [255,0,0], start, end, 5)
				except:
					pygame.draw.circle(surface, [255,20,50], (px, py), self.radius)


		#		surface.blit(self.appearance, (px, py))



		# My velocity
		#endxy = ixy+numpy.round_(self.vxy*10)
		#pygame.draw.line(surface, (255, 255, 0), array(ixy)[0], array(endxy)[0], 1)



