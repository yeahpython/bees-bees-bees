import pickle
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)

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
from numpy import linalg
from random import choice
import settings


game_title = "evade"

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

def getString(allowed_keys = [], string = ""):
	font = pygame.font.Font(None, 30)
	box = pygame.Rect(0, 0, 300, 50)
	box.centerx = graphics.screen_w / 2
	box.centery = graphics.screen_h / 2
	s = pygame.display.get_surface()

	pygame.draw.rect(s, graphics.foreground, box, 0)
	pygame.draw.rect(s, [255, 255, 255], box, 1)
	pygame.display.flip()
	clock = pygame.time.Clock()
	previous_key_states = []
	key_downs = []
	redraw = 1

	if not(allowed_keys):
		for key in range(pygame.K_a, pygame.K_z + 1):
			allowed_keys.append(key)
		allowed_keys.append(pygame.K_SPACE)

	allowed_keys += [pygame.K_BACKSPACE, pygame.K_RETURN]

	while not pygame.event.get(pygame.QUIT):
		clock.tick(60)
		key_states = pygame.key.get_pressed()
		if previous_key_states:
			key_downs = [new and not old for new, old in zip(key_states, previous_key_states)]
		else:
			key_downs = [0 for x in key_states]

		for key in allowed_keys:
			if key_downs[key]:
				if key == pygame.K_BACKSPACE:
					string = string[:-1]
				elif key == pygame.K_RETURN:
					return string
				elif len(string) < 20:
					if key == pygame.K_SPACE:
						string += " "
					else:
						string += pygame.key.name(key)
				redraw = 1

		if redraw:
			text = font.render(string, 1, [255, 255, 255])
			textpos = text.get_rect(centerx = s.get_width()/2, centery = s.get_height()/2)
			pygame.draw.rect(s, graphics.foreground, box, 0)
			#box = text.get_rect(centerx = s.get_width()/2, height = 50, centery = s.get_height()/2)
			pygame.draw.rect(s, [255, 255, 255], box, 1)
			s.blit(text, textpos)
			pygame.display.flip()
			redraw = 0

		previous_key_states = key_states[:]
		pygame.event.pump()

def waitForEnter():
	messages.say("Press [enter] to continue", down = 1)
	pygame.display.flip()
	clock = pygame.time.Clock()
	while not pygame.event.get(pygame.QUIT):
		clock.tick(60)
		key_states = pygame.key.get_pressed()
		if key_states[pygame.K_RETURN]:
			break
		pygame.event.pump()

def waitForKey(key):
	messages.say("Press " + pygame.key.name(key) +" to exit", down = 1)
	pygame.display.flip()
	clock = pygame.time.Clock()
	while not pygame.event.get(pygame.QUIT):
		clock.tick(60)
		key_states = pygame.key.get_pressed()
		if key_states[key]:
			break
		pygame.event.pump()

def getChoice(title, options):
	messages.colorBackground()
	messages.say(title)
	messagecount = 1
	for key, meaning in options.iteritems():
		messagecount = messages.say("[" + pygame.key.name(key) + "]: " + meaning, down = messagecount)
	pygame.display.flip()
	clock = pygame.time.Clock()
	n = None
	while not pygame.event.get(pygame.QUIT):
		clock.tick(60)
		key_presses = pygame.event.get(pygame.KEYDOWN)
		key_states = pygame.key.get_pressed()
		for key in options:
			if key_states[key]:
				return key
		pygame.event.pump()

def getChoiceUnbounded(title, options):
	
	clock = pygame.time.Clock()
	n = None

	messages_per_page = 3

	currpos = 0
	currpage = 0
	updateview = 1

	hborder = 15

	optiondisplay = pygame.Surface((min(300, graphics.screen_w - 2*hborder), 15 * (len(options) + 3)))
	#selectionimage = pygame.Surface((50, 50), flags = pygame.SRCALPHA)
	#pygame.draw.circle(selectionimage, [255, 0, 0], [25, 25], 10, 0)
	selectionimage = pygame.Surface((optiondisplay.get_width() - 10, 50), flags = pygame.SRCALPHA)

	box = pygame.Rect((0,0), (selectionimage.get_width() - 10, 15))
	pygame.draw.rect(selectionimage, [255, 255, 255], box, 1)

	smallsteps = 0
	slowness = 6

	previous_key_states = []

	while not pygame.event.get(pygame.QUIT):
		if updateview:
			messages.colorBackground(surface = optiondisplay)
			messages.say(title, surface = optiondisplay, size = "small")
			messagecount = 1
			for choice in options:
				messagecount = messages.say(choice, down = messagecount, surface = optiondisplay, size = "small")
			disp = pygame.display.get_surface()

			optionx = hborder
			optiony = graphics.screen_h - 15 * (len(options) + 4)
			optionpos = optionx, optiony

			dest = optiondisplay.get_rect(centerx = graphics.screen_w / 2, centery = graphics.screen_h / 2)

			disp.blit(optiondisplay, dest, special_flags = 0)

			disp.blit(selectionimage, (dest.x + 5, dest.y + 35 + currpos * 15))

			pygame.display.flip()
			updateview = 0

		clock.tick(60)

		'''stupid mac...'''
		#key_presses = pygame.event.get()
		key_states = pygame.key.get_pressed()
		#event = pygame.event.poll()
		pygame.event.pump()

		#if event.type != pygame.NOEVENT:
		#	print event

		#if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
		if key_states[pygame.K_UP]:
			smallsteps -= 1
			if smallsteps == 0 or (previous_key_states and not previous_key_states[pygame.K_UP]):
				smallsteps = slowness
				if currpos > 0:
					currpos -= 1
					updateview = 1

		#if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
		elif key_states[pygame.K_DOWN]:
			smallsteps -= 1
			if smallsteps == 0 or (previous_key_states and not previous_key_states[pygame.K_DOWN]):
				smallsteps = slowness
				if currpos < len(options) - 1:
					currpos += 1
					updateview = 1

		elif key_states[pygame.K_RETURN] and (previous_key_states and not previous_key_states[pygame.K_RETURN]):
			return options[currpos]

		elif key_states[pygame.K_q]:
			return

		previous_key_states = key_states[:]


levels = ["5.txt", "1.txt", "ringmap.txt", "3.txt", "dumb room.txt"]

files = {
	"tiny debugger" : 1,
	"ring map" : 2,
	"vertical map" : 3,
	"horizontal map" : 4,
	"huge map" : 0,
}

def enteredlevel(allowcancel = 1):
 	options = ["tiny debugger", "ring map", "vertical map", "horizontal map", "huge map", "quit"]
	if allowcancel:
		options += ["cancel"]

	choice = getChoiceUnbounded("Select a level (UP / DOWN / ENTER):", options)
	if choice in files:
		return levels[files[choice]]
	return choice

def fiddle(tens, units):
	return 10 * tens + units

def main_loop():
	'''these things only need to happen once'''
	screen = pygame.display.get_surface()
	screen.fill([120,255,200])


	messages.screen = screen

	clock = pygame.time.Clock()
	dt=0
	font = pygame.font.Font(None, 30)

	'''these are level-specific'''
	level = enteredlevel(allowcancel = 0)
	if level == "quit":
		return
	world, t, r = preparelevel(screen, level)
	p = player.Player(r)


	#h = zoo.Beehive()
	h = zoo.Beehive("the fact that any argument is passed here means that I'll load saved bees")

	

	c = camera.Camera(p, world, screen, r)

	#Generating new bees
	r.bees = []
	#r.bees = h.preserved_bees(r, p)

	r.generate_bees(r.beecap)
	r.h = h
	for b in r.bees:
		b.randomize_position()

	'''loadedbeenames = []
				for b in h.specimens:
					loadedbeenames.append(b[0])
			
				loadedbeenames.append("cancel")
			
				x = getChoiceUnbounded("Here are the saved bees", loadedbeenames)'''

	framecount = 0
	while not pygame.event.get(pygame.QUIT): # Main game loop
		framecount += 1

		test.begin_timing(test.segs, test.segdescriptors)
		world.blit(r.background, (0,0))

		#Handle player input
		key_presses = pygame.event.get(pygame.KEYDOWN)
		key_states = pygame.key.get_pressed()

		'''when you press o'''
		if key_states[pygame.K_o]:
			options = ["Move to another map", "Examine bee", "Save bees", "Load bees", "Tweak variables", "Modify map", "Back", "Quit"]
			choice = getChoiceUnbounded("select option", options)

			if choice != "Back":
				if choice == "Quit":
					return

				elif choice == "Move to another map":
					level = enteredlevel()
					if level == "quit":
						return

					if level != "cancel":
						print level
						test.clear_tests()
						world, t, r2 = preparelevel(screen, level)
						p = player.Player(r2)

						r2.bees = r.bees

						r = r2
						h = zoo.Beehive()
						#h = zoo.Beehive("the fact that any argument is passed here means that I'll load saved bees")
						c = camera.Camera(p, world, screen, r)
						c.xy = 1 * p.xy
						r.h = h
						for b in r.bees:
							b.lastnonwall = matrix([[-1.0, 0.0]])
							b.madness = 0
							b.room = r
							b.player = p
							b.randomize_position()

				elif choice == "Examine bee":
					'''this thing lets you examine the closest bee to you'''
					if r.bees:
						minbee = r.bees[0]
						for b in r.bees:
							if linalg.norm(b.xy - p.xy) < linalg.norm(minbee.xy - p.xy):
								minbee = b
						for phys in [p] + r.food + r.bees + r.bullets:
							phys.erase()

						r.repair(world)
						for x in r.bees + r.food + [p] + r.bullets:
							x.draw(world)
						c.draw()
						pygame.display.flip()

						while not pygame.event.get(pygame.QUIT):
							choice = getChoiceUnbounded("Examining nearest bee...what feature?", ["Neural Network", "Movement", "Nothing"])

							#key = getChoice("Examine bee! What feature?", {pygame.K_t: "Neural Network", pygame.K_e: "Movement from loads of starting points", pygame.K_r: "Nothing"})
							
							if choice == "Neural Network":
								command = minbee.show_brain(world)
								if command:
									return
							
							if choice == "Movement":
								c.draw()
								messages.say("Loading", down = 1)
								pygame.display.flip()
								minbee.visualize_intelligence(world)
								minbee.sample_path(world)
								c.draw()
								pygame.display.flip()



							if choice == "Nothing":
								done = 1
								break
				elif choice == "Save bees":
					messages.colorBackground()
					beemap = {}
					beenames = []
					for b in r.bees:
						beemap[b.name] = b
						beenames.append(b.name)

					b = beemap[getChoiceUnbounded("Pick a bee", beenames)]
					messages.say("Pick a new name for the bee", 0)
					rename = getString(string = b.name)
					if rename:
						b.name = rename
					h.save_bee(b)
					h.savedata()

				elif choice == "Load bees":
					loadedbeenames = []
					for b in h.specimens:
						loadedbeenames.append(b[0])

					loadedbeenames.append("cancel")

					name = getChoiceUnbounded("Here are the saved bees", loadedbeenames)

					if name == "cancel":
						print "cancelled."
						continue

					else:
						b = h.make_bee(name, r, p)
						r.bees.append(b)
						b.flash = 50



				elif choice == "Tweak variables":

					l = [settings.healthlossrate, settings.acid, settings.healthgain]
					titles = ["Health Loss Rate", "Acid", "Health Gain"]
					indices = {title:index for index, title in enumerate(titles)}

					'''takes "name: value" string to "name".'''
					information = {x + ": " + str(l[index]) : x for x, index in indices.iteritems()}

					'''this is a bunch of informative labels'''
					options = [x for x in information]

					toChange = getChoiceUnbounded("Pick a variable to modify", options)

					'''we have the name of the variable we want to change now'''
					toChange = information[toChange]

					messages.say("Pick a new value", down = 4)

					allowed_keys = range(pygame.K_0, pygame.K_9 + 1)
					allowed_keys += [pygame.K_PERIOD]

					number = float(getString(allowed_keys, str(l[indices[toChange]])))

					l[indices[toChange]] = number

					settings.healthlossrate, settings.acid, settings.healthgain = l

					for name, index in indices.iteritems():
						print name + ":", l[index]



				elif choice == "Modify map":
					messages.colorBackground()
					messages.say("This is where I would modify the map", 2000)

		#test.record("stuff")
		#test.add_sticky('drawing', 'erase')
		# Clean up

		for phys in [p] + r.food + r.bees + r.bullets:
			phys.erase()

		r.repair(world)

		#test.record("stuff")
		#test.remove_sticky('drawing', 'erase')

		

		#test.add_sticky('update')

		mod = 2
		#each bee updates once every mod frames

		'''Update'''
		for i, bee in enumerate(r.bees):
			bee.slow = (i + framecount) % mod


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

		'''if r.bees:
									b = r.bees[0]
									ixy = b.xy.astype(int)
									for x in range(-1, 2, 1):
										if x and 0 < ixy[0,0] + 41 * -x < graphics.world_w:
											continue
										for y in range(-1, 2, 1):
											if y and 0 < ixy[0,1] + 41 * -y < graphics.world_h:
												continue
											x0 = ixy[0,0] + x * graphics.world_w
											y0 = ixy[0,1] + y * graphics.world_h
											pygame.draw.circle(world, [255, 255, 255], (x0, y0), 40, 1)'''


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

		ta = "Time: " + str(pygame.time.get_ticks() / 1000)
		tb = " | current bees: " + str(len(r.bees))
		tc = " |" + str(int(clock.get_fps()))+"fps"

		t.permanent_text = "[o]ptions | " +  ta + tb + tc
		t.data.append(clock.get_fps())
		t.draw(screen)
		pygame.display.flip()
		
		#test.record('drawing', "topbar")


		for phys in r.bees + r.food + [p]:
			phys.visible = c.can_see(phys)

		#test.record("visibility")

		test.summarizetimings(test.segs, test.segdescriptors)
		pygame.event.pump()
		#end of while loop

def main():
	initialization()

	pygame.event.set_blocked(None)
	pygame.event.set_allowed(pygame.QUIT)

	main_loop()