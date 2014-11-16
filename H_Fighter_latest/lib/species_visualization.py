from graphics import screen_w, screen_h, world_tw, world_th, bw, bh
import pygame
from game_settings import *
from math import copysign, log
from random import randrange


def is_ancestor(potential_ancestor, potential_descendant):
	'''potential_ancestor and potential_descendant are tuples btw'''
	if len(potential_ancestor) > len(potential_descendant):
		return False
	for i, val in enumerate(potential_ancestor):
		if val != potential_descendant[i]:
			return False
	return True

def log_skew(f):
	if f > 0:
		return log(f)
	elif f < 0:
		return log(-f)
	else:
		assert (f == 0)
		return f

def interpolate(first, second, amount):
	return amount * (second - first) + first

class SpeciesPlot(object):
	''''''
	def __init__(self):
		self.w = 600
		self.h = 800
		self.plot = pygame.Surface((self.w, self.h))
		self.plot.fill([0,0,0])

		self.mx = -200
		self.Mx = 200
		self.my = -200
		self.My = 200

		self.min_ancestry = 0
		self.max_ancestry = 2

		self.col = -1
		self.row = -1

		#self.in_A = randrange(2, 10)
		#self.in_B = randrange(2,10)
		#self.out_A = randrange(0, 4)
		#self.out_B = randrange(0, 4)

		#print "Visualizing following connections: ", self.in_A, " : ", self.out_A, "; ", self.in_B, " : ", self.out_B 

	def get_representation(self, bee):
		#a = bee.brain._all_edges[0][self.in_A, self.out_A]
		#b = bee.brain._all_edges[0][self.in_B, self.out_B]
		#inputs = [-0.090999999999999998, 0.19800000000000001, 0.99646446609406725, 0.89039844891608511, 0.99646446609406725, 0.99646446609406725, 0.89387507361604435, 0.41390060569899922, 0.89746951672795061, 0.99646446609406725, 0.7125000000000001]
		c = int(bee.player.xy[0,0] / bw)
		r = int(bee.player.xy[0,1] / bh)
		try:
			c %= world_tw
			r %= world_th
		except:
			pass
			#print "world_tw and world_th problem"

		v = bee.room.visiondirectory

		infoz = v[c][r]
		#c1 = c+1
		#r1 = r+1

		#try:
		#	c1 %= world_tw
		#	r1 %= world_th
		#except:
		#	c1 = r1 = 0


		#info_00 = v[c][r]
		#info_10 = v[c1][r]
		#info_01 = v[c][r1]
		#info_11 = v[c1][r1]
		#rem_c = (1.0 * bee.player.xy[0,0] % bw) / bw
		#rem_r = (1.0 * bee.player.xy[0,1] % bh) / bh

		# Producing an interpolated version of the inputs
		#infoz = [ rem_r * ((bw - rem_c) * ab + rem_c * bb) + (bh - rem_r) * ((bw - rem_c) * aa + rem_c * ba) for aa, ba, ab, bb in zip(info_00, info_10, info_01, info_11) ]
		#infoz = [interpolate(left, right, rem_c) for left, right in zip(info_00, info_10)]
		#infob = [interpolate(left, right, rem_c) for left, right in zip(info_01, info_11)]
		#infoz = [interpolate(above, below, rem_r) for above, below in zip(infoa, infob)]
		#infoz = [x / (bw*bh) for x in infoz]

		inputs = [0.0,0.0] + [1 - distance for distance in infoz] + [1.0]

		downup, rightleft = bee.brain.compute(inputs, use_memory = 0)
		if settings[BRAIN_ACTIVATION] != 1:
			downup = -2 * downup + 1
			rightleft = 2 * rightleft - 1
		if settings[SPECIES_STYLE] == 1:
			return rightleft, 1 - ((len(bee.ancestry) - self.min_ancestry) * 1.0 / (self.max_ancestry - self.min_ancestry))*2
		elif settings[SPECIES_STYLE] == 2:
			return ((len(bee.ancestry) - self.min_ancestry) * 1.0 / (self.max_ancestry - self.min_ancestry))*2 - 1, downup
		else:
			x,y = rightleft, downup
			radius = (len(bee.ancestry) - self.min_ancestry) * 1.0 / (self.max_ancestry - self.min_ancestry)
			l = (x ** 2 + y ** 2)**0.5
			if not l:
				l = 1
			x = x / l * radius
			y = y / l * radius
			return x, y

	def get_location(self, representation):
		#a, b = representation
		#x = (a-self.mx) / ((self.Mx - self.mx)+0.01)
		#y = (b-self.my) / ((self.My - self.my)+0.01)
		#x,y = int(x), int(y)
		a, b = representation
		#a, b = log_skew(a), log_skew(b)
		if settings[SPECIES_STYLE] == 3:
			#l = (a**2 + b**2)**0.5 + 0.01
			#a, b = a / l, b / l
			a, b = 120 * a, 120 * b
		elif settings[SPECIES_STYLE] == 4:
			a, b = self.w / 2 * a, self.w / 2 * b
		elif settings[SPECIES_STYLE] == 1:
			a *= 120
			b *= self.h / 2.4
		else:
			b *= 120
			a *= self.h / 2.4
		a += self.w / 2
		b += self.h / 2
		a = int(a)
		b = int(b)
		return a,b

	def update(self, bees):
		if not self.plot:
			self.plot = pygame.Surface((self.w, self.h))
		c = int(bees[0].player.xy[0,0] / bw)
		r = int(bees[0].player.xy[0,1] / bh)
		#if c == self.col and r == self.row and randrange(40):
		#	return

		self.col = c
		self.row = r


		self.plot.fill([0,0,0])
		self.min_ancestry = min([len(b.ancestry) for b in bees])
		self.max_ancestry = max([len(b.ancestry) for b in bees]) + 2
		#pygame.draw.circle(self.plot, [255,255,255], self.get_location((0,0)), 10, 1)
		#for b in bees:
		#	x, y = b.representation = self.get_representation(b)
#
		#self.mx = min([x for x,y in [b.representation for bee in bees]])
		#self.Mx = max([x for x,y in [b.representation for bee in bees]])
#
		#self.my = min([y for x,y in [b.representation for bee in bees]])
		#self.My = max([y for x,y in [b.representation for bee in bees]])

		# reset family tree use
		for b in bees:
			b.familytreeuse = 0


		if settings[SPECIES_STYLE] == 4:
			pygame.draw.circle(self.plot, [255, 255, 255], (self.w/2, self.h/2), self.w/2, 1)


		maxrad = 10
		# Drawing everything
		for b in bees:
			if b.dead == 2:
				continue
			thickness = ((len(b.ancestry) - self.min_ancestry) * maxrad) / (self.max_ancestry - self.min_ancestry)

			b.representation = self.get_representation(b)
			beepos = self.get_location(b.representation)
			if b.parent:
				parent = self.get_location(self.get_representation(b.parent))
				b.parent.familytreeuse += 1
				origin = self.get_location((0.0,0.0))
				if settings[SPECIES_STYLE] == 3:
					#pygame.draw.line(self.plot, [0,0,0], beepos, parent, thickness + 5)
					pygame.draw.line(self.plot, b.treecolor, beepos, parent, 1)
					#pygame.draw.line(self.plot, b.treecolor, beepos, origin, 3)
				else:
					#pygame.draw.line(self.plot, [0,0,0], beepos, parent, thickness + 5)
					pygame.draw.line(self.plot, b.treecolor, beepos, parent, 1)
					#pygame.draw.line(self.plot, [50, 50, 50], beepos, origin, 1)
			else:
				b.parent_species_representation = b.representation

			if settings[SPECIES_STYLE] != 3:
				if b.dead:
					pygame.draw.circle(self.plot, b.treecolor, beepos, thickness + 1, 1)
					#pygame.draw.circle(self.plot, [255,0,0], beepos, 10, 1)
				else:
					pygame.draw.circle(self.plot, b.treecolor, beepos, thickness)

		for b in bees:
			if b.parent and b.parent.dead and b.parent.familytreeuse == 1:
				# if your dead father has only one son
				# your father is your grandfather
				b.parent.dead = 2
				b.parent = b.parent.parent
				

		for b in bees:
			if b.dead and b.familytreeuse == 0:
				# if dead and with no descendants remove
				b.dead = 2


		'''# Substituting boring chains
		for b in bees:
			if b.parent and b.parent.parent and b.parent.dead and (b.parent.familytreeuse == 1):
				b.parent.dead = 2
		
		# kiling the trunk of the family tree
		for b in bees:
			if b.dead and not b.parent and (b.familytreeuse == 1):
				b.dead = 2
				break

		# Substituting boring chains, part two
		for b in bees:
			if b.parent and b.parent.dead == 2:
				b.parent = b.parent.parent
		

		ancestries = sorted([b.ancestry for b in bees])
		ranks = { ancestry:i for i,ancestry in enumerate(ancestries)}

		for b in bees:
			if b.dead == 1:
				#bee.dead == 2 means remove bee
				#bee.dead == 1 means still useful
				i = ranks[b.ancestry] + 1
				if i >= len(ranks):
					continue
				potential_descendant = ancestries[i]
				if not is_ancestor(b.ancestry, potential_descendant):
					#Then this bee has no living descendents. Mark it for removal.
					b.dead = 2'''
		

	def draw(self, surface, position = (0,0)):
		if settings[SPECIES_STYLE] == 3:
			surface.blit(self.plot, position, special_flags=pygame.BLEND_MAX)
		else:
			surface.blit(self.plot, position)


