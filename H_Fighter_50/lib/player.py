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
import messages



defaultradius = 40
killmoderadius = 10



gravity = matrix([[0, 0.0006]]) # was 0.0006
jumpspeed = 0.4
jumpvel = matrix([[0, -jumpspeed]])
maxvel = 0.5
maxvelx = 0.3
groundacc = 0.0006
airacc = groundacc * matrix([1,0])
airresist = 0.001
friction = 0.001

class Player(physical.Physical):
	def __init__(self, room):
		super(Player, self).__init__(room)
		self.radius = defaultradius
		self.color = [51, 255, 204]
		self.counter = 0
		self.counter2 = 0
		self.losinghealth = 0
		self.visual_tag = 1000000
		self.health = 1
		self.lifetime = 0
		self.name = "Harold"
		self.killmode = 0
		self.kind = "player"

	def maybe_die(self):
		# Player death. Draw some things at the top of the screen.
		if self.counter % 10 == 0:
			self.topbar.flash("decreasing radius")
			#self.topbar.data.append(self.lifetime)
			#self.topbar.data.append(self.radius)
			#self.randomize_position(0)
			#self.randomize_color()
			self.lifetime = 0
			#self.radius = 40
			#self.prevrad = 40

	def update(self, dt, key_states, key_presses):
		test.add_sticky('player')
		super(Player, self).update(dt, key_states, key_presses)

		self.maybe_die()

		for phys in self.objectsinview:
			if phys.kind == "bullet":
				phys.hit_player()
			elif phys.kind == "bee":
				phys.eat_player()

		self.lifetime += 1
		#self.radius *= 1.001
		#self.radius = self.radius*0.92 + 40*0.08

		bw = graphics.bw
		bh = graphics.bh


		myleft = (self.xy[0,0] - self.radius) / bw
		myright = (self.xy[0,0] + self.radius) / bw
		mytop = (self.xy[0,1] - self.radius) / bh
		mybottom = (self.xy[0,1] + self.radius) / bh

		myleft, myright, mytop, mybottom = int(myleft), int(myright), int(mytop), int(mybottom)


		self.counter += 1
		self.counter2 += 1

		#modify velocity
		if key_states[pygame.K_UP] and self.grounded:
			#jv = jumpspeed * self.normals[0] * -1
			jv = jumpvel#jumpspeed * self.normals[0]
			self.vxy += jv# jumpspeed*matrix(self.testvectors[0])/linalg.norm(self.testvectors[0])#jumping
		#if key_states[pygame.K_DOWN]:
		#	jv = jumpspeed * self.normals[0]
		#	self.vxy += jv# jumpspeed*matrix(self.testvectors[0])/linalg.norm(self.testvectors[0])#jumping
		#if key_states[pygame.K_DOWN]:
			#self.vxy -= jumpvel
		self.vxy += gravity*dt

		if key_states[pygame.K_SPACE]:
			self.randomize_position()

		if key_states[pygame.K_z]:
			self.killmode = 1
			self.radius = killmoderadius
		else:
			self.killmode = 0
			self.radius = defaultradius

		
		if self.grounded:
			self.vxy -= friction*self.vxy*dt # Friction
			if key_states[pygame.K_LEFT]      : self.vxy += groundacc*self.normals[0]*matrix([[0, -1],[1, 0]])*dt# Left # used to be 
			elif key_states[pygame.K_RIGHT]   : self.vxy += groundacc*self.normals[0]*matrix([[0, 1],[-1, 0]])*dt# Right
		else:
			self.vxy -= airresist*self.vxy*dt*linalg.norm(self.vxy) # Air resistance
			if key_states[pygame.K_LEFT]     : self.vxy -= airacc*dt# Left 
			elif key_states[pygame.K_RIGHT]  : self.vxy += airacc*dt# Right
		

		#if abs(self.vxy[0,0]) > maxvelx:
		#	self.vxy[0,0] *= maxvelx / abs(self.vxy[0,0])

		if linalg.norm(self.vxy) > maxvel:
			self.vxy /= linalg.norm(self.vxy)
			self.vxy *= maxvel

		#collision testing and further modification of position and velocity
		self.grounded = 0
		num_deflections = 0
		self.normals = []
		self.project() # This will consume dt
		
		#stay in the box
		self.xy[0,0] = self.xy[0,0]%graphics.world_w
		self.xy[0,1] = self.xy[0,1]%graphics.world_h
		test.remove_sticky('player')

	def eat(self, food):
		for f in food:
			if linalg.norm(f.xy - self.xy) < f.radius + self.radius:
				f.radius -= 2
				self.radius +=0.1
				f.vxy += (f.xy - self.xy)/linalg.norm(f.xy - self.xy)

	def draw(self, surface):
		test.add_sticky('player')

		super(Player, self).draw(surface)
		color = [0,0,0]
		print self.losinghealth
		if self.losinghealth:
			color = [255,0,0]
		else:
			color = self.color
		self.losinghealth = 0

		#if self.counter >= self.radius - 10:
		#	if self.radius < 20:
		#		color = [255, 200, 0]
		#	if self.counter >= self.radius:
		#		self.counter -= self.radius
		ixy = self.xy.astype(int)
		if self.radius < 10:
			self.radius = 10
		for x in range(-1, 2, 1):
			for y in range(-1, 2, 1):
				px = ixy[0,0] + x*graphics.world_w
				py = ixy[0,1] + y*graphics.world_h
				#pygame.draw.circle(surface, [180,255,255], (px, py), int(self.radius), 1)
				if 1:#self.grounded:
					w = 0
				else:
					w = 2
				pi = 3.1415926
				pygame.draw.circle(surface, color, (px, py-int(self.radius*0.7)), int(self.radius*0.3), w)

				#body
				pygame.draw.line(surface, color, (px,py-int(self.radius*0.6)), (px, py+int(self.radius*0.2)), 1)

				#right leg
				pygame.draw.line(surface, color, (px,py+int(self.radius*0.2)), (px + self.radius*math.cos(0.4*pi), py+self.radius*math.sin(0.4*pi)), 1)
				
				#left leg
				pygame.draw.line(surface, color, (px,py+int(self.radius*0.2)), (px + self.radius*math.cos(0.6*pi), py+self.radius*math.sin(0.6*pi)), 1)
				
				#right arm
				pygame.draw.line(surface, color, (px,py-int(self.radius*0.2)), (px + self.radius*math.cos(0.1*pi), py+self.radius*math.sin(0.1*pi)), 1)
				
				#left arm
				pygame.draw.line(surface, color, (px,py-int(self.radius*0.2)), (px + self.radius*math.cos(0.9*pi), py+self.radius*math.sin(0.9*pi)), 1)
				#pygame.draw.circle(surface, [0,0,0], (px, py), int(self.radius), 0)
				#pygame.draw.circle(surface, [55,255,155], (px, py), int(self.radius*0.5), 0)

				#centercolor = [0, 0, 0]
				#if self.losinghealth:
				#	centercolor = [255, 200, 0]
				#pygame.draw.circle(surface, centercolor, (px, py), int(0.1*self.radius))

		# My velocity
		#endxy = ixy+numpy.round_(self.vxy*10)
		#pygame.draw.line(surface, (255, 255, 0), array(ixy)[0], array(endxy)[0], 1)
		test.remove_sticky('player')








