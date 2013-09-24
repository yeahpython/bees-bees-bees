import pickle
import os
import pygame
if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

from numpy import array, linalg, matrix
import random
import copy


import bee
import player
import graphics
import room
import tile
import collision
import test
import messages
import food
import camera
import topbar
import brain
import zoo
import time



game_title = "evade"
level = "flat room.txt"

def initialization():
	pygame.init()
	pygame.display.set_mode(graphics.screen_size)
	pygame.display.set_caption(game_title)
	tile.init()

def main_loop():
	#display variables
	screen = pygame.display.get_surface()
	messages.screen = screen
	graphics.load(os.path.join("data", "rooms", level))
	world = pygame.Surface((graphics.world_w, graphics.world_h))
	messages.say("evade", 0)

	'''message variables'''
	font = pygame.font.Font(None, 30)


	t = topbar.TopBar(screen)
	r = room.load(os.path.join("data", "rooms", level)) 
	test.mark(r.background)
	r.topbar = t

	'''player variables'''
	p = player.Player(r)
	lifetimes = []
	p.place(r.start_position)
	p.randomize_position()

	r.player = p

	h = zoo.Beehive()
	#h = zoo.Beehive("the fact that any argument is passed here means that I'll load saved bees")
	#print "loaded", len(h.specimens), "specimens",
	#for k in h.specimens:
	#	print k[0] + k[1] + ", ",
	#print ""

	r.food = []
	r.bees = []

	clock = pygame.time.Clock()
	dt=0

	dirtiness = float('infinity')
	allowed_dirty = 1

	c = camera.Camera(p, world, screen, r)
	c.xy = p.xy + matrix([0,0])

	#Generating new bees
	r.bees = h.build_bees(r, p)
	r.generate_bees(r.beecap)
	r.h = h

	nn = 0
	
	for b in r.bees:
		b.randomize_position()
	brain_number = 0
	bestbees = []
	while True: # Main game loop
		test.begin_timing(test.segs, test.segdescriptors)

		if nn == 0:
			world.blit(r.background, (0,0))
			nn = 100000
		else:
			nn -= 1

		#Handle quitting
		if pygame.event.get(pygame.QUIT):
			return
		#Handle player input
		key_presses = pygame.event.get(pygame.KEYDOWN)
		key_states = pygame.key.get_pressed()
		test.record("stuff")
		test.add_sticky('drawing', 'erase')
		# Clean up


		for phys in [p] + r.food + r.bees + r.bullets:
			phys.erase()


		if dirtiness>=allowed_dirty or graphics.REDRAW_ROOM:
			r.draw2(world)

			dirtiness = 0

		test.record("stuff")
		test.remove_sticky('drawing', 'erase')

		

		test.add_sticky('update')

		#Update
		for phys in [p] + r.food + r.bees + r.bullets:
			phys.update(dt, key_states, key_presses)




		r.update() # Necessarily comes afterwards so that the bees can see the player

		test.record("room")

		test.remove_sticky('update')

		c.follow_player(dt) # Here so that room knows what to draw
		c.updatesight()

		test.record("moving the camera")
		
		test.draw(world, r)

		test.add_sticky('drawing')
		for x in r.bees + r.food + [p] + r.bullets:
			x.draw(world)
		dirtiness += 1
		test.remove_sticky('drawing')
		
		

		
		# Time
		dt = clock.tick(400)
		#dt = min(dt, 100)
		#print int(clock.get_fps()),

		test.record("extras")

		#c.follow_player(dt)
		c.draw()
		test.record('drawing', "camera")

		ta = "total bees: " + str(r.beehistory)
		tb = " | current bees: " + str(len(r.bees))
		tc = " |" + str(int(clock.get_fps()))+"fps"
		gr = " grounded is " + str(p.grounded)

		t.permanent_text = ta + tb + tc
		if nn%10 == 5:
			t.data.append(clock.get_fps())
		t.draw(screen)
		pygame.display.flip()
		
		test.record('drawing', "topbar")


		for phys in r.bees + r.food + [p]:
			phys.visible = c.can_see(phys)

		test.record("visibility")

		test.summarizetimings(test.segs, test.segdescriptors)

		mm = int(p.xy[0,0]/graphics.bw)
		nn = int(p.xy[0,1]/graphics.bh)
		#print r.visiondirectory[mm][nn]

def main():
	initialization()

	pygame.event.set_blocked(None)
	pygame.event.set_allowed(pygame.QUIT)

	main_loop()