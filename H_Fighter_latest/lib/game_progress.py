import os
import pickle
import graphics
import pygame

time_to_quit = False

def save_game(r):
	g = open(os.path.join("data", "saved", "room.txt"), "wb")
	r.background = 0 #
	r.collisionfield = 0 #
	r.camera = 0 #
	r.topbar.saved_text_images = [] #
	r.topbar.s = 0
	r.player = 0 #
	r.pixels = 0 #

	for b in r.bees + r.deadbees:
		b.decoration = 0#
		b.tag = 0#
		b.objectsinview = []
	#r.bees =[]
	#r.deadbees = []

	#r.object_directory = [[[] for x in y] for y in r.object_directory]
	#r.visibles = []
	#r.bestbees = []
	'''
	r.a = 0
	r.adjust_convexes = 0
	r.background = 0
	r.beehistory = 0
	r.bees = 0
	r.bestbees = 0
	r.bgh = 0
	r.bgw = 0
	r.bullets = 0
	r.camera = 0
	r.collisionfield = 0
	r.cols = 0
	r.compute_densities = 0
	r.convex_directory = 0
	r.deadbees = 0
	r.dirtyareas = 0
	r.draw = 0
	r.food = 0
	r.freespots = 0
	r.generate_bees = 0
	r.get_sides = 0
	r.give_tiles_better_sides = 0
	r.globalize_dimensions = 0
	r.h = 0
	r.lines = 0
	r.madness = 0
	r.object_directory = 0
	r.optimize_convexes = 0
	r.painter = 0
	r.pixels = 0
	r.player = 0
	r.pointcheck = 0
	r.precompute_vision = 0
	r.recentdeaths = 0
	r.reduce_sides = 0
	r.repair = 0
	r.roomnumber = 0
	r.rows = 0
	r.side_directory = 0
	r.sidelabels = 0
	r.sides = 0
	r.signal_new_tree = 0
	r.start_position = 0
	r.stasis = 0
	r.tiles = 0
	r.timetosave = 0
	r.topbar = 0
	r.update = 0
	r.visibles = 0
	r.visiondirectory = 0
	'''
		

	pickle.dump(r, g)
	g.close()

def load_game():
	g = open(os.path.join("data", "saved", "room.txt"))
	try:
		print "\nTrying to load saved game."
		r = pickle.load(g)
		print 0,
		graphics.extract_dimensions(r.lines)
		print 1,
		r.background = pygame.Surface((graphics.world_w, graphics.world_h))
		print 2,
		r.collisionfield = pygame.Surface((graphics.world_w, graphics.world_h))
		print 3,
		r.pixels = pygame.PixelArray(r.collisionfield)
		print 3.5,
		r.globalize_dimensions()
		print 4,
		r.draw(r.background) # Note that this sets the start position to wherever the '!' is
		print 5,
		r.background.convert()
		print 6,
		r.draw(r.collisionfield, collision_only = 1)
		print 7,
		r.collisionfield.convert()
		print 8,
		r.pixels = pygame.PixelArray(r.collisionfield)
		print 9,
		for b in r.bees:
			b.update_eyes()
		print "10, let's go!"
		print "\n\n* * * * * * Loaded Saved Game * * * * * *"
		return r
	except:
		print "Failed to load saved game"

	g.close()
	return 0