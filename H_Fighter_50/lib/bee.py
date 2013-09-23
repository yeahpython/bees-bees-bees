import random
import pygame
import graphics
import math
import collision
from numpy import linalg, matrix, array
import numpy
import test
import itertools
import random
import time
import copy
import bullet

import food
import physical
import brain

num_best_bees = 10

'''normal mode
gravity = matrix([[0, 0.0006]])
jumpspeed = 0.4
jumpvel = matrix([[0, -jumpspeed]])
maxvel = 0.5
maxvelx = 0.3
groundacc = 0.02
airacc = 0.02
airresist = 0.0000001
friction = 0.001
'''

'''flying'''
gravity = matrix([[0, 0.0006]]) # was 0.0006
jumpspeed = 0.05
jumpvel = matrix([[0, -jumpspeed]])
maxvel = 0.5
maxvelx = 0.3
groundacc = 0.001
yogroundacc = matrix([[groundacc, 0]])
airacc = 0.0001
airresist = 0.000002
friction = 0.0000001
speed_decay = 0.998
healthlossrate = 0.000001

#afunc = lambda blah: 2/(1+math.e**-blah)-1
#bfunc = lambda blah: 255/(1+math.e**-blah)

consonants = "qwrrrtttypssssssdfffgggghhhhjlzxccccvbbbbbnnnmmm"
vowels = "eeuiiiooaaa"
splits = "-"

bw = graphics.bw
bh = graphics.bh


class Bee(physical.Physical):
	def __init__(self, room, prebrain = None, color = [128,128,128], radius = 14, health = 1):
		super(Bee, self).__init__(room)
		if prebrain != None:
			self.brain = prebrain
		else:
			self.brain = brain.Brain(12, [30, 5])
		self.color = color
		self.radius = radius
		self.health = health
		self.visual_tag = -1
		self.eyes = [(1, 0), (1, 1), (0, 1), (-1, 0), (1, -1), (-1, 1), (-1, -1), (0, -1)]
		self.responsetime = 30
		self.timesincelastthought = random.random()*self.responsetime
		self.up = 0
		self.leftright = 0

		self.name = ""
		self.randomize_name()
		self.children = 0
		self.ancestry = ""
		self.score = 0
		self.player = "lol"
		self.room.beehistory += 1
		self.bullets = []
		self.timesincelastshot = 0
		self.kind = "bee"
		self.husk = 0
		#self.a = 1

	def update(self, dt, key_states, key_presses):
		
		fullname = self.name + self.ancestry
		test.add_sticky('bee')
		super(Bee, self).update(dt, key_states, key_presses)
		test.record("physical inherited update")

		self.timesincelastshot += dt

		#for b in self.bullets:
		#	b.update(dt, key_states, key_presses)

		
		self.update_health(dt)
		self.considergivingbirth()

		if not self.husk:

			for p in self.objectsinview:
				if p.kind == "bullet":
					p.hit_bee(self)
				elif p.kind == "player":
					self.eat_player()


			self.timesincelastthought += dt

			test.record("health, birth, eating")

			if self.timesincelastthought > self.responsetime:
				self.timesincelastthought -= self.responsetime

				c = int(self.xy[0,0] / bw)
				r = int(self.xy[0,1] / bw)
				infoz = self.room.visiondirectory[c%graphics.world_tw][r%graphics.world_th]
				del c
				del r
				test.record("looking about")

				#go = time.time()
				#t = [math.sin(go), math.sin(go/2.3), math.sin(go)%1.5]
				
				disp_to_p = self.player.xy - self.xy
				dispx = disp_to_p[0,0]/graphics.world_w
				dispy = disp_to_p[0,1]/graphics.world_h

				if dispx > 0.5:
					dispx -= 1
				if dispx < -0.5:
					dispx += 1
				if dispy > 0.5:
					dispy -= 1
				if dispy < -0.5:
					dispy += 1
				disps = [dispx, dispy]

				inputs = disps + [self.health] + infoz #+ playerinputs + t
						#2		#1		  # 9

				test.record("displacements")

				outputs = self.brain.compute(inputs)
				test.record("thinking")

				processedoutputs = [x for x in outputs]
				self.up = outputs[0]
				#down = outputs[1]
				self.leftright = outputs[1]
				if outputs[2] > 0 and self.timesincelastshot > 1000 and 1==0:
					self.timesincelastshot = 0
					direction = matrix([outputs[3],outputs[4]])
					direction = disp_to_p
					direction /= linalg.norm(direction)
					b = bullet.Bullet(self, self.player, self.room, direction * outputs[2] * 2)
					b.xy = self.xy + matrix([0,0])
					self.room.bullets.append(b)
					self.health -= 0.05

				

			
			self.vxy += gravity*dt


			if 1: #self.grounded:
				self.vxy += self.up*jumpvel
				self.vxy *= speed_decay**dt
				#self.vxy -= friction*self.vxy*dt # Friction
				#self.vxy += self.leftright*self.normals[0]*matrix([[0, -1],[1, 0]])*dt*groundacc
				self.vxy += self.leftright*yogroundacc*dt
			else:
				self.vxy *= speed_decay**dt
				self.vxy[0,0] += self.leftright*airacc# Left


			#if abs(self.vxy[0,0]) > maxvelx:
			#	print self.vxy, "has too much horizontal"
			#	self.vxy[0,0] *= maxvelx / abs(self.vxy[0,0])

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
		self.age()

		test.record()
		test.remove_sticky('bee')

	def randomize_name(self):
		self.name = ""
		l = random.choice([6,7,8,9])
		for k in range(l, 0, -1):
			if k != 1 and k!= l:
				if random.random() > 0.9:
					self.name += random.choice(splits)
					continue
				elif random.random() > 0.7:
					continue
			if k%2 == 0:
				self.name += random.choice(consonants)
			else:
				self.name += random.choice(vowels)

	def age(self):
		if not self.husk:
			if self.health < 0:
				self.die()
		if self.husk:
			self.husk += 1
		if self.husk > 10:
			try:
				self.room.bullets = [b for b in self.room.bullets if b.bee != self]
				self.room.bees.remove(self)
			except:
				pass


	def eat_player(self):
		disp = self.xy - self.player.xy
		dist = disp[0,0]**2 + disp[0,1]**2
		if dist < (self.radius + self.player.radius)**2:
			if self.player.killmode:
				self.die()
			#self.player.randomize_color()
			#self.player.radius -=10
			
			p = disp * (dist+0.1)**(-2) * 300
			if p[0,0] > 0:
				self.player.grounded = 1
				self.player.normals.append(-p / linalg.norm(p))

			self.player.vxy -= p
			self.health += 0.5
			#self.score += 1

			# Fun with bestbees
			if self not in self.room.bestbees:
				if len(self.room.bestbees) < num_best_bees:
					self.room.bestbees.append(self)
				elif min([foo.score for foo in self.room.bestbees]) < self.score:
					self.room.bestbees.append(self)
					self.room.bestbees.sort(key = lambda x: x.score)
					self.room.bestbees = self.room.bestbees[-num_best_bees:]

	def update_health(self, dt):
		self.health -= healthlossrate*dt
		#self.health += (1-((self.xy[0,0] - self.player.xy[0,0])/graphics.world_w)**2 )*2*healthlossrate * dt
		if self.normals:
			self.health -= self.room.acid
		if self.health > 1:
			self.health = 1

	def considergivingbirth(self):
		if self.health > 0.9 and random.random() > 0.3 and len(self.room.bees) < self.room.beecap:
			self.health -= 0.2
			self.children += 1
			newbee = Bee(self.room, copy.deepcopy(self.brain), self.color, self.radius)
			newbee.mutate()
			newbee.brain.randomizenodes()
			newbee.place(self.xy + matrix([0,0]))#mimic position
			#newbee.randomize_position(0.3)#randomize position
			newbee.findplayer(self.player)
			newbee.name = self.name
			newbee.ancestry = self.ancestry + "." + str(self.children)
			#print newbee.name + newbee.ancestry + "has been born"
			self.room.bees.append(newbee)

	def eat(self, food):
		for f in food:
			disp = f.xy - self.xy
			if disp[0,0]**2 + disp[0,1]**2 < (f.radius + self.radius)**2:
				self.health += 0.2
				f.radius -= 10
				f.vxy += (f.xy - self.xy)*0.1

	def fight(self, prey):
		if self != prey:
			disp = self.xy - prey.xy
			if disp[0,0]**2 + disp[0,1]**2 < (self.radius + prey.radius)**2:
				prey_to_self = linalg.norm(self.vxy) / 1000000
				prey.health -= prey_to_self
				self.health += prey_to_self
				self.health = min(self.health, 1)

	def mutate(self):
		self.brain.mutate()
		newcolor = []
		for p in self.color:
			p += random.random()*50 - 25
			p = max(p, 0)
			p = min(p, 255)
			newcolor.append(p)
		self.color = newcolor
		self.eyes = [(x+random.random() - 0.5, y + random.random() - 0.5) for x,y in self.eyes]

	def findplayer(self,p):
		self.player = p

	def die(self):
		'''
		f = food.Food(self.room)
		f.place(self.xy)
		f.vxy = self.vxy
		f.findplayer(self.player)
		f.color = self.color
		self.room.food.append(f)
		'''
		if not self.husk:
			self.husk = 1
			#self.radius *= 2

	def draw(self, surface):
		#for b in self.bullets:
		#	b.draw(surface)
		fullname = self.name + self.ancestry
		test.add_sticky('bee')
		super(Bee, self).draw(surface)
		ixy = self.xy.astype(int)
		for x in range(-1, 2, 1):
			for y in range(-1, 2, 1):
				px = ixy[0,0] + x*graphics.world_w
				py = ixy[0,1] + y*graphics.world_h
				c = self.color
				#if self.husk:
				#	c = [255,0,255]
				pygame.draw.circle(surface, c, (px, py), int(self.radius))
				#pygame.draw.circle(surface, [int(p) for p in self.color], (px, py), int(self.radius))
				centercolor = [0,0,0]
				rad = int(self.radius*(1-self.health))
				rad = max( rad, 0)
				if not self.husk:			
					pygame.draw.circle(surface, [int(p) for p in centercolor], (px, py), rad)



		# My velocity
		#endxy = ixy+numpy.round_(self.vxy*10)
		#pygame.draw.line(surface, (255, 255, 0), array(ixy)[0], array(endxy)[0], 1)
		test.record('placeholder')
		test.remove_sticky('bee')


def look2(room, my_x, my_y, vx, vy, dt = 1.0, bw = graphics.bw, bh = graphics.bh):
	'''returns ALL tiles that cover the path, even by just an edge or point.'''
	# Trivial case where either vx or vy is zero
	if vx == 0 or vy == 0:
		for x,y in collision.find_tiles_rect(my_x, my_y, vx, vy, dt, bw, bh):
			# Life
			if  0 <= x < graphics.world_w / bw and 0 <= y < graphics.world_h / bh and room.object_directory[x][y]:
				return (x,y), room.object_directory[x][y]
			# Wall
			elif 0 <= x < graphics.world_w / bw and 0 <= y < graphics.world_h / bh and room.tiles[x][y].name != 'empty':
				return (x,y), -1
		else:
			return 0

	# If the above if statement is false we may assume vx != 0 and vy != 0

	# Find the starting position
	x = int(math.floor(my_x / bw))
	y = int(math.floor(my_y / bh))

	coordlist = [] # Include everthing touching the starting point.

	xstep = int(math.copysign(1,vx))
	ystep = int(math.copysign(1,vy))

	newtiles = []
	while dt >= 0 and len(newtiles) < 100:# and 0 <= my_x <= graphics.world_w and 0 <= my_y <= graphics.world_h:
		#my_x %= graphics.world_w
		#my_y %= graphics.world_h
		# Set x to next
		if xstep > 0:
			x_to_next = (x + 1)*bw - my_x
		else:
			x_to_next = x*bw - my_x
		if vx == 0: # With current setting this is never going to happen, so this really is optional.
			t_next_x = float('infinity'); print "Hey, vx isn't supposed to be zero"
		else:
			t_next_x = x_to_next / vx

		if ystep > 0:
			y_to_next = (y + 1)*bw - my_y
		else:
			y_to_next = y*bw - my_y
		if vy == 0: # With current setting this is never going to happen, so this really is optional.
			t_next_y = float('infinity'); print "Hey, vy isn't supposed to be zero"
		else:
			t_next_y = y_to_next / vy

		if t_next_x < 0 or t_next_y < 0:
			print "hmm, interesting", t_next_x, t_next_y

		# Comparing time
		if t_next_x < t_next_y:
			x+=xstep
			dt -= t_next_x
			my_x += vx*t_next_x #This might sometimes create a nan.
			my_y += vy*t_next_x
		#elif t_next_x > t_next_y:
		else:
			y+=ystep
			dt -= t_next_y
			my_y += vy*t_next_y
			my_x += vx*t_next_y
		# Life
		x0 = x % (graphics.world_w / bw)
		y0 = y % (graphics.world_h / bh)
		x0 = int(x0)
		y0 = int(y0)
		if (x0, y0) in newtiles:
			print "hey, this tile is already here"
			break
		newtiles.append((x0,y0))
		#test.tiles.append((x0,y0))
		if room.object_directory[x0][y0]:
			return (x0,y0), room.object_directory[x0][y0]
		# Wall
		elif room.tiles[x0][y0].name != 'empty':
			if len(newtiles) > 1:
				return (x0,y0), -1
	return 0
	test.record('blah')


