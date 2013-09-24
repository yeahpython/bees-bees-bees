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

levels = ["simple room.txt", "sidescrolling.txt", "fun.txt", "hill.txt", "dumb room.txt"]

def initialization():
	pygame.init()
	pygame.display.set_mode(graphics.screen_size)
	pygame.display.set_caption(game_title)
	tile.init()

def preparelevel(screen, level):
	graphics.load(os.path.join("data", "rooms", level))
	world = pygame.Surface((graphics.world_w, graphics.world_h))
	t = topbar.TopBar(screen)
	r = room.load(os.path.join("data", "rooms", level))
	test.mark(r.background)
	r.topbar = t
	return world, t, r

def enteredlevel():
	messages.say("Paused. [0,1,2,3,4]", 0)
	shortcuts = {pygame.K_0:0, pygame.K_1:1, pygame.K_2:2, pygame.K_3:3, pygame.K_4:4}

	clock = pygame.time.Clock()
	n = None
	while True:
		clock.tick(60)
		key_presses = pygame.event.get(pygame.KEYDOWN)
		key_states = pygame.key.get_pressed()
		for k in shortcuts.keys():
			if key_states[k]:
				n = shortcuts[k]
				return levels[n]

def main_loop():
	'''these things only need to happen once'''
	screen = pygame.display.get_surface()
	messages.screen = screen
	clock = pygame.time.Clock()
	dt=0
	font = pygame.font.Font(None, 30)

	'''these are level-specific'''
	level = enteredlevel()
	world, t, r = preparelevel(screen, level)
	p = player.Player(r)

	h = zoo.Beehive()
	#h = zoo.Beehive("the fact that any argument is passed here means that I'll load saved bees")

	c = camera.Camera(p, world, screen, r)

	#Generating new bees
	r.bees = h.preserved_bees(r, p)
	r.generate_bees(r.beecap)
	r.h = h
	for b in r.bees:
		b.randomize_position()

	'''there are things I want to keep between levels. Like the bees.'''

	while True: # Main game loop
		print ""

		test.begin_timing(test.segs, test.segdescriptors)
		world.blit(r.background, (0,0))

		#Handle quitting
		if pygame.event.get(pygame.QUIT):
			return
		#Handle player input
		key_presses = pygame.event.get(pygame.KEYDOWN)
		key_states = pygame.key.get_pressed()

		if key_states[pygame.K_p]:
			test.backgroundmarkers = []

			level = enteredlevel()

			world, t, r2 = preparelevel(screen, level)
			p = player.Player(r2)

			r2.bees = r.bees

			r = r2
			h = zoo.Beehive()
			#h = zoo.Beehive("the fact that any argument is passed here means that I'll load saved bees")
			c = camera.Camera(p, world, screen, r)
			r.h = h
			for b in r.bees:
				b.room = r
				b.player = p
				b.randomize_position()

		#test.record("stuff")
		#test.add_sticky('drawing', 'erase')
		# Clean up

		for phys in [p] + r.food + r.bees + r.bullets:
			phys.erase()

		r.repair(world)

		#test.record("stuff")
		#test.remove_sticky('drawing', 'erase')

		

		#test.add_sticky('update')

		#Update
		for phys in [p] + r.food + r.bees + r.bullets:
			phys.update(dt, key_states, key_presses)




		r.update() # Necessarily comes afterwards so that the bees can see the player

		#test.record("room")

		#test.remove_sticky('update')

		c.follow_player(dt) # Here so that room knows what to draw
		c.updatesight()

		#test.record("moving the camera")
		
		test.draw(world, r)

		#test.add_sticky('drawing')
		for x in r.bees + r.food + [p] + r.bullets:
			x.draw(world)
		#dirtiness += 1
		#test.remove_sticky('drawing')
		
		

		
		# Time
		dt = clock.tick(400)
		#dt = min(dt, 100)
		#print int(clock.get_fps()),

		#test.record("extras")

		#c.follow_player(dt)
		c.draw()
		#test.record('drawing', "camera")

		ta = "total bees: " + str(r.beehistory)
		tb = " | current bees: " + str(len(r.bees))
		tc = " |" + str(int(clock.get_fps()))+"fps"
		gr = " grounded is " + str(p.grounded)

		t.permanent_text = ta + tb + tc
		t.data.append(clock.get_fps())
		t.draw(screen)
		pygame.display.flip()
		
		#test.record('drawing', "topbar")


		for phys in r.bees + r.food + [p]:
			phys.visible = c.can_see(phys)

		#test.record("visibility")

		test.summarizetimings(test.segs, test.segdescriptors)

def main():
	initialization()

	pygame.event.set_blocked(None)
	pygame.event.set_allowed(pygame.QUIT)

	main_loop()