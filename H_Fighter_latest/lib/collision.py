from numpy import array, matrix, linalg
from graphics import bw, bh
import numpy
import pygame
import graphics
import math
import tile
import test


class Side(object):
	"""contains location plus some collision testing."""
	def __init__(self, side, normal):
		#self.side = [matrix([s]).astype(numpy.float64) for s in side]
		self.side = [matrix([s]).astype(float) for s in side]
		self.normal = normal
		nx, ny = normal[0,0], normal[0,1]
		max_slope = 2
		self.ground = ny > 0 and abs(nx) < max_slope*abs(ny)
		self.linestodraw = []
		self.rectstodraw = []
		self.circlestodraw = []
		self.tiles = []
		self.number = -1
		self.normpos = (self.side[0][0,0] * matrix(self.normal).T)[0,0]

	#def draw(self, surface):
	#	pass

	def is_hit_by(self, p_start, p_dxy, dt = 1.0):
		'''checks for intersection of point path with side.
		Returns false if there are no intersections... otherwise returns a new path to travel
		assumption here is that motion is not parallel to surface'''



		rotation = matrix([[0,1], [-1,0]])

		#for player
		p_target = p_start + p_dxy#; print p_target
		p_normal = p_dxy * rotation#; print p_normal


		#for this side
		s_start, s_target = self.side#; print s_start, s_target
		s_dxy = s_target - s_start#; print s_dxy
		s_normal = s_dxy * rotation#; print s_normal

		'''
		SIMULTANEOUS EQUATIONS. MY DIAGRAM IS

		
		 /           /p0x\  \
		 | (n0x n0y) |   |  |
		 |           \p0y/  |        /n0x n0y\ /x\
		 |                  |    =   |       | | |
		 |           /p1x\  |        \n1x n1y/ \y/
		 | (n1x n1y) |   |  |
		 \           \p1y/  /
		
		         B               =      A   *  X
		'''
		#print numbers_overlap([matrix([[k]]) for k in range(1, 10)],[matrix([[k]]) for k in range(3, 15)]), "YOLO"

		A = numpy.append(p_normal, s_normal, axis = 0)
		# Transformation A aligns p vector to the y axis and aligns the s vector to the x axis.

		B = numpy.append(p_normal * p_start.T, s_normal * s_start.T, axis = 0)
		# Potential intersection.
		

		y0 = A * p_start.T    # These should have the same x value
		y1 = A * p_target.T
		x0 = A * s_start.T
		x1 = A * s_target.T

		ymin, ymax = min(y0[1,0], y1[1,0]), max(y0[1,0], y1[1,0])
		xmin, xmax = min(x0[0,0], x1[0,0]), max(x0[0,0], x1[0,0])

		s = 1 # "Stickiness"

		#r = pygame.Rect(xmin, ymin, xmax - xmin, ymax - ymin)

		#f1 = r.inflate(2,2).collidepoint(X[0,0], X[1,0])
		'''
		for x in range(-1, 2, 1):
			for y in range(-1, 2, 1):
				B = numpy.append(p_normal * p_start.T, s_normal * s_start.T, axis = 0)
				R = A * matrix([[graphics.world_w * x], [graphics.world_h * y]])
				# B is the intersection of the two segments after the transformation if they became lines
				B += R

		'''
		
		f = (xmin - s <= B[0,0] <= xmax + s) and (ymin - s <= B[1,0] <= ymax + s)


		# X is the non-transformed "true" intersection point

		if f:# c:
			if linalg.det(A) == 0:
				X = p_target
			else:
				X = linalg.solve(A, B).T 

			#Let's snip off what we've already travelled
			in_wall_vector = p_target - X # Snipped vector

			'''
			#project stuff from inside the wall to the surface
			iw_projection = numpy.append(X, p_target, axis = 0)*s_dxy.T 
			s_projection = numpy.append(s_start, s_target, axis = 0)*s_dxy.T

			
			pleft, pright = min(iw_projection[0,0], iw_projection[1,0]), max(iw_projection[0,0], iw_projection[1,0])
			sleft, sright = min(s_projection[0,0], s_projection[1,0]), max(s_projection[0,0], s_projection[1,0])

			#If the collision is trivial, we ignore it.
			if pright > pleft >= sright or pleft < pright <= sleft:
				return 0
			'''


			#modify velocity
			vxy = p_dxy / dt

			norm = linalg.norm(s_dxy)
			normalized = s_dxy / norm
			deflected_vxy = normalized * (vxy*normalized.T)[0,0]

			displacement_completed = X - p_start
			distance_travelled = linalg.norm(displacement_completed)
			time_elapsed = distance_travelled / linalg.norm(vxy)

			dt -= time_elapsed
			deflectedpath = deflected_vxy * dt

			return X, deflectedpath, distance_travelled, self.ground, self.normal, deflected_vxy, dt
		return 0

	def push_out(self, p_xy, radius):
		'''checks for intersection of circle with side.
		Returns false if there are no intersections... otherwise returns a new path to travel
		assumption here is that motion is not parallel to surface'''
		test.add_sticky("pushout")

		rotation = matrix([[0,1], [-1,0]])
		#takes (1,0) to (0, -1)
		#takes (0,1) to (1, 0)
		#Like an anticlockwise rotation in our choice of axis
		'''
		#for player
		p_target = p_start + p_dxy#; print p_target
		p_normal = p_dxy * rotation#; print p_normal
		'''
		#for this side
		s_start, s_target = self.side#; print s_start, s_target
		s_dxy = s_target - s_start#; print s_dxy
		s_normal = s_dxy * rotation#; print s_normal

		# Let's find the closest point! We can do this with projection
		# Something that takes (1,0) to s_dxy and (0,1) to s_normal

		G = numpy.append(s_dxy.T, s_normal.T, axis = 1)


		G /= linalg.det(G)**0.5
		# Now just a rotation

		H = linalg.inv(G)
		# rotation that takes s_dxy to x axis

		p0 = H * s_start.T
		p1 = H * s_target.T

		p0 = p0.T
		p1 = p1.T

		q = H * p_xy.T
		# move q and then move T

		cp = matrix([0,0])

		if p0[0,0] > p1[0,0]:
			p0, p1 = p1, p0 # making sure p0 is on left

		if p0[0,0] <= q[0,0] <= p1[0,0]: # If the closest point is on the line
			cp[0,0] = q[0,0]
			cp[0,1] = p0[0,1]
		elif q[0,0] < p0[0,0]:
			cp = p0
		elif p1[0,0] < q[0,0]: # q is on
			cp = p1
		else:
			print "problem: Can't find closest point"

		w = G * cp.T
		test.lines.append(((w[0,0],w[1,0]), (p_xy[0,0], p_xy[0,1])))

		q = q.T
		if linalg.norm(q-cp) < radius:
			if linalg.norm(q-cp) != 0:
				direction = (q-cp) / linalg.norm(q-cp)
			else:
				print "darn! No idea where to project! Modify later to incorporate vxy"
				direction = matrix([1,0])
			q = cp + radius * direction
			p_xy = (G * q.T).T
		
		
		test.remove_sticky("pushout")
		return p_xy

def numbers_overlap(list_1, list_2, wordy = 0):
	'''i1 = [n,m,o,...], i2 = [p,q,r...]
	it basically says whether or not if you connected i1 and i2 there would be areas between all of them'''
	ans = max(list_1) >= min (list_2) and min(list_1) <= max (list_2)
	if wordy: print "numbers_overlaps is looking at", list_1, list_2, "and returns", ans
	return ans
	
def get_projections(plist, sidevector):
	return [p*sidevector.T for p in plist]

def shadows_overlap(plist1, plist2, sidevector, wordy = 0):
	if wordy: print "beginning shadows test"
	g = [get_projections(plist1, sidevector), get_projections(plist2, sidevector)]
	if wordy:
		print "projections are", [[i[0,0] for i in k] for k in g]
	return numbers_overlap(g[0], g[1], wordy)

def overlap_shape(shape_points, plist):
	sidevectors = [shape_points[k] - shape_points[k-1] for k in range(len(shape_points))]
	return all([shadows_overlap(shape_points, plist, sidevector) for sidevector in sidevectors])

def overlap_line(line_points, plist, wordy = 0):
	'''these can be taken as lists of matrices'''
	if wordy: print "\n\n\nbeginning overlap_line"
	rotation = matrix([[0,1], [-1,0]])
	sidevectors = []
	along = line_points[1] - line_points[0]
	sidevectors.append(along)
	if wordy: print "brah my along vector is", along
	normal = along*rotation
	if wordy: print "brah my normal vector is", normal
	sidevectors.append(normal)
	g = [shadows_overlap(line_points, plist, sidevector, wordy) for sidevector in sidevectors]
	if wordy:
		print "Shadow tests say", g[0][0,0], g[1][0,0]
	return all(g)

'''
def find_tiles(line, room):
	# Inefficient as hell!
	tiles = []
	x0, y0 = line[0,0]/32, line[0,1]/32
	x1, y1 = line[1,0]/32, line[1,1]/32

	left = min(x0, x1)
	left = max(0, left)
	right = max(y0, y1)
	right = min (right, room.cols)
	top = min(y0, y1)
	top = max(0, top)
	bottom = max(y0, y1)
	bottom = min(bottom, room.rows)
	for col in range(left, right):
		for row in range(top, bottom):
			t = room.tiles[col][row]
			plist = [matrix([p]) for p in t.pointlist]
			plist = ((0, 0), (32, 0), (32, 32), (0, 32))
			plist = [matrix([p]) for p in plist]
			offset = matrix([[col*32, row*32]])
			plist = [p + offset for p in plist]
			if t.name != "empty" and overlap_line(line, plist):
				tiles.append(((col, row), t))
	return tiles
'''

def find_enough_tiles(my_x, my_y, vx, vy, dt = 1.0, bw = 32.0, bh = 32.0):
	'''returns a set of tiles that cover the path.
	does not return all tiles that the path covers'''
	#print "starting at", my_x, my_y, "ending at", my_x+vx*dt, my_y+vy*dt
	x = int(math.floor(my_x / bw))
	y = int(math.floor(my_y / bh))
	coordlist = [(x,y)]

	xstep = int(math.copysign(1,vx))
	ystep = int(math.copysign(1,vy))

	#print "dt is", dt 
	while dt >= 0:
		#print "2"
		newtiles = []
		if xstep > 0:
			x_to_next = (x + 1)*bw - my_x
		else:
			x_to_next = x*bw - my_x
		if vx == 0:
			t_next_x = float('infinity')
		else:
			t_next_x = x_to_next / vx

		if ystep > 0:
			y_to_next = (y + 1)*bw - my_y
		else:
			y_to_next = y*bw - my_y
		if vy == 0:
			t_next_y = float('infinity')
		else:
			t_next_y = y_to_next / vy

		#print "comparing x time", t_next_x, "with y time", t_next_y
		if t_next_x < t_next_y:
			#print "went x"
			x+=xstep
			dt -= t_next_x
			my_x += vx*t_next_x #This might sometimes create a nan.
			my_y += vy*t_next_x
		elif t_next_x > t_next_y:
			#print "went y"
			y+=ystep
			dt -= t_next_y
			my_y += vy*t_next_y
			my_x += vx*t_next_y
		else:
			#print "it takes the same time to go x,", t_next_x, "as it does to go y,", t_next_y 
			#newtiles.append((x, y+ystep))
			#newtiles.append((x+xstep, y))
			y+=ystep
			x+=xstep
			dt -= t_next_y
			my_y += vy*t_next_y
			my_x += vx*t_next_y

		newtiles.append((x,y))

		if dt >= 0:# Only record places that you've travelled with nonnegative time.
			coordlist.extend(newtiles)
		#print "remaining time is", dt
	#print "phew, coordlist", coordlist
	return coordlist

def find_tiles_rect(my_x, my_y, vx, vy, dt = 1.0, bw = 32.0, bh = 32.0):
	'''returns all tiles that a rectangle / line
	covers'''

	'''
	# Find boundaries
	left, right = min(my_x, my_x + vx*dt), max(my_x, my_x + vx*dt)
	top, bottom = min(my_y, my_y + vy*dt), max(my_y, my_y + vy*dt)

	# Scale down
	left /= bw
	right /= bw
	top /= bh
	bottom /=bh

	# Get the (inclusive boundaries)
	tleft = math.ceil(left) - 1
	tright = math.floor(right)
	ttop = math.ceil(top) - 1
	tbottom = math.floor(bottom)

	# Integer-ify
	tleft = int(tleft)
	tright = int(tright)
	ttop = int(ttop)
	tbottom = int(tbottom)
	'''
	try:
		lol = int(my_x)
	except:
		print "problem with my_x:", my_x

	startx = int(my_x / bw)
	starty = int(my_y / bh)
	endx = int((my_x + vx*dt) / bw)
	endy = int((my_y + vy*dt) / bh)

	xstep = int(math.copysign(1,vx))
	ystep = int(math.copysign(1,vy))

	coordlist = [(x, y) for x in range(startx, endx+xstep, xstep) for y in range(starty, endy + ystep, ystep)]# Basically tleft <= x <= tright, ttop <= y <= tbottom 
	#if len(coordlist) > 10:
	#	print "why is the coordlist so long?", coordlist
	return coordlist

def find_all_tiles(my_x, my_y, vx, vy, dt = 1.0, bw = 32.0, bh = 32.0):
	'''returns ALL tiles that cover the path, even by just an edge or point.
	starting to modify so that they are returned approximately in order'''
	# Trivial case where either vx or vy is zero
	if vx == 0 or vy == 0:
		return find_tiles_rect(my_x, my_y, vx, vy, dt, bw, bh)
	# If the above if statement is false we may assume vx != 0 and vy != 0

	# Find the starting position
	x = int(math.floor(my_x / bw))
	y = int(math.floor(my_y / bh))

	coordlist = find_tiles_rect(my_x, my_y, 0.0, 0.0, dt, bw, bh) # Include everthing touching the starting point.
	coordlist.extend(find_tiles_rect(my_x + vx*dt, my_y + vy*dt, 0.0, 0.0, dt, bw, bh)) # Include everything touching the end point.

	xstep = int(math.copysign(1,vx))
	ystep = int(math.copysign(1,vy))

	#print "dt is", dt
	a = 0 
	while dt >= 0 and a < 20:
		a += 1
		newtiles = []

		x_to_next = (x + (xstep > 0))*bw - my_x

		if vx == 0: # With current setting this is never going to happen, so this really is optional.
			t_next_x = float('infinity'); print "Hey, vx isn't supposed to be zero"
		else:
			t_next_x = x_to_next / vx

		y_to_next = (y + (ystep > 0))*bh - my_y
		
		if vy == 0: # With current setting this is never going to happen, so this really is optional.
			t_next_y = float('infinity'); print "Hey, vy isn't supposed to be zero"
		else:
			t_next_y = y_to_next / vy

		#print x_to_next, vx, y_to_next, vy
		#if t_next_x < 0 or t_next_y < 0:
			#print x_to_next, vx, y_to_next, vy, "comparing x time", t_next_x, "with y time", t_next_y

		if t_next_x < t_next_y:
			#print "went x"
			x+=xstep
			dt -= t_next_x
			my_x += vx*t_next_x #This might sometimes create a nan.
			my_y += vy*t_next_x
		elif t_next_x > t_next_y:
			#print "went y"
			y+=ystep
			dt -= t_next_y
			my_y += vy*t_next_y
			my_x += vx*t_next_y
		else:
			#print "it takes the same time to go x,", t_next_x, "as it does to go y,", t_next_y 
			newtiles.append((x, y+ystep))
			newtiles.append((x+xstep, y))
			y+=ystep
			x+=xstep
			dt -= t_next_y
			my_y += vy*t_next_y
			my_x += vx*t_next_y


		x0 = x % (graphics.world_w / bw)
		y0 = y % (graphics.world_h / bh)
		x0 = int(x0)
		y0 = int(y0)
		#test.tiles.append((x0,y0))
		newtiles.append((x0, y0))

		if 1:#dt >= 0:# Only record places that you've travelled with nonnegative time.
			coordlist.extend(newtiles)
		#print "remaining time is", dt
	#print "final coordlist", coordlist
	coordlist = list(set(coordlist)) # I'm too lazy to use the proper OrderedDict because dictionaries are scary.
	#print "bam, finished"
	return coordlist




