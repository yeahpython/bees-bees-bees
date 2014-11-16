import pygame
import graphics
from graphics import bw, bh
import numpy
from numpy import array, linalg, matrix
import collision
import time

sides = []
vectors = [(0,0), (0,0)]
indicators = []
lines = []
tiles = []
backgroundmarkers = []
#^^^^^^^^^^^^^^^^^^
backgroundpointmarkers = []

#show = [0,     0,           0,          0,       0,      1,                     0]
#     sides   vectors   indicators     lines   tiles   backgroundmarkers       text

SHOW_SIDES = 0
SHOW_VECTORS = 0
SHOW_INDICATORS = 0
SHOW_LINES = 0
SHOW_TILES = 0
SHOW_BACKGROUND_MARKERS = 0
SHOW_TEXT = 0


segs = [] #a list of times
segdescriptors = [] # a list of descriptors or hashtags to say what's happening during the time
stickylabels = []

frames = [0]

def clear_tests():
	sides = []
	vectors = [(0,0), (0,0)]
	indicators = []
	lines = []
	tiles = []
	backgroundmarkers = []
	backgroundpointmarkers = []
	segs = [] #a list of times
	segdescriptors = [] # a list of descriptors or hashtags to say what's happening during the time
	stickylabels = []

def begin_timing(segs, segdescriptors):
	segs[:] = [time.time()]
	segdescriptors[:] = []

def add_sticky(*args):
	stickylabels.extend(args)

def remove_sticky(*args):
	for label in args:
		stickylabels.remove(label)

def record(*args):
	'''this will register the time between the last call to record and this overlap_line
	as being spent on args'''
	segs.append(time.time())
	segdescriptors.append(args)
	segdescriptors[-1] = segdescriptors[-1] + tuple(stickylabels)

def summarizetimings(segs, segdescriptors):
	frames[0] += 1
	if SHOW_TEXT and not frames[0] % 30:
		record("end")

		total = segs[-1] - segs[0]
		w = [segs[k+1] - segs[k] for k in range(len(segs) - 1)]
		#print "total time was", total
		#for i, k in enumerate(w):
		#	print int(w[i] * 10000000), w[i] / total * 100, "%", segdescriptors[i]
		print "\n\n\n"

		totaldict = {}

		for i, keys in enumerate(segdescriptors):
			for key in keys:
				try:
					totaldict[key] += w[i] / total * 100
				except:
					totaldict[key] = w[i] / total * 100

		wolo = []

		for k, v in totaldict.iteritems():
			wolo.append( (v,k) )

		wolo.sort(key = lambda x: x[0])

		print "time taken was", total, "seconds"
		for v, k in wolo:
			print "{0}%".format(round(v, 3)), k

	segs = []
	segdescriptors = []

def normtuple(x,y):
	return (x**2 + y**2)

def mark(background):
	if not SHOW_BACKGROUND_MARKERS:
		return

	for p1, p2 in backgroundmarkers:
		w = []
		for x in range(-1, 2, 1):
			for y in range(-1, 2, 1):
				p_1 = p1
				p_2 = p2[0] + x*graphics.world_w, p2[1] + y*graphics.world_h
				w.append((p_1, p_2))
		#print w
		g = min([ normtuple(p2[0]-p1[0], p2[1] - p1[1]) for p1, p2 in w])

		for p1, p2 in w:
			a = normtuple(p2[0]-p1[0], p2[1]-p1[1])
			if a == g:
				try:
					pygame.draw.line(background, (255,0,0), p1, p2, 1)
				except:
					pass

	for p in backgroundpointmarkers:
		pygame.draw.circle(background, (0,255,0), [int(x) for x in p], 5, 0)


def draw(surface, room):
	# Sides I'm colliding with
	global sides
	global vectors
	global indicators
	global lines
	global tiles


	'''p_p0 = [100,0]
	p_p1 = [100,100]
	s_p0 = [0,100]
	s_p1 = [50,50]


	pp_p0 = matrix(p_p0).astype(numpy.float64)
	pp_p1 = matrix(p_p1).astype(numpy.float64)
	ss_p0 = matrix(s_p0).astype(numpy.float64)
	ss_p1 = matrix(s_p1).astype(numpy.float64)

	c = None
	if collision.overlap_line([ss_p0, ss_p1], [pp_p0, pp_p1], wordy = 1) and collision.overlap_line( [pp_p0, pp_p1], [ss_p0, ss_p1], wordy = 1):
		c = (0,255,0)
	else:
		c = (255, 0, 0)

	pygame.draw.line(surface, c, p_p0, p_p1, 1)
	pygame.draw.line(surface, c, s_p0, s_p1, 1)'''




	if SHOW_SIDES:
		for i, layer in enumerate(sides):
			for side in layer:
				color = graphics.colorcycle[i%len(graphics.colorcycle)]
				pygame.draw.line(surface, color, array(side.side[0])[0], array(side.side[1])[0], 7)
	sides = []

	if SHOW_VECTORS:
		for i, (d_x, d_y) in enumerate(vectors):
			spacing = 50
			ox = 50
			oy = 50
			mx = graphics.screen_w - ox
			cols = (mx - ox) / spacing
			x,y = i % cols, i / cols
			startxy = (x * spacing + ox, y * spacing + oy)
			sx, sy = startxy

			norm = (d_x**2 + d_y**2)**0.5
			if norm == 0:
				continue

			d_x /= norm
			d_y /= norm

			d_x *= 15
			d_y *= 15

			pygame.draw.circle(surface, (51, 255, 204), startxy, 20)
			pygame.draw.circle(surface, (40, 40, 40), startxy, 17)
			pygame.draw.line(surface, (41, 255, 204), startxy, (sx + d_x, sy + d_y), 1)
	vectors = [(0,0)]

	if SHOW_INDICATORS:
		for i, value in enumerate(indicators):
			pygame.draw.circle(surface, (255,51,102), ((i+1)*graphics.screen_w/(len(indicators) + 1), 16), int(value))

	if SHOW_LINES:
		for p1, p2 in lines:
			w = []
			for x in range(-1, 2, 1):
				for y in range(-1, 2, 1):
					p_1 = p1
					p_2 = p2[0] + x*graphics.world_w, p2[1] + y*graphics.world_h
					w.append((p_1, p_2))
			#print w
			g = min([ normtuple(p2[0]-p1[0], p2[1] - p1[1]) for p1, p2 in w])

			for p1, p2 in w:
				a = normtuple(p2[0]-p1[0], p2[1]-p1[1])
				if a == g:
					try:
						"""
						a,b = p1
						a = max(a, -10000)
						a = min(a, 10000)
						b = max(b, -10000)
						b = min(b, 10000)
						p1 = a,b

						a,b = p2
						a = max(a, -10000)
						a = min(a, 10000)
						b = max(b, -10000)
						b = min(b, 10000)
						p2 = a,b
						"""
						pygame.draw.line(surface, (255,0,0), p1, p2, 1)
					except:
						print "bad bad bad"
	lines = lines[-100:]

	for x,y in tiles:
		try:
			r = pygame.Rect(x*bw, y*bh,bw,bh)
			#room.dirtyareas.append(r)
			if SHOW_TILES:
				pygame.draw.rect(surface, (0, 0, 255), r, 1)
		except:
			print "test.tiles hates this tile", x, y
	tiles = []