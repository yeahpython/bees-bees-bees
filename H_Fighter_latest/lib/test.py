import pygame
import graphics
from graphics import bw, bh
import numpy
from numpy import array, linalg, matrix
import collision
import time
import string

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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
SHOW_LINES = 1
LINE_MEMORY = 5
SHOW_TILES = 1
SHOW_BACKGROUND_MARKERS = 1
SHOW_TEXT = 1


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

def record(*args):
	'''this will register the time between the last call to record and this overlap_line
	as being spent on args'''
	if frames[0] % 30:
		return
	segs.append(time.time())
	segdescriptors.append(args)
	segdescriptors[-1] = segdescriptors[-1] + tuple(stickylabels)

def add_sticky(*args):
	if frames[0] % 30:
		return
	record()
	stickylabels.extend(args)

def remove_sticky(*args):
	if frames[0] % 30:
		return
	record()
	for label in args:
		stickylabels.remove(label)

# sort by parent and then by time
def decorator(x):
	i = string.rfind(x[1], ":");
	if i != -1:
		return x[1][:i], -x[0]
	else:
		return x[1], -x[0]

def summarizetimings(segs, segdescriptors):
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
			if i >= len(w):
				print "error with length", len(segdescriptors), len(w) 
			for key in keys:
				try:
					totaldict[key] += w[i] / total * 100
				except:
					try:
						totaldict[key] = w[i] / total * 100
					except:
						print "error: probably accidentally forgot to close a sticky label or something"

		wolo = []

		n = 20
		stardict = {task:" "*n for task,time in totaldict.iteritems()}
		timeThresholds = [segs[0] + total / n * i for i in range(n)]
		curr = 0
		for i, keys in enumerate(segdescriptors):
			if segs[i] >= timeThresholds[curr]:
				for key in keys:
					index = int((segs[i] - segs[0]) * n / total)
					if index < 0:
						index = 0
					if index >= n:
						index = n-1
					stardict[key] = stardict[key][:index] + "*" + stardict[key][index+1:]
				curr += 1
				if curr >= len(timeThresholds):
					break


		for task, time in totaldict.iteritems():
			a = [time]
			g = task[:]
			while (True):
				i = string.rfind(g, ":")
				if i == -1:
					break
				g = g[:i]
				if g not in totaldict:
					break
				a.append(totaldict[g]) # append the time of its parent

			wolo.append( (time,task, [-x for x in a[::-1]]) )

		wolo.sort(key = lambda x: x[2]) 
		#wolo.sort(key = decorator) 

		print "time taken was", total, "seconds"

		for v, k, a in wolo:
			
			#n_stars = int(v) * total_stars / 100
			#print (total_stars-n_stars)*" " + n_stars*("*"),
			print stardict[k],
			print "%4.1f" % v,
			i = string.rfind(k, ":")
			if i != -1:
				if (k[:i]) in totaldict:
					print " "*i+bcolors.OKGREEN + k[i:]+ bcolors.ENDC
				else:
					print k[:i]+bcolors.OKGREEN + k[i:]+ bcolors.ENDC
			else:
				print bcolors.OKGREEN+ k+ bcolors.ENDC
	segs = []
	segdescriptors = []
	frames[0] += 1

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
			pygame.draw.line(surface, (0,255,0), p1, p2, 1)
		lines = []
		'''
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
						# a,b = p1
						# a = max(a, -10000)
						# a = min(a, 10000)
						# b = max(b, -10000)
						# b = min(b, 10000)
						# p1 = a,b

						# a,b = p2
						# a = max(a, -10000)
						# a = min(a, 10000)
						# b = max(b, -10000)
						# b = min(b, 10000)
						# p2 = a,b
						pygame.draw.line(surface, (0,255,0), p1, p2, 1)
					except:
						print "bad bad bad"
		lines = lines[-LINE_MEMORY:]
		'''

	for x,y in tiles:
		try:
			r = pygame.Rect(x*bw, y*bh,bw+1,bh+1)
			#room.dirtyareas.append(r)
			if SHOW_TILES:
				pygame.draw.rect(surface, (0, 0, 255), r, 1)
		except:
			print "test.tiles hates this tile", x, y
	tiles = []