import random
import pygame
import graphics
from graphics import bw, bh
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
import settings

num_best_bees = 10
madness = 0

'''normal mode
gravity = matrix([[0, 0.0006]])
jumpspeed = 0.04
jumpvel = matrix([[0, -jumpspeed]])
maxvel = 0.3
maxvelx = 1
groundacc = 0.0000002
yogroundacc = matrix([[groundacc, 0]])
airacc = 0.0002
airresist = 0.2
friction = 0.1
speed_decay = 0.999
healthlossrate = 0.000001
'''

'''flying'''
gravity = matrix([[0, 0.0006]]) # was 0.0006
jumpspeed = 0.00003
jumpvel = matrix([[0, -jumpspeed]])
maxvel = 0.5
maxvelx = 0.3
groundacc = 0.00003
yogroundacc = matrix([[groundacc, 0]])
airacc = 0.0001
airresist = 0.000002
friction = 0.0000001
speed_decay = 0.998

STALK_CAMERA = True

#afunc = lambda blah: 2/(1+math.e**-blah)-1
#bfunc = lambda blah: 255/(1+math.e**-blah)

consonants = "qwrrrtttypssssssdfffgggghhhhjlzxccccvbbbbbnnnmmm"
vowels = "eeuiiiooaaa"
splits = "-"

WRAPAROUND_TRACKING = True;

class Bee(physical.Physical):
	def __init__(self, room, prebrain = None, color = [128,128,128], radius = 5, health = 1):
		super(Bee, self).__init__(room)
		if prebrain != None:
			self.brain = prebrain
		else:
			self.brain = brain.Brain(7, [3, 4])
		self.radius = radius
		self.health = health
		self.slow = 1
		self.visual_tag = -1
		self.friends = matrix([0, 0])
		self.friendsrelpos = matrix([0, 0])
		#self.eyes = [(1, 0), (1, 1), (0, 1), (-1, 0), (1, -1), (-1, 1), (-1, -1), (0, -1)]
		
		#not actually used, check visiondirectory
		self.eyes = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
		self.responsetime = 30
		self.timesincelastthought = random.random()*self.responsetime
		self.up = 0
		self.leftright = 0

		tags = []
		tags += ["dx", "dy"]
		#tags += ["dvx", "dvy"]
		#tags += ["health"]
		tags += ["*.", "*'", ".*", "'*"]
		#tags += ["friend dvx", "friend dvy", "friend dx", "friend dy"]

		for i, value in enumerate(tags):
			self.brain.nodetags[0,i] = value

		last = len(self.brain.nodes) - 1
		self.brain.nodetags[last,0] = "up"
		self.brain.nodetags[last,1] = "down"
		self.brain.nodetags[last,2] = "left"
		self.brain.nodetags[last,3] = "right"
		#self.brain.nodetags = {(0,0): "dispx", 
		#						(0,1):"dispy"}
		#inputs = disps + [dvx, dvy] + [self.health] + infoz + [self.friends[0,0], self.friends[0,1], self.friendsrelpos[0,0], self.friendsrelpos[0,1]]#+ playerinputs + t
				#2		    #2            #1		  # 4              + 4

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
		self.prevpos = self.xy * 1
		self.vxy *= 0
		self.dvxy = matrix([0.0,0.0])
		self.lastnonwall = matrix([[-1.0, 0.0]])
		self.madness = madness
		self.flash = 20
		#self.a = 1


	def show_brain(self, surface):
		command = self.brain.visualize(surface)
		return command

	'''draws in one long path'''
	def sample_path(self, surface):
		self.slow = 1
		original_position = self.xy * 1
		original_health = self.health

		'''drawing in the start point for '''
		pygame.draw.circle(surface, (0, 0, 255), (int(self.xy[0,0]), int(self.xy[0,1])), 30, 2)
		steps = 600
		for x in range(steps):
			start = self.xy * 1
			self.update(self.dt, 0, 0)
			self.health = original_health
			end = self.xy * 1
			#pygame.draw.circle(surface, (0, 0, 255), (int(self.xy[0,0]), int(self.xy[0,1])), 2, 0)
			if abs(start[0,0] - end[0,0]) < graphics.world_w/2:
				if abs(start[0,1] - end[0,1]) < graphics.world_h/2:
					pygame.draw.line(surface, (x * (255.0 / steps), 255 - x * (255.0 / steps), 255), (start[0,0], start[0,1]), (end[0,0], end[0,1]), 1)
		self.xy = original_position

	'''draws a bunch of paths from a lattice of starting positions'''
	def visualize_intelligence(self, surface):
		self.slow = 1
		original_position = self.xy * 1
		original_health = self.health
		original_nodes = copy.deepcopy(self.brain.nodes)
		'''
		pygame.draw.circle(surface, (0, 0, 255), (int(self.xy[0,0]), int(self.xy[0,1])), 10, 2)
		a = 30
		b = 20
		for x in range(600):
			start = self.xy * 1
			self.update(30, 0, 0)
			end = self.xy * 1
			pygame.draw.circle(surface, (0, 0, 255), (int(self.xy[0,0]), int(self.xy[0,1])), 2, 0)
			pygame.draw.line(surface, (0,255,0), (start[0,0], start[0,1]), (end[0,0], end[0,1]), 1)
		'''
		a = 30
		b = 30
		steps = 4
		# 24 * 16 * 4 = 1536
		dt = 30
		#pygame.draw.circle(surface, (0, 0, 255), (int(self.xy[0,0]), int(self.xy[0,1])), 30, 1)
		triangles = 50.0 * matrix([[1,0],[0.5,0.86602540378]]).T
		for j in range(-b, b+1):
			for i in range(-a, a+1):
				xxx = matrix([[i],[j]])
				offset =(triangles * xxx).T
				

				simradius = 400
				if linalg.norm(offset) > simradius or linalg.norm(offset) < 40:
					continue
				self.xy = offset + original_position
				#self.xy[0,0] = (graphics.world_w * (i + 0.5) )/ a
				#self.xy[0,1] = (graphics.world_h * (j + 0.5) )/ b
				c = int(self.xy[0,0] / bw) % graphics.world_tw
				r = int(self.xy[0,1] / bh) % graphics.world_th

				if self.room.tiles[c][r].name != "empty":
					continue


				for x in range(steps):
					start = self.xy * 1
					self.update(dt, 0, 0)
					self.health = original_health
					self.health = 0.3
					end = self.xy * 1
					#Draw in a circle at each step
					#pygame.draw.circle(surface, (0, 0, 100), (int(self.xy[0,0]), int(self.xy[0,1])), 2, 0)
					if abs(start[0,0] - end[0,0]) < graphics.world_w/2:
						if abs(start[0,1] - end[0,1]) < graphics.world_h/2:
							color = (50 + x * (200 / steps),x * (100 / steps),0)
							color = self.color
							pygame.draw.line(surface, color, (start[0,0], start[0,1]), (end[0,0], end[0,1]), 1)


				radius = int(10 * (simradius - linalg.norm(offset)) / simradius) + 2
				px = int((offset + original_position)[0,0]) % graphics.world_w
				py = int((offset + original_position)[0,1]) % graphics.world_h
				pygame.draw.circle(surface, self.color, (px, py), radius, 1)
				pygame.display.flip()
				self.brain.nodes = copy.deepcopy(original_nodes)
				#clock = pygame.time.Clock()
				#clock.tick(400)
				
		self.xy = original_position

	def stalkcamera(self):
		'''this is a sneakyass setting that teleports you closer to the camera when necessary'''

		#this is the plain unwrapped offset
		offset = self.xy - self.room.camera.xy
		center = matrix([graphics.world_w/2, graphics.world_h/2])
		offset += center
		offset[0,0] %= graphics.world_w
		offset[0,1] %= graphics.world_h
		offset -= center
		# now it's in a box centered at 0,0

		#stalkframe = 200

		stalkw = graphics.disp_w
		stalkh = graphics.disp_h
		stalkcorner = matrix([stalkw, stalkh])

		# so we have the minimum offset from the camera.
		'''
		offset[0,0] = min(offset[0,0], graphics.disp_w / 2 + stalkframe)
		offset[0,0] = max(offset[0,0], -graphics.disp_w / 2 - stalkframe)

		offset[0,1] = min(offset[0,1], graphics.disp_h / 2 + stalkframe)
		offset[0,1] = max(offset[0,1], -graphics.disp_h / 2 - stalkframe)
		'''

		oldoffset = offset * 1

		offset += stalkcorner
		offset[0,0] %= 2*stalkw
		offset[0,1] %= 2*stalkh
		offset -= stalkcorner

		#offset[0,0] = min(offset[0,0], 200 / 2 + stalkframe)
		#offset[0,0] = max(offset[0,0], -200 / 2 - stalkframe)

	#	offset[0,1] = min(offset[0,1], 200 / 2 + stalkframe)
	#	offset[0,1] = max(offset[0,1], -200 / 2 - stalkframe)

		if linalg.norm(oldoffset - offset) > 0:
			self.xy = self.room.camera.xy + offset


	def update(self, dt, key_states, key_presses):
		'''physics, thinking, moving'''


		'''This is where you cruise without physics and without thinking'''
		if not self.slow:
			self.dt = dt
			self.xy += self.vxy*self.dt
			return

		self.prevpos = self.xy * 1
		fullname = self.name + self.ancestry

		test.add_sticky('bee')

		super(Bee, self).update(dt, key_states, key_presses)

		test.record("physical inherited update")

		self.timesincelastshot += dt

		#for b in self.bullets:
		#	b.update(dt, key_states, key_presses)

		
		self.update_health(dt)
		self.considergivingbirth()

		'''when you're not dead'''
		self.friends*=0.9
		self.friendsrelpos*=0.9
		for p in self.objectsinview:
			if p.kind == "bullet":
				p.hit_bee(self)
			if p.kind == "bee" and p.name != self.name:
				self.friends = p.vxy - self.vxy
				self.friendsrelpos = p.xy - self.xy
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
			test.record("Time spend computing bee vision")

			#go = time.time()
			#t = [math.sin(go), math.sin(go/2.3), math.sin(go)%1.5]
			
			center = matrix([graphics.world_w/2, graphics.world_h/2])

			if STALK_CAMERA:
				self.stalkcamera()

			disp_to_p = self.player.xy - self.xy

			if WRAPAROUND_TRACKING:
				disp_to_p += center
				disp_to_p %= graphics.world_w
				disp_to_p %= graphics.world_h
				disp_to_p -= center

			dispx = disp_to_p[0,0]/graphics.world_w
			dispy = disp_to_p[0,1]/graphics.world_h

			disps = [dispx, dispy]
			dvx = self.player.vxy[0,0] - self.vxy[0,0]
			dvy = self.player.vxy[0,1] - self.vxy[0,1]

			inputs = []
			inputs += disps # 2
			inputs += infoz # 4
			#inputs += [dvx, dvy] # 2
			inputs += [self.health] # 1 
			#inputs += [self.friends[0,0], self.friends[0,1], self.friendsrelpos[0,0], self.friendsrelpos[0,1]] # 4
			test.record("Displacements")


			outputs = self.brain.compute(inputs)
			test.record("Computing brain outputs")

			processedoutputs = [x for x in outputs]
			self.up = outputs[1] - outputs[0]
			#down = outputs[1]
			self.leftright = outputs[3] - outputs[2]
			self.color = [outputs[0], outputs[1], (linalg.norm(self.vxy) - 0.1)*2]
			self.color = [int(i*128 + 127) for i in self.color]
			self.color = [max(a,0) for a in self.color]
			self.color = [min(a,255) for a in self.color]


			if 1==0 and outputs[2] > 0 and self.timesincelastshot > 1000:
				self.timesincelastshot = 0
				direction = matrix([outputs[3],outputs[4]])
				direction = disp_to_p
				direction /= linalg.norm(direction)
				b = bullet.Bullet(self, self.player, self.room, direction * outputs[2] * 2)
				b.xy = self.xy + matrix([0,0])
				self.room.bullets.append(b)
				self.health -= 0.05

			

		
		self.vxy += gravity*dt


		self.dvxy = self.up*jumpvel*dt + self.leftright*yogroundacc*dt
		self.vxy += self.dvxy * dt
		self.vxy *= speed_decay**dt


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


		#maybe teleport back
		c = int(self.xy[0,0] / bw)
		r = int(self.xy[0,1] / bh)
		if self.room.tiles[c][r].name == "wall":
			if (self.lastnonwall[0,0] < 0):
				self.randomize_position(200)
			else:
				self.xy = self.lastnonwall * 1
				self.vxy *= 0
		else:
			self.lastnonwall = self.xy * 1


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
		deathpercentage = 1
		if self.health < 0:
			if random.random() > deathpercentage:
				self.brain.randomizeconnections()
				self.health = 1
			else:
				self.die()

	def eat_player(self):
		disp = self.xy - self.player.xy
		dist = linalg.norm(disp)
		if dist < (self.radius + self.player.forcefield)**2 and dist > 0:
			if self.player.automaticEvasion:
				self.player.randomize_position(5)
			if self.player.killmode:
				self.die()

			#self.player.color = [x for x in self.color]
			#self.player.radius -=1
			#self.player.grounded = 0
			
			self.player.losinghealth=1
			self.player.beepushes.append(-disp / dist)

			kickdirection = -disp / dist
			self.player.vxy += (dist + 0.1)**-2 * kickdirection * 10
			#self.player.grounded = 0

			self.health += settings.healthgain
			#self.score += 1

			# Fun with bestbees
			'''if self not in self.room.bestbees:
													if len(self.room.bestbees) < num_best_bees:
														self.room.bestbees.append(self)
													elif min([foo.score for foo in self.room.bestbees]) < self.score:
														self.room.bestbees.append(self)
														self.room.bestbees.sort(key = lambda x: x.score)
														self.room.bestbees = self.room.bestbees[-num_best_bees:]'''

	def update_health(self, dt):
		self.health -= settings.healthlossrate*dt
		#self.health -= linalg.norm(self.vxy) * 0.01
		#self.health += (1-((self.xy[0,0] - self.player.xy[0,0])/graphics.world_w)**2 )*2*healthlossrate * dt
		if self.normals:
			self.health -= settings.acid
		#self.health -= linalg.norm(self.dvxy) * dt * 0.01

		if self.health > 1:
			self.health = 1

	def considergivingbirth(self):
		if len(self.room.bees) < self.room.beecap and self.health > 0.9 and random.random() > 0.3:
			self.health -= 0.0
			self.children += 1
			newbee = Bee(self.room, copy.deepcopy(self.brain), self.color, self.radius)
			newbee.mutate()
			newbee.brain.randomizenodes()
			newbee.randomize_color()
			newbee.health = 0.8
			newbee.place(self.xy + matrix([0,0]))#mimic position
			#newbee.randomize_position(0.3)#randomize position
			newbee.findplayer(self.player)
			newbee.name = self.name
			newbee.ancestry = self.ancestry + "." + str(self.children)
			newbee.madness = self.madness
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
		try:
			self.room.bullets = [b for b in self.room.bullets if b.bee != self]
			self.room.bees.remove(self)
		except:
			pass

	def draw(self, surface):
		#for b in self.bullets:
		#	b.draw(surface)
		fullname = self.name + self.ancestry
		test.add_sticky('bee')
		test.add_sticky('draw bee')
		super(Bee, self).draw(surface)
		ixy = self.xy.astype(int)
		start = self.xy
		end = self.prevpos
		'''this is here to trip you up'''
		if abs(start[0,0] - end[0,0]) < graphics.world_w / 2:
			if abs(start[0,1] - end[0,1]) < graphics.world_h/2:
				if self.madness == 1:
					'''lines'''
					pygame.draw.line(self.room.background, self.color, array(self.xy)[0], array(self.prevpos)[0], 1)
				elif self.madness == 2:
					'''extra mad'''
					pygame.draw.circle(self.room.background, self.color, array(self.xy)[0], int(linalg.norm(self.prevpos-self.xy)), 0)

		for x in range(-1, 2, 1):
			if x and 0 < ixy[0,0] + self.radius * -x < graphics.world_w:
				continue
			for y in range(-1, 2, 1):
				if y and 0 < ixy[0,1] + self.radius * -y < graphics.world_h:
					continue
				px = ixy[0,0] + x*graphics.world_w
				py = ixy[0,1] + y*graphics.world_h
				#c = self.color
				blood = [255,0,0]

				#pygame.draw.circle(surface, c, (px, py), int(self.radius))
				r = int(self.radius * 0.6)
				if self.vxy[0,0]>0:
					pygame.draw.line(surface, blood, (px-r,py-r), (px+r, py+r), 1)
				else:
					pygame.draw.line(surface, blood, (px+r,py-r), (px-r, py+r), 1)




				#pygame.draw.circle(surface, [int(p) for p in self.color], (px, py), int(self.radius))
				#centercolor = [255-n for n in c]
				#rad = int(self.radius*(1-self.health))
				#rad = max( rad, 0)
				#pygame.draw.circle(surface, [int(p) for p in centercolor], (px, py), rad)


				if self.flash:
					pygame.draw.circle(surface, [255, 255, 255], (px, py), self.flash + 1)
					self.flash -= 1

				regularcolor = self.color
				r2 = int(self.radius * 0.6 * self.health)
				if self.vxy[0,0]>0:
					pygame.draw.line(surface, regularcolor, (px-r2,py-r2), (px+r2, py+r2), 1)
				else:
					pygame.draw.line(surface, regularcolor, (px+r2,py-r2), (px-r2, py+r2), 1)



				



		# My velocity
		#endxy = ixy+numpy.round_(self.vxy*10)
		#pygame.draw.line(surface, (255, 255, 0), array(ixy)[0], array(endxy)[0], 1)
		test.record()
		test.remove_sticky('bee')
		test.remove_sticky('draw bee')


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


