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
import utils
from game_settings import *


defaultradius = 15
forcefieldradius = 40
killmoderadius = 10

jumpspeed = 0.4
jumpvel = matrix([[0, -jumpspeed]])
maxvel = 0.5
maxvelx = 0.3
groundacc = 0.006
airacc = groundacc * matrix([1,0])
airresist = 0.001
friction = 0.01


class Player(physical.Physical):
	def __init__(self, room):
		super(Player, self).__init__(room)
		self.radius = defaultradius
		self.walkingspeed = defaultradius / 15 * 0.04
		self.forcefield = forcefieldradius
		self.color = [x for x in graphics.creature]
		self.counter = 0
		self.counter2 = 0
		self.losinghealth = 0
		self.visual_tag = 1000000
		self.health = 1
		self.lifetime = 0
		self.name = "Harold"
		self.killmode = 0
		self.kind = "player"
		self.place(self.room.start_position)
		self.room.player = self
		self.feetSupported = 0
		self.lefta = 0.5
		self.righta = 0.5
		self.beepushes = []
		self.offset = matrix([0.0,0.0])
		self.displaycolor = [x for x in self.color]
		self.grounded = 0
		self.automaticEvasion = 0
		self.jetpackfuel = 0

	def maybe_die(self):
		if self.radius < 10:
			self.radius = defaultradius
			self.topbar.flash("You died!!!")
			#self.topbar.data.append(self.lifetime)
			#self.topbar.data.append(self.radius)
			self.randomize_position()
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
		

		if key_states[pygame.K_UP]:
			if self.feetSupported:
				self.jetpackfuel = 200
				self.vxy += jumpvel

			if self.jetpackfuel:
				jv = jumpvel / 50
				consumedfuel = min(dt, self.jetpackfuel)
				self.vxy += jv * consumedfuel
				self.jetpackfuel -= consumedfuel
				if self.jetpackfuel < 0:
					self.jetpackfuel = 0
		else:
			self.jetpackfuel = 0

		#modify velocity
		'''
		if key_states[pygame.K_UP] and self.grounded:
			#jv = jumpspeed * self.normals[0] * -1
			jv = jumpvel#jumpspeed * self.normals[0]
			self.vxy += jv# jumpspeed*matrix(self.testvectors[0])/linalg.norm(self.testvectors[0])#jumping
		'''
		#if key_states[pygame.K_DOWN]:
		#	jv = jumpspeed * self.normals[0]
		#	self.vxy += jv# jumpspeed*matrix(self.testvectors[0])/linalg.norm(self.testvectors[0])#jumping
		#if key_states[pygame.K_DOWN]:
			#self.vxy -= jumpvel

		self.vxy += matrix([[0, settings[GRAVITY]]])*38/6*dt


		if key_states[pygame.K_SPACE]:
			self.randomize_position()

		if key_states[pygame.K_g]:
			#self.topbar.flash("Generating bees!")
			self.room.generate_bees(1)

		'''add kill mode'''
		allowkillmode = False
		'''
		if allowkillmode:
			if key_states[pygame.K_z]:
				self.killmode = 1
				self.radius = killmoderadius
			else:
				self.killmode = 0
				self.radius = defaultradius
		'''

		self.feetSupported = self.grounded
		
		'''
		if self.feetSupported and not (key_states[pygame.K_LEFT] or key_states[pygame.K_RIGHT] or key_states[pygame.K_UP]):
			self.vxy *= (1-friction)**dt # Friction
			self.vxy *= 0
			if key_states[pygame.K_LEFT]      : self.vxy += groundacc*self.normals[0]*matrix([[0, -1],[1, 0]])*dt# Left # used to be 
			elif key_states[pygame.K_RIGHT]   : self.vxy += groundacc*self.normals[0]*matrix([[0, 1],[-1, 0]])*dt# Right
		else:
			self.vxy -= airresist*self.vxy*dt*linalg.norm(self.vxy) # Air resistance
			if key_states[pygame.K_LEFT]     : self.vxy -= airacc*dt# Left 
			elif key_states[pygame.K_RIGHT]  : self.vxy += airacc*dt# Right
		'''
		
		if self.feetSupported:
			if key_states[pygame.K_LEFT]:
				if self.normals:
					self.vxy += groundacc*self.normals[0]*matrix([[0, -1],[1, 0]])*dt# Left # used to be
				else:
					self.vxy += groundacc*matrix([-1, 0])*dt
			elif key_states[pygame.K_RIGHT]:
				if self.normals:
					self.vxy += groundacc*self.normals[0]*matrix([[0, 1],[-1, 0]])*dt# Right
				else:
					self.vxy += groundacc*matrix([1, 0])*dt
			elif not self.beepushes or key_states[pygame.K_UP]:
				self.vxy *= 0.2
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
		#if self.grounded:
		#	if self.beepushes or (key_states[pygame.K_LEFT] or key_states[pygame.K_RIGHT] or key_states[pygame.K_UP]):
		#		self.grounded = 0
		self.grounded = 0
		num_deflections = 0
		self.normals = []
		self.project() # This will consume dt
		
		#stay in the box
		self.xy[0,0] = self.xy[0,0]%graphics.world_w
		self.xy[0,1] = self.xy[0,1]%graphics.world_h

		c = int(self.xy[0,0] / bw)
		r = int(self.xy[0,1] / bh)
		if self.room.tiles[c][r].name == "wall":
			if (self.lastnonwall == 0):
				self.randomize_position(10)
			else:
				c0, r0 = self.lastnonwall
				self.xy[0,0] = (c0 + 0.5) * bw
				self.xy[0,1] = (r0 + 0.5) * bh
				self.vxy *= 0.5
		else:
			self.lastnonwall = c, r

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
		if self.losinghealth:
			self.walkingspeed = self.radius / 15 * 0.04
			self.displaycolor[0] = 0.9 * self.displaycolor[0] + 0.1 * 255
			self.displaycolor[1] = 0.9 * self.displaycolor[1]
			self.displaycolor[2] = 0.9 * self.displaycolor[2]
			#self.color[0] = 255
		else:
			self.displaycolor[0] = 0.9 * self.displaycolor[0] + 0.1 * self.color[0]
			self.displaycolor[1] = 0.9 * self.displaycolor[1] + 0.1 * self.color[1]
			self.displaycolor[2] = 0.9 * self.displaycolor[2] + 0.1 * self.color[2]

		color = [int(x) for x in self.displaycolor]

		#if self.counter >= self.radius - 10:
		#	if self.radius < 20:
		#		color = [255, 200, 0]
		#	if self.counter >= self.radius:
		#		self.counter -= self.radius
		ixy = self.xy.astype(int)




		for x,y in utils.body_copies(self.xy, self.radius):
			px = ixy[0,0] + x*graphics.world_w
			py = ixy[0,1] + y*graphics.world_h
			#pygame.draw.circle(surface, [180,255,255], (px, py), int(self.radius), 1)

			pi = 3.1415926

			'''shoulders'''
			shouldershift = 0#max(min(int(10*self.vxy[0,0]), 10), -10)
			shoulderx = px + shouldershift
			shouldery = py - int(self.radius*0.7)
			if self.losinghealth:
				if self.beepushes:
					n = random.choice(self.beepushes)
					self.offset += n * 0.5
			
			self.offset *= 0.95

			for i in range(2):
				if self.offset[0,i] > 5:
					self.offset[0,i] = 5
				if self.offset[0,i] < -5:
					self.offset[0,i] = -5

			offsetx = int(self.offset[0,0])
			offsety = int(self.offset[0,1])

			self.beepushes = []

			shoulderx += offsetx
			shouldery += offsety
			
			shoulders = (shoulderx, shouldery)

			'''head'''
			headx = shoulderx
			heady = shouldery-int(self.radius*0.1)
			#headx -= offsetx/2
			#heady -= offsety/2

			head = int(headx), int(heady)
			pygame.draw.circle(surface, color, head, int(self.radius*0.2), 0)

			'''groin'''
			groinx = px
			groiny = py+int(self.radius*0.1)

			groinx += offsetx / 2
			groiny += offsety

			groin = (groinx, groiny)

			'''neck'''
			pygame.draw.line(surface, color, head, shoulders, 2)

			'''torso'''
			pygame.draw.line(surface, color, shoulders, groin, 2)


			'''right leg'''
			rightfootx = px + 0.4*self.radius - 3 * self.vxy[0,0] * self.radius
			rightfooty = py+int(self.radius) + 0.1*self.radius
			rightfootx = px + 0.4*self.radius*math.cos(self.walkingspeed*pi*self.xy[0,0])
			if abs(self.vxy[0,0]) > 0.01:
				rightfooty = py+int(self.radius)
				step = 0.1*self.radius*math.sin(self.walkingspeed*pi*self.xy[0,0])
				if step < 0:
					step *= abs(self.offset[0,1]*5 + 1)
					rightfooty += step
			rightfoot = rightfootx, rightfooty
			pygame.draw.line(surface, color, groin, rightfoot, 2)
			#pygame.draw.line(surface, color, (px,py+int(self.radius*0.2)), (px + self.radius*math.cos(0.4*pi), py+inself.radius*math.sin(0.4*pi)), 1)

			'''left leg'''
			leftfootx = px - 0.4*self.radius - 3 * self.vxy[0,0] * self.radius
			leftfooty = py+int(self.radius) + 0.1*self.radius
			leftfootx = px - 0.4*self.radius*math.cos(self.walkingspeed*pi*self.xy[0,0])
			if abs(self.vxy[0,0]) > 0.01:
				leftfooty = py+self.radius
				step = - 0.1*self.radius*math.sin(self.walkingspeed*pi*self.xy[0,0])
				if step < 0:
					step *= abs(self.offset[0,1]*5 + 1)
					leftfooty += step
			leftfooty = int(leftfooty)
			leftfoot = leftfootx, leftfooty
			pygame.draw.line(surface, color, groin, leftfoot, 2)

			rightpoint = px + 0.8 * self.radius, py + 0.8 * self.radius
			leftpoint = px - 0.8 * self.radius, py + 0.8 * self.radius

			rightpoint, leftpoint = [int(x) for x in rightpoint], [int(x) for x in leftpoint]

			#self.feetSupported = self.room.pointcheck(leftfoot) or self.room.pointcheck(rightfoot) or self.room.pointcheck(rightpoint) or self.room.pointcheck(leftpoint)
			#print "feet supported:", self.feetSupported

			''''right arm'''
			#howfar = 0.3
			#if self.vxy[0,0] >= 0:
			#	howfar = 0.3 - 2.3 * (self.vxy[0,0])
			#self.righta = 0.9 * self.righta + 0.1 * howfar
			#pygame.draw.line(surface, color, shoulders, (px + 0.7*self.radius*math.cos(self.righta*pi), py+0.7*self.radius*math.sin(self.righta*pi)), 2)
			
			righthandx = shoulderx + 0.4*self.radius * math.cos(self.walkingspeed*pi*self.xy[0,0]) * (0.2+min(abs(self.vxy[0,0]), 0.1))**0.5 * 2
			righthandy = shouldery + self.radius
			righthandy -= abs(int(self.offset[0,1] * 5))
			righthand = (righthandx, righthandy)
			pygame.draw.line(surface, color, shoulders, righthand, 2)

			'''left arm'''
			#howfar = 0.7
			#if self.vxy[0,0] <= 0:
			#	howfar = 0.7 - 2.3 * (self.vxy[0,0])
			#self.lefta = 0.9 * self.lefta + 0.1 * howfar
			#pygame.draw.line(surface, color, shoulders, (px + 0.7*self.radius*math.cos(self.lefta*pi), py+0.7*self.radius*math.sin(self.lefta*pi)), 2)
			
			lefthandx = shoulderx - 0.4*self.radius * math.cos(self.walkingspeed*pi*self.xy[0,0]) * (0.2+min(abs(self.vxy[0,0]), 0.1))**0.5 * 2
			lefthandy = shouldery + self.radius
			lefthandy -= abs(int(self.offset[0,1] * 5))
			lefthand = (lefthandx, lefthandy)
			pygame.draw.line(surface, color, shoulders, lefthand, 2)

			ffcolor = [255, 255, 255]
			#if self.losinghealth:
			#	ffcolor = [255, 0, 0]

			'''force field'''
			'''if self.losinghealth:
				pygame.draw.circle(surface, self.displaycolor, (px, py), int(self.forcefield), 1)
				'''

			#pygame.draw.circle(surface, [255,255,0], (px, py), int(self.radius), 1)

			#centercolor = [0, 0, 0]
			#if self.losinghealth:
			#	centercolor = [255, 200, 0]
			#pygame.draw.circle(surface, centercolor, (px, py), int(0.1*self.radius))

		# My velocity
		#endxy = ixy+numpy.round_(self.vxy*10)
		#pygame.draw.line(surface, (255, 255, 0), array(ixy)[0], array(endxy)[0], 1)
		test.remove_sticky('player')
		self.losinghealth = 0








