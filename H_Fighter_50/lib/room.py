'''This file defines a room for the platformer.'''

import graphics
from graphics import bw, bh
import tile
import pygame
import numpy
import collision
import random
from numpy import matrix, linalg, array
from itertools import groupby
import copy
import test
import bee
import convex
import messages
import math
import bullet
# Tile count in a room
#rows = None #graphics.world_h / bh
#cols = None #graphics.world_w / bw

USE_IMAGES = 0


def tuplefrommatrix(mat):
	return (mat[0,0], mat[0,1])

def load(file_in):
	file_descriptor = open(file_in)
	lines = file_descriptor.readlines()
	global rows, cols
	rows = len(lines)-1
	cols = len(lines[-1])
	file_descriptor.close()
	tiles = []
	for c in range(cols):
		tiles.append([])
		for r in range(rows):
			tiles[c].append(tile.tile[lines[r][c]]) # Essentially we used the character (e.g. 'Q') to access the dictionary entries (which are Tile object instances)
			#Notice that there is a transposition here.
	
	return Room(tiles)

def normal_and_normpos(s):
	normal = s[1][0,0], s[1][0,1]
	point = s[0][0]
	pos = point[0] * normal[0] + point[1]*normal[1]
	if normal[0] < 0 or normal[1] == -1:
		pos *= -1
		normal = [-x for x in normal]
	else:
		normal = [x for x in normal]
	return normal, pos

def flipkey(k):
	(normal1, normal2), pos = k
	return (-1*normal1, -1*normal2), -1*pos


class Room(object):
	def __init__(self, tiles):
		self.cols, self.rows = cols, rows
		self.tiles = tiles # Whoops, this is more of a set of pointers than a set of distinct Tile objects
		
		messages.say("reducing sides", 0)
		self.sides = self.get_sides(matrix([[-1, -1]]), matrix([[graphics.world_w + 1, graphics.world_h + 1]]), checknormals = 0, verbose = 0)
		#print "I have", len(self.sides), "sides."
		self.side_directory =  [[[] for r in range(rows+2)] for c in range(cols+2)]
		self.give_tiles_better_sides()
		self.sidelabels = []
		#numbering the sides
		for i, side in enumerate(self.sides): # For all numbered sides
			#print "\n\n\n\n\n\n", array(side.side[0])[0], "\n\n\n"#, array(side.side[0])[0]
			start = array(side.side[0])[0]
			n = array(side.normal)[0]
			start = [x - 0.05*y for (x,y) in zip(start, n)]
			end = array(side.side[1])[0]
			end = [x - 0.05*y for (x,y) in zip(end, n)]

			font = pygame.font.Font(None, 15)
			text = font.render(str(i), 1, (255, 255, 255))
			textpos = text.get_rect(centerx = (start[0] + end[0])/2, centery = (start[1] + end[1])/2)
			self.sidelabels.append([start,end,text,textpos])

		messages.say("optimising convexes", 0)
		self.convex_directory = [[ None for r in range(rows+4)] for c in range(cols+4)]
		for c in range(-2, cols+2):
			for r in range(-2, rows+2):
				tps = self.tiles[c%cols][r%rows].pointlist
				if not tps:
					continue
				mps = [matrix([x,y]) for x,y in tps]
				offset = matrix([bw*c, bh*r])
				a = convex.Convex(mps, offset)
				a.name = self.tiles[c%cols][r%rows].name
				self.convex_directory[c][r] = a
		

		lol = []
		for s in self.sides:
			lol.extend(s.side)

		coco = 0
		for p in lol:
			ex,ey = p[0,0],p[0,1]
			l = math.ceil(ex/bw) - 1
			r = math.floor(ex/bw)
			t = math.ceil(ey/bh) - 1
			b = math.floor(ey/bh)

			l = int(l)
			r = int(r)
			t = int(t)
			b = int(b)

			mx = int(ex/bw)
			my = int(ey/bh)

			if l == r or t == b:
				continue

			for posx in range(l, r+1):
				for posy in range(t, b+1):
					c = self.convex_directory[posx][posy]
					if c:
						for q in c.points:
							if linalg.norm(p-q) == 0:
								if not c.use[q]:
									coco += 1
								c.use[q] = 1
								#print "we're using {0} now".format(q)
								#print "\n", c.use, "\n"
								break
						else:
							pass
							#print "none of the elements of {0} equal {1}".format(c.points, p)

			#print "found", coco, "points"


		self.adjust_convexes()

		messages.say("computing density", 0)
		self.density = [[ sum([self.tiles[(x + x0)% len(tiles)][(y + y0) % len(tiles[0])].name != 'empty' for x0 in [-2, -1, 0, 1, 2] for y0 in [-1, 0, 1]]) for y in range(len(tiles[0]))] for x in range(len(tiles))]
		#print "I have", len(self.tiles), "x", len(self.tiles[0]), "tiles."
		
	


		


		self.object_directory = [[[] for r in range(rows)] for c in range(cols)]
		self.background = pygame.Surface((graphics.world_w, graphics.world_h))
		self.a = 0

		self.start_position = matrix([100, 100])
		messages.say("drawing background", 0)
		self.draw(self.background) # Note that this sets the start position to wherever the '!' is
		self.background.convert()
		self.food = []
		self.bees = []
		self.player = None
		self.topbar = None
		self.beehistory = 0
		self.acid = 0.05
		self.bestbees = []
		self.timetosave = 100
		self.h = None
		self.beecap = 30
		self.dirtyareas = []
		self.visibles = []
		self.bullets = []

		messages.say("precomputing vision", 0)
		self.visiondirectory = [[[] for r in range(rows)] for c in range(cols)]
		eyes = [(1, 0), (1, 1), (0, 1), (-1, 0), (1,2), (1, -1), (-1, 1), (-1, -1), (0, -1)]
		directions = [] + eyes
		for c in range(cols):
			for r in range(rows):
				sights = []
				xy = matrix([(c+0.5)*bw, (r+0.5)*bh])
				for x,y in directions:
					n = (x**2 + y**2)**0.5
					x0 = x / n
					y0 = y / n
					sights.append(bee.look2(self, xy[0,0], xy[0,1], x0, y0, 100, bw, bh))

				infoz = []
				for targ in sights:
					if targ:
						(x,y), name = targ
						posx, posy = x*bw + 16, y*bh + 16
						dist = ((posx - xy[0,0])**2 + (posy - xy[0,1])**2)**0.5
						infoz.append(dist / 100)
					else:
						infoz.append(0)
				self.visiondirectory[c][r] = infoz

	def adjust_convexes(self):
		'''modifies shadows and deactivates sides as necessary to improve collision testing'''

		known_side_mods = {}

		dirs = {}
		dirs[(0, 1)] = "right"
		dirs[(0, -1)] = "left"
		dirs[(1, 0)] = "bottom"
		dirs[(-1,0)] = "top"

		'''side modification'''
		for x in range(cols):
			for y in range(rows):
				'''want to kill some sides of this shape'''
				c = self.convex_directory[x][y]
				if not c:
					continue

				for x0, y0 in dirs:
					'''check each neighbor for stickiness'''
					xo = x + x0
					yo = y + y0
					given = (self.tiles[x][y].name, self.tiles[xo%graphics.world_tw][yo%graphics.world_th].name, dirs[(x0,y0)])
					co = self.convex_directory[xo][yo]
					if not co:
						continue



					'''
					READ FROM THE PRECOMPUTED STUFF
					'''

					if given in known_side_mods:
						result = known_side_mods[given][:]
					else:
						result = []
						sticky_normal = None
						sticky_count = 0
						number_same = 0

						possnorms = c.shadowDict.keys()

						for k in co.shadowDict.keys():
							for j in possnorms:
								if numpy.array_equal(k,j):
									break
							else:
								possnorms.append(k)

						for n in possnorms: # Counting sticky edges
							'''for all shadows'''
							try:
								small, big =  c.shadowDict[n]
							except:
								small, big = convex.find_shadows([n], c.points)[n]

							try:
								so, bo =  co.shadowDict[n]
							except:
								so, bo = convex.find_shadows([n], co.points)[n]

							'''see if they stick'''
							if big == so:
								sticky_normal = n, 'bigso', (small, float('infinity')), (-float('infinity'), bo)
								sticky_count += 1
							elif small == bo:
								sticky_normal = n, 'smallbo', (so, float('infinity')), (-float('infinity'), big)
								sticky_count += 1

						if sticky_count == 1: # Modify result
							swap = 0
							left, right = 0,0
							if sticky_normal[1] == 'bigso':
								left, right = c, co
							elif sticky_normal[1] == 'smallbo':
								left, right = co, c
								swap = 1
							else:
								print "what the hell?"
								continue

							n = sticky_normal[0]
							result = [n, swap]
						
						known_side_mods[given] = result
						#print "{0} to the {1} of {2} gives {3}".format(given[1], given[2], given[0], result)

					#print "result was", result

					if result:
						#if x == y == 1:
						#	print result, c.shadowDict
						#if given in known_side_mods:
						#	result2 = known_side_mods[given]
						#	if any([linalg.norm(x-y) == 0 for x,y in zip(result, result2)]):
						#		print "strange", result, result2

						n = result[0]
						swap = result[1]
						if swap:
							left,right = co, c
						else:
							left,right = c, co


						for m in left.shadowDict:
							if linalg.norm(n-m) == 0:
								left.shadowDict[m] = left.shadowDict[m][0], float('infinity')
						for m in right.shadowDict:
							if linalg.norm(n-m) == 0:
								right.shadowDict[m] = -float('infinity'), right.shadowDict[m][1]
					
				d = {}


				for n, r in c.shadowDict.iteritems():
					if r != (-float('infinity'), float('infinity')):
						d[n] = r

				c.shadowDict = d

		known_point_mods = {}

		'''point modification'''
		'''
		for x in range(cols):
			for y in range(rows):
				c = self.convex_directory[x][y]
				if not c: continue
				for p in c.points:
					ex,ey = p[0,0],p[0,1]
					l = math.ceil(ex/bw) - 1
					r = math.floor(ex/bw)
					t = math.ceil(ey/bh) - 1
					b = math.floor(ey/bh)

					l = int(l)
					r = int(r)
					t = int(t)
					b = int(b)

					mx = int(ex/bw)
					my = int(ey/bh)

					if l == r or t == b:
						continue

					#test.backgroundmarkers.append(( (ex,ey), ((l+0.5)*bw, (t+0.5)*bh)))
					#test.backgroundmarkers.append(( (ex,ey), ((r+0.5)*bw, (t+0.5)*bh)))
					#test.backgroundmarkers.append(( (ex,ey), ((l+0.5)*bw, (b+0.5)*bh)))
					#test.backgroundmarkers.append(( (ex,ey), ((r+0.5)*bw, (b+0.5)*bh)))
					#test.backgroundmarkers.append(( (ex,ey), (ex-5, ey+5)))

					v = h = 0

					if l == mx:
						h = r
					else:
						h = l

					if t == my:
						v = b
					else:
						v = t

					concount = 0
					cons = []
					for posx in range(l, r+1):
						for posy in range(t, b+1):
							cons.append(self.convex_directory[posx][posy])
					#cons = [self.convex_directory[posx][posy] for posx,posy in [(l,t),(r,t),(l,b),(r,b)]]


					try:
						vert = self.convex_directory[mx][v]
						horiz = self.convex_directory[h][my]
						diag = self.convex_directory[h][v]
					except:
						print "bad", ex,ey,mx,v
						continue

					weird = []
					foo = [c, horiz, diag, vert]
					for con in foo:
						if not con:
							weird.append(0)
						else:
							for q in con.points:
								if numpy.allclose(p,q):
									weird.append(1)
									break
							else:
								weird.append(0)

					if len(weird) != 4:
						print "tile list 'weird' is of wrong lenth,", len(weird)

					remove = [0,0,0,0]
					p_remove = [0,0,0,0]
					# we want to remove a point.
					# if it's never used.
					#     It's completely surrounded
					#     The adjacent sides will always push better

					if sum(weird) == 2:
						remove = weird # Imprecise
						p_remove = weird
					elif sum(weird) == 4:
						remove = weird # Incorrect for wedges
						p_remove = weird # Incorrect for wedges
					elif sum(weird) == 3:
						remove = p_remove = [weird[i-2] for i in range(4)]
						#remove is inefficient because we make all tiles push

					for i, k in enumerate(foo):
						if k:
							if remove[i] and p in k.use:
								k.use[p] = 0
							if p_remove[i] and p in k.use_pointwise:
								k.use_pointwise[p] = 0
		'''


		'''deleting convexes and drawing testlines'''
		wolo = 0
		for x in range(cols):
			for y in range(rows):
				c = self.convex_directory[x][y]
				if not c:
					continue
				if not c.shadowDict and all([v == 0 for k,v in c.use.iteritems()]):
					self.convex_directory[x][y] = None
				else:
					for n in c.shadowDict:
						ex, ey = (x + 0.5)*bw, (y + 0.5)*bh
						mi, ma = c.shadowDict[n]
						if ma != float('infinity'):
							test.backgroundmarkers.append(( (ex,ey), (ex+10*n[0,0], ey+10*n[0,1])))
						if mi != -float('infinity'):
							test.backgroundmarkers.append(( (ex,ey), (ex-10*n[0,0], ey-10*n[0,1])))
					for k,v in c.use.iteritems():
						if v:
							wolo += 1
							ex, ey = k[0,0], k[0,1]
							test.backgroundmarkers.append(( (ex-5,ey-5), (ex+5, ey+5)))
							test.backgroundmarkers.append(( (ex+5,ey-5), (ex-5, ey+5)))
					p = ( (x+0.4)*bw, (y+0.4)*bh)
					q = ( (x+0.6)*bw, (y+0.4)*bh)
					r = ((x+0.6)*bw, (y+0.6)*bh)
					s = ((x+0.4)*bw, (y+0.6)*bh)
					test.backgroundmarkers.extend([(p,q), (q,r), (r,s), (s,p)])

	def update(self):
		print "boom, boom, I'm a room."
		self.timetosave -= 1
		if self.timetosave < 0:
			for b in self.bestbees:
				#print b.score,
				self.h.save_bee(b)
			self.h.savedata()
			self.timetosave = 100

		self.object_directory = [[[] for r in range(rows)] for c in range(cols)]

		if not self.bees:
			self.topbar.flash("extinction :(")
			self.generate_bees(self.beecap)

	def generate_bees(self, n):
		for k in range(n):
			b = bee.Bee(self)
			#b.randomize_position()
			b.randomize_color()
			b.findplayer(self.player)
			self.bees.append(b)

	def draw(self, surface):
		if self.a != 0:
			return
		'''flat color'''
		surface.fill(graphics.background)
		#surface.fill([70,70,70])

		'''random circles'''
		'''
		for k in range(10000):
			x = random.random()*graphics.world_w
			y = random.random()*graphics.world_h
			x0, y0 = int(x/bw), int(y/bh)
			r = random.random()*graphics.bw * (1 + 0.12*self.density[x0][y0])
			red = min(27*self.density[x0][y0] + random.random() * 30, 255)
			green = min(50*self.density[x0][y0] + random.random() * 100, 255)
			blue = min(13*self.density[x0][y0] + random.random() * 100, 255)
			c = (red, green, blue)
			for a in range(-1,2,1):
				for b in range(-1,2,1):
					pygame.draw.circle(surface, c, [int(x) + a * graphics.world_w, int(y) + b*graphics.world_h], int(r))
		'''
		#for x in range(cols):
		#	for y in range(rows):
		#		r = pygame.Rect(x*bw, y*bh, bw, bh)
		#		pygame.draw.rect(surface, [min(27*self.density[x][y] + random.random() * 100, 255)]*3, r)
		for x in range(cols):
			for y in range(rows):
				this_tile = self.tiles[x][y] # For each tile
				if this_tile.name != 'empty':
					if USE_IMAGES:
						surface.blit(this_tile.surface, (x*bw, y*bh)) # Blit image
					else:
						pointlist = [ (x*bw + x0, y*bh +y0) for x0, y0 in this_tile.pointlist] # Draw shape
						if not pointlist:
							self.start_position[0,0] = x*bw + 16
							self.start_position[0,1] = y*bh + 16
							continue
						g = len(self.side_directory[x][y])
						pygame.draw.polygon(surface, graphics.foreground, pointlist)
						#pygame.draw.polygon(surface, [ 255 - min(random.random()*150 + self.density[x][y] * 20, 255) for k in graphics.foreground], pointlist)

		
		for i, side in enumerate(self.sides): # For all numbered sides
			start = array(side.side[0])[0]
			n = array(side.normal)[0]
			start = [x - 0.05*y for (x,y) in zip(start, n)]
			end = array(side.side[1])[0]
			end = [x - 0.05*y for (x,y) in zip(end, n)]

			font = pygame.font.Font(None, 15)
			text = font.render(str(i), 1, (255, 255, 255))
			textpos = text.get_rect(centerx = (start[0] + end[0])/2, centery = (start[1] + end[1])/2)

			#print "\n\n\n\n\n\n", array(side.side[0])[0], "\n\n\n"#, array(side.side[0])[0]
			#try:
				#start, end, text, textpos = self.sidelabels[i]
			pygame.draw.line(surface, graphics.outline, start, end, 3) # Draw the offsetted lines
			#pygame.draw.circle(surface, [0,0,255], [int(k) for k in start], 2)
			#pygame.draw.circle(surface, [0,0,255], [int(k) for k in end], 2)
			#surface.blit(text, textpos)
			#except:
			#	continue
		

	def repair(self, surface):
		for a in self.dirtyareas:
			surface.blit(self.background, a, a)
		self.dirtyareas = []


	def get_sides(self, xy, dxy, checknormals = 1, verbose = 0):
		'''Given a start and end, returns a list of sides'''
		# Selecting bounding box
		x, y = array(xy)[0]
		dx, dy = array(dxy)[0]
		qleft = int(min(x, x+dx)-1) / bw
		qright = int(max(x, x+dx) + 1) / bw + 1
		qtop = int(min(y, y+dy)-1) / bh 
		qbottom = int(max(y, y+dy)+1) / bh + 1

		sides = []# This will be a huge list of Side objects.
		testboxes = []# Here are the tiles that I will check for sides
		# Getting tiles from bounding box
		for col in range(qleft, qright):
			for row in range(qtop , qbottom):
				if -1 <= col <= cols + 1 and -1 <= row <= rows + 1:
					#we can definitely do more checks, but for now I'll just be naive about it.
					tile = self.tiles[col%graphics.world_tw][row%graphics.world_th]
					for ((x1, y1), (x2, y2)), normal in tile.sides:
						offset_x, offset_y = col*bw, row*bh
						sides.append((((x1+offset_x, y1+offset_y), (x2+offset_x, y2+offset_y)), normal) )
						#testboxes.append( pygame.Rect(offset_x, offset_y, bw, bh) )
		#print sides[0]
		#print normal_and_normpos(sides[0])
		sides.sort(key = normal_and_normpos )
		#groups = []
		#uniquekeys = []
		#print "position 1"
		#print "position 2"
		#for k, g in groupby(sides, normal_and_normpos):
		#	groups.append(list(g))
		#	uniquekeys.append(list(k))
		#print uniquekeys, "hey"
		fams = []
		for s in sides:
			if not fams or fams[-1][0]!= normal_and_normpos(s):
				fams.append([normal_and_normpos(s),[s]])
			else:
				fams[-1][1].append(s)
		#print "position 3"
		#families = zip(uniquekeys, groups)
		#print "position 5"
		families = [(k, combine_sides(g)) for k, g in fams]
		#print [k for k,g in families], "whoa"
		sides2 = []
		for k, g in families:
			sides2.extend(g)

		#print len(sides2), "rofl"
		#zeros = [(k,g) for k,g in families if k[1] == 0]
		#print "position 6"
		#positives = [(k,g) for k,g in families if k[1] > 0]
		#print "position 7"
		#negatives = [(k,g) for k,g in families if (k,g) not in zeros and (k,g) not in positives]
		#if negatives:
		#	print "problem!" 

		#sides = [ (s, matrix(s[0][0])*s[1].T, s[1]) for s in sides]
		#print sides[0]
		#sides.sort(key = lambda s: ( (s[2][0,0], s[2][0,1]), s[1][0,0]))
		#sides = [s[0] for s in sides]
		#print sides[0]
		#divided_up = sorted(sides, key = lambda s: tuplefrommatrix(s[1]))
		#print "mkay"
		'''
		Pseudocode time:
		take all the sides and sort them by normal and normpos.
		take them and group them by if the normals are negative and the normpos are negative.
		remove doubled sides.

		for the remaining sides, do the adjacent addition.
		'''

		#sides = combine_sides(sides, verbose) # package the sides. Could be a lot more efficient.
		#print [s for s in sides2 if s not in sides]
		sides = sides2
		#print len(sides), "mao"
		if checknormals:
			return [collision.Side(segment, normal) for segment, normal in sides if (matrix(normal)*dxy.T)[0,0] > 0 ] # Here I filter the sides by checking if you're travelling inward to the side. (simple dot product stuff
		else:
			return [collision.Side(segment, normal) for segment, normal in sides]

	def give_tiles_better_sides(self):
		'''sends all the tiles a list of the sides that overlap with them'''
		counter = 1
		#print "self.sides has", len(self.sides), "elements."
		for i, side in enumerate(self.sides):
			side.number = i
			s = side.side # A list of points in the form of matrices [[ x, y]]
			my_x, my_y = array(s[0])[0]
			vx, vy = array(s[1]-s[0])[0]
			targets = collision.find_all_tiles(my_x, my_y, vx, vy, 1.0, bw, bh)
			#print "So this side has", len(targets), "targets"
			for x, y in targets:
				if -1 <= x < cols+1 and -1 <= y < rows+1:
					#print "now I will add the term", i, ", to position", (x,y), "which currently records", self.side_directory[x][y]
					self.side_directory[x][y].append(i)
					counter += 1
		#print "phew, added", counter, "references"
		for c in range(cols):
			for r in range(rows):
				t=self.side_directory[c][r]
				t[:] = list(set(t))#;print "position", (c,r), "links to", len(t), "sides,", t

def combine_sides(unoptimised_sides, verbose = 0):
	no_interior = []
	for s in unoptimised_sides:
		add_side_except_interior(s, no_interior, verbose)

	combined_adjacent = []
	for s in no_interior:
		add_side_combining_adjacent(s, combined_adjacent)
	return combined_adjacent

def add_side_except_interior(new_side, list_of_sides, verbose = 0):
	rotate_180 = matrix(((-1, 0), (0, -1)))
	cancelled = 0
	(n_start, n_end), n_normal = new_side
	for old_side in list_of_sides:
		(o_start, o_end), o_normal = old_side

		if linalg.norm(n_normal + o_normal) == 0:#n_normal[0] == -o_normal[0] and n_normal[1] == -o_normal[1]:
			if n_start == o_end and n_end == o_start: # Basically if there are two sides pressed together and of the same size: #print "KILLED DOUBLE SIDES"
				a = len(list_of_sides)
				if verbose: print a, "is the length of the list of sides before removal"
				list_of_sides[:] = [s for s in list_of_sides if s not in [old_side]]
				if verbose: print len(list_of_sides), "is the length of the list of sides after removal"
				if a - len(list_of_sides) == 2 and verbose:
					print old_side, new_side, "Somehow cancellation of these two sides removed two sides (instead of one)"
				cancelled = 1
	if not cancelled:
		list_of_sides.append(new_side)
	return list_of_sides

def add_side_combining_adjacent(new_side, list_of_sides):
	combined = 0
	(n_start, n_end), n_normal = new_side
	for old_side in list_of_sides:
		(o_start, o_end), o_normal = old_side
		if linalg.norm(n_normal - o_normal) == 0:
			if n_start == o_end: #print "COMBINED TWO SIDES"
				modified_side = ((o_start, n_end), n_normal)
				list_of_sides[:] = add_side_combining_adjacent( modified_side, [s for s in list_of_sides if s != old_side] )
				combined = 1
			elif n_end == o_start: #print "COMBINED TWO SIDES"
				modified_side = ((n_start, o_end), n_normal)
				list_of_sides[:] = add_side_combining_adjacent( modified_side, [s for s in list_of_sides if s != old_side] ) # There's plenty of inefficiency here!
				combined = 1
	if not combined:
		list_of_sides.append(new_side)
	return list_of_sides
