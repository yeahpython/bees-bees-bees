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
	r.topbar.s = 0 #
	r.topbar.saved_text_images = [] #
	r.player = 0 #
	r.pixels = 0 #

	for b in r.bees:
		b.decoration = 0#
		b.tag = 0#
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