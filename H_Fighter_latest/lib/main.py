import pickle
import os
#os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)

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
import clicks
import game_progress
import familytree
from numpy import linalg
from random import choice
from game_settings import *
import species_visualization


game_title = "evade"

def initialization():
	pygame.init()
	pygame.display.set_mode(graphics.screen_size)
	pygame.display.set_caption(game_title)
	tile.init()

def preparelevel(screen, level):
	if level == "random map":
		return prepareRandomLevel(screen)
	elif level == "Random 35 x 35":
		return prepareRandomLevel(screen, 35, 35)
	elif level == "Random 60 x 60":
		return prepareRandomLevel(screen, 60, 60)
	elif level == "Random 60 x 25":
		return prepareRandomLevel(screen, 60, 25)
	else:
		graphics.load(os.path.join("data", "rooms", level))
		world = pygame.Surface((graphics.world_w, graphics.world_h))
		t = topbar.TopBar(screen)
		r = room.load(os.path.join("data", "rooms", level))
		test.mark(r.background)
		r.topbar = t
		return world, t, r

def prepareRandomLevel(screen, cols = 0, rows = 0):
	messages.colorBackground()
	if not cols:	
		cols = int(getChoiceUnbounded("Room width?", [str(x) for x in range(30, 61, 5)]))
	if not rows:
		rows = int(getChoiceUnbounded("Room height?", [str(x) for x in range(20, 61, 5)]))
	room.globalize_dimensions(rows, cols)

	lines = [" " * cols for x in range(rows+1)]
	room.randomlymodify(lines)
	tiles = []
	for c in range(cols):
		tiles.append([])
		for r in range(rows):
			tiles[c].append(tile.tile[lines[r][c]])
	r = room.Room(tiles, lines)
	graphics.extract_dimensions(lines)

	world = pygame.Surface((graphics.world_w, graphics.world_h))
	t = topbar.TopBar(screen)
	test.mark(r.background)
	r.topbar = t
	return world, t, r

def getString(allowed_keys = [], string = "", textpos = 0, message = ""): # Should be able to exit nonhorribly now
	'''returns -1 if window is closed
	and 0 for cancel'''
	disp = pygame.display.get_surface()
	bg = pygame.Surface((disp.get_width(), disp.get_height()))
	bg.blit(disp, (0,0))
	font = pygame.font.Font(None, 30)
	box = 0
	if textpos:
		box = textpos
	else:
		box = pygame.Rect(0, 0, 300, 50)
		box.centerx = graphics.screen_w / 2
		box.centery = graphics.screen_h / 2
	s = pygame.display.get_surface()

	prompt = font.render(message, 1, graphics.outline)
	promptpos = prompt.get_rect(centerx = box.centerx, bottom = box.y - 10)

	pygame.draw.rect(s, graphics.foreground, box, 0)
	pygame.draw.rect(s, graphics.outline, box, 1)
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
	global time_to_quit
	while True:
		clock.tick(60)

		'''check for quit'''
		if pygame.event.get(pygame.QUIT):
			time_to_quit = True
			return -1
		clicks.get_more_clicks()

		'''check for cancel'''
		if clicks.mouseups[0]:
			x,y = pygame.mouse.get_pos()
			if not box.collidepoint(x,y):
				return string

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
					disp.blit(bg, (0,0))
					return string
				elif len(string) < 20:
					if key == pygame.K_SPACE:
						string += " "
					else:
						string += pygame.key.name(key)
				redraw = 1

		if redraw:
			s.blit(prompt, promptpos)


			text = font.render(string, 1, graphics.outline)
			textpos2 = text.get_rect(centerx = box.centerx, centery = box.centery)
			pygame.draw.rect(s, [155,0,200], box, 0)
			#box = text.get_rect(centerx = s.get_width()/2, height = 50, centery = s.get_height()/2)
			pygame.draw.rect(s, graphics.outline, box, 1)
			s.blit(text, textpos2)
			pygame.display.flip()
			redraw = 0

		previous_key_states = key_states[:]
		pygame.event.pump()

def waitForEnter(hidemessage = 0):
	if not hidemessage:
		messages.say("Press [enter] to continue", down = 1)
	pygame.display.flip()
	clock = pygame.time.Clock()
	while True:
		clock.tick(60)
		if pygame.event.get(pygame.QUIT):
			global time_to_quit
			time_to_quit = True
			break

		clicks.get_more_clicks()
		if clicks.mouseups[0]:
			break
		key_states = pygame.key.get_pressed()
		if key_states[pygame.K_RETURN]:
			break

def waitForKey(key, message = 0):
	if message:
		messages.say(message, down = 1)
	else:
		messages.say("Press " + pygame.key.name(key) +" to exit", down = 1)
	pygame.display.flip()
	clock = pygame.time.Clock()
	while not pygame.event.get(pygame.QUIT):
		clock.tick(60)
		key_states = pygame.key.get_pressed()
		if key_states[key]:
			break
		if pygame.event.get(pygame.QUIT):
			global time_to_quit
			time_to_quit = True
			break
		pygame.event.pump()

def getChoiceUnbounded(title, options, allowcancel = False):
	page_size = 30
	curr = 0
	pages = (len(options)-1) / page_size + 1
	if pages <= 1:
		return getChoiceBounded(title, options, allowcancel)
	else:
		while True:
			view = ["prev", "next"] + options[curr::pages]
			out = getChoiceBounded(title + " (Page %s of %s)" % (curr + 1, pages), view, allowcancel)
			if out == "prev":
				curr -= 1
				curr %= pages
			elif out == "next":
				curr += 1
				curr %= pages
			else:
				return out

def getChoiceBounded(title, given_options, allowcancel = False):
	'''Prompts you to choose one of the options. If the user clicks outside the box this returns None.'''

	options = given_options[:]
	if allowcancel:
		options.append("cancel")

	disp = pygame.display.get_surface()
	bg = pygame.Surface((disp.get_width(), disp.get_height()))
	bg.blit(disp, (0,0))

	clock = pygame.time.Clock()
	n = None

	messages_per_page = 3

	currpos = 0
	currpage = 0
	updateview = 1

	hborder = 15

	optiondisplay = pygame.Surface((min(300, graphics.screen_w - 2*hborder), min(15 * (len(options) + 3), graphics.screen_h - 2 * hborder) ))
	selectionimage = pygame.Surface((optiondisplay.get_width() - 10, 50), flags = pygame.SRCALPHA)

	box = pygame.Rect((0,0), (selectionimage.get_width(), 15))
	pygame.draw.rect(selectionimage, graphics.outline, box, 1)

	smallsteps = 0
	slowness = 6

	previous_key_states = []
	wet = 0

	oldxy = (-1, -1)

	# lean right
	#dest = optiondisplay.get_rect(right = graphics.screen_w - 15, top = 15)
	dest = optiondisplay.get_rect(centerx = graphics.screen_w/2, centery = graphics.screen_h/2)

	while True:
		if pygame.event.get(pygame.QUIT):
			print "quit from getChoiceUnbounded"
			global time_to_quit
			time_to_quit = True
			return "quit"
		clicks.get_more_clicks()
		wet += 1

		x,y = pygame.mouse.get_pos()

		if oldxy != (x,y):
			oldxy = x,y
			i = (y - dest.y - 5) / 15 - 2
			if 0 <= i < len(options):
				if dest.left < x < dest.right and i != currpos:
					currpos = i
					updateview = 1

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

			#make it top right
			#center the options
			#dest = optiondisplay.get_rect(centerx = graphics.screen_w / 2, centery = graphics.screen_h / 2)

			disp.blit(optiondisplay, dest, special_flags = 0)

			disp.blit(selectionimage, (dest.x + 5, dest.y + 35 + currpos * 15))

			pygame.display.flip()
			updateview = 0

		if clicks.mouseups[0]:
			oldxy = x,y
			i = (y - dest.y - 5) / 15 - 2
			if 0 <= i < len(options) and dest.left < x < dest.right:
				disp.blit(bg, (0,0))
				return options[currpos]
			elif allowcancel: 
				disp.blit(bg, (0,0))
				return "cancel"

		clock.tick(60)

		'''stupid mac...'''
		#key_presses = pygame.event.get()
		key_states = pygame.key.get_pressed()
		#event = pygame.event.poll()

		#if event.type != pygame.NOEVENT:
		#	print event

		#if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
		if key_states[pygame.K_UP]:
			smallsteps -= 1
			if smallsteps == 0 or (previous_key_states and not previous_key_states[pygame.K_UP]):
				smallsteps = slowness
				currpos -= 1
				currpos %= len(options)
				updateview = 1

		#if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
		elif key_states[pygame.K_DOWN]:
			smallsteps -= 1
			if smallsteps == 0 or (previous_key_states and not previous_key_states[pygame.K_DOWN]):
				smallsteps = slowness
				currpos += 1
				currpos %= len(options)
				updateview = 1

		elif key_states[pygame.K_RETURN] and (previous_key_states and not previous_key_states[pygame.K_RETURN]):
			disp.blit(bg, (0,0))
			return options[currpos]

		elif key_states[pygame.K_q]:
			disp.blit(bg, (0,0))
			return

		previous_key_states = key_states[:]
		pygame.event.pump()

levels = ["5.txt", "1.txt", "ringmap4.txt", "3.txt", "dumb room.txt", "ringmap5.txt", "dumb room.txt"]

files = {
	"tiny debugger" : 1,
	"ring map" : 2,
	"vertical map" : 3,
	"horizontal map" : 4,
	"closed ring map" : 5,
	"walls" : 6,
	"huge map" : 0,
}

def enteredlevel(allowcancel = 1):
	# always allows quit and cancel
	# deals with cancel and quit elegantly
 	options = ["tiny debugger", "random map", "ring map", "vertical map", "horizontal map", "huge map", "closed ring map", "walls", "quit"]

	choice = getChoiceUnbounded("Select a level:", options, allowcancel = allowcancel)

	if choice in files:
		return levels[files[choice]]
	else:
		return choice

def fiddle(tens, units):
	return 10 * tens + units

def close(r):
	'''This is a convenient function for closing for when the room is in your namespace'''
	if pygame.event.get(pygame.QUIT):
		print "Trying to quit properly..."
		game_progress.save_game(r)
		return True
	else:
		return False

time_to_quit = False

def main_loop():
	print "\n\n\n\n\n\n\n\n\n\n\n\n* * * * * NEW GAME * * * * *"

	'''these things only need to happen once'''
	screen = pygame.display.get_surface()
	screen.fill(graphics.background)
	load_settings()

	messages.screen = screen

	clock = pygame.time.Clock()
	dt=0
	font = pygame.font.Font(None, 30)

	world, t, r = 0, 0, 0
	
	loadedSavedGame = 0
	
	if getChoiceUnbounded("Load saved game?", ["yes", "no"]) == "yes":
		r = game_progress.load_game()
		
	if r:
		messages.say("Loading saved game", down = 4)
		pygame.display.flip()
		world = pygame.Surface((graphics.world_w, graphics.world_h))
		t = r.topbar
		loadedSavedGame = 1
	else:
		'''these are level-specific'''
		level = enteredlevel(allowcancel = 0)
		if level == "quit":
			return
		world, t, r = preparelevel(screen, level)
	
	p = player.Player(r)

	#h = zoo.Beehive()
	h = zoo.Beehive("the fact that any argument is passed here means that I'll load saved bees")

	c = camera.Camera(p, world, screen, r)
	c.jump_to_player()

	myfamilytree = familytree.FamilyTree()
	myspeciesplot = species_visualization.SpeciesPlot()

	#Generating new bees
	#r.bees = h.preserved_bees(r, p)
	if loadedSavedGame:
		for b in r.bees:
			b.player = p
	else:
		r.generate_bees(settings[MAXIMUM_BEES])
	r.h = h
	#for b in r.bees:
	#	b.randomize_position()

	framecount = 0

	previous_key_states = []
	key_ups = []

	global time_to_quit

	last_data_update = -20

	while not close(r): # Main game loop # Don't need cancel and quit works

		if time_to_quit:
			'''probably going to add a bunch of shutdown stuff here'''
			print "Quitting indirectly at main loop. Saving room..."
			game_progress.save_game(r)
			break

		clicks.get_more_clicks()
		framecount += 1

		test.begin_timing(test.segs, test.segdescriptors)
		#Handle player input
		key_presses = pygame.event.get(pygame.KEYDOWN)
		key_states = pygame.key.get_pressed()

		if previous_key_states:
			key_ups = [old and not new for new, old in zip(key_states, previous_key_states)]
		else:
			key_ups = [0 for x in key_states]

		previous_key_states = key_states[:]

		if key_ups[pygame.K_e]:
			if r.bees:
				#for x in r.bees + r.food + [p] + r.bullets:
				#	x.draw(world)
				#c.draw()
				#pygame.display.flip()
				'''this is for picking the closest bee'''
				'''minbee = r.bees[0]
				for b in r.bees:
					if linalg.norm(b.xy - p.xy) < linalg.norm(minbee.xy - p.xy):
						minbee = b'''

				minbee = random.choice(r.bees)
				messages.say("Loading", down = 1)
				pygame.display.flip()
				minbee.visualize_intelligence(world, c)
				p.displaycolor = [255,255,255]
				pygame.draw.circle(world, [0,0,0], array(p.xy.astype(int))[0], int(p.forcefield))
				pygame.draw.circle(world, [255,255,255], array(p.xy.astype(int))[0], int(p.forcefield), 1)
				p.draw(world)
				#c.xy = minbee.xy * 1
				#c.updatesight()
				c.draw()
				pygame.display.flip()
				minbee.sample_path(world)
				c.draw()
				pygame.display.flip()
				waitForKey(pygame.K_w)
				dt = clock.tick(400)
				dt = 0 #Trick the engine into thinking no time has passed

		if time_to_quit:
			game_progress.save_game(r)
			return

		test.record()
		world.blit(r.background, (0,0))
		test.record("blitting background")
		#world.blit(r.collisionfield, (0,0))


		togglers = {
		pygame.K_r : SHOW_EYES,
		pygame.K_h : SHOW_HELP,
		pygame.K_t : GENERATE_RANDOM_MAP,
		pygame.K_n : SHOW_NAMES,
		}

		for key, variable in togglers.iteritems():
			if key_ups[key]:
				settings[variable] = not settings[variable]


		if key_ups[pygame.K_m]:
			print framecount
			r.madness += 1
			r.madness %= 5
			for bee in r.bees:
				bee.madness = r.madness

		if key_ups[pygame.K_a]:
			r.stasis = not r.stasis

		if key_ups[pygame.K_z]:
			print pygame.mouse.get_pos()



		'''All mouse click stuff'''
		if clicks.mouseups[0]:
			for b in r.bees:
				b.skipupdate = True
			options = ["Move to another map", "Random 60 x 25", "Random 35 x 35", "Random 60 x 60", "Examine bee", "Save bees", "Extinction", "Load bees", "Delete bees", "Tweak variables", "Modify map", "View Shortcuts", "quit"]
			choice = getChoiceUnbounded("select option", options, allowcancel = 1)

			if choice != "cancel":
				if choice == "quit":
					time_to_quit = True

				elif choice in ["Move to another map", "Random 60 x 25", "Random 35 x 35", "Random 60 x 60"]:
					level = choice
					if choice == "Move to another map":
						level = enteredlevel()
					if level == "quit":
						return

					if level != "cancel":
						print level
						test.clear_tests()
						test.sides = []
						test.vectors = [(0,0), (0,0)]
						test.indicators = []
						test.lines = []
						test.tiles = []
						test.backgroundmarkers = []
						test.backgroundpointmarkers = []
						test.segs = [] #a list of times
						test.segdescriptors = [] # a list of descriptors or hashtags to say what's happening during the time
						test.stickylabels = []
						r.topbar = 0
						world, t, r2 = preparelevel(screen, level)
						p.topbar = 0
						p = player.Player(r2)
						r2.roomnumber = r.roomnumber + 1
						r2.bees = r.bees
						r2.deadbees = r.deadbees

						r = r2
						h.savedata()
						#h = zoo.Beehive()
						h = zoo.Beehive("the fact that any argument is passed here means that I'll load saved bees")
						c = camera.Camera(p, world, screen, r)
						c.xy = 1 * p.xy
						r.h = h

						for b in r.bees + r.deadbees:
							b.lastnonwall = matrix([[-1.0, 0.0]])
							b.madness = 0
							b.room = r
							b.player = p
							b.randomize_position()



				elif choice == "Extinction":
					if getChoiceUnbounded("Kill all bees?", ["no", "yes"], allowcancel = 1) == "yes":
						for b in r.bees:
							b.health = -20
						for b in r.bees + r.deadbees:
							b.dead = 2
						t.data = []

				elif choice == "Examine bee":
					'''this thing lets you examine the closest bee to you'''
					if r.bees:
						minbee = r.bees[0]
						for b in r.bees:
							if linalg.norm(b.xy - p.xy) < linalg.norm(minbee.xy - p.xy):
								minbee = b
						for x in r.bees + r.food + [p] + r.bullets:
							x.draw(world)
						c.draw()
						pygame.display.flip()

						while not time_to_quit: # quit should work fine here
							choice = getChoiceUnbounded("Examining nearest bee...what feature?", ["Neural Network", "Movement"], allowcancel = True)

							if choice == "Neural Network":
								command = minbee.show_brain(world)
								if command:
									return
							
							elif choice == "Movement":
								c.draw()
								messages.say("Loading", down = 1)
								pygame.display.flip()
								minbee.visualize_intelligence(world, c)
								minbee.sample_path(world)
								c.draw()
								pygame.display.flip()

							elif choice == "cancel":
								done = 1
								break

							elif choice == "quit":
								time_to_quit = True
				
				elif choice == "Save bees":
					beemap = {}
					beenames = []

					for b in r.bees:
						label = b.firstname + " " + b.name
						beemap[label] = b
						beenames.append(label)

					choice = getChoiceUnbounded("Pick a bee", beenames, allowcancel = True)

					if choice == "quit":
						time_to_quit = True

					elif choice != "cancel":
						b = beemap[choice]
						#messages.colorBackground()
						#messages.say("Pick a new name for the bee", down = 4)
						rename = b.name
						'''loop is for error checks'''
						while not time_to_quit:
							rename = getString(string = b.name, message = "Pick a new name for the bee")

							# quit
							if rename == -1:
								break
							# cancel
							elif rename == 0:
								break
							elif any(specimen[0] == rename for specimen in h.specimens):
								messages.colorBackground()
								messages.say("Name taken. Pick a new name for the bee", down = 4)
								continue
							else:
								b.name = rename
								break
						h.save_bee(b)
						h.savedata()

				elif choice == "Load bees":
					loadedbeenames = []
					for b in h.specimens:
						loadedbeenames.append(b[0])

					loadedbeenames.append("done")
					loadedbeenames = loadedbeenames[-1::-1]
					i = 0
					while not time_to_quit:
						name = getChoiceUnbounded("Loaded " +str(i) +" bees", loadedbeenames, allowcancel = True)
						if name in ["done", "quit", "cancel"]:
							break
						else:
							i+=1
							b = h.make_bee(name, r, p)
							r.bees.append(b)
							b.flash = 50
							b.xy[0,0] = p.xy[0,0]

				elif choice == "Delete bees":
					i = 0
					message = "Choose a bee to delete"
					while not time_to_quit:
						indexfromname = {}
						loadedbeenames = []
						for index, b in enumerate(h.specimens):
							name = b[0]
							loadedbeenames.append(name)
							indexfromname[name] = index
						loadedbeenames.append("done")
						loadedbeenames = loadedbeenames[-1::-1]

						if i:
							message = "Deleted " + str(i) + " bees"
						name = getChoiceUnbounded(message, loadedbeenames, allowcancel = True)
						if name in ["quit", "done", "cancel"]:
							break
						else:
							confirm = getChoiceUnbounded("Delete %s?" % name, ["no", "yes"], allowcancel = True)
							if confirm != "yes":
								continue
							i+=1
							indextoremove = indexfromname[name]
							h.specimens = h.specimens[:indextoremove] + h.specimens[(indextoremove + 1):]

				elif choice == "Tweak variables":
					families = {
					"Life and Death" : 
					(ACID, 
					TOO_SLOW, 
					HEALTH_LOSS_RATE, 
					HEALTH_GAIN, 
					MAXIMUM_BEES, 
					SLOWNESS_PENALTY,
					COST_OF_JUMP, 
					SPEED_PAYOFF,
					MAX_HEALTH),

					"Mutation":
					(MUTATION_CHANCES,
					SCALING_MUTATION,
					ADDITIVE_MUTATION_RATE,
					INVERT_MUTATION_RATE,
					OFFSPRING_MUTATION_RATE,
					EYE_MUTATION_RANGE,),
					
					"Topology / Physics":
					(STING_REPULSION,
					AUTOMATIC_EVASION,
					SWARMING_PEER_PRESSURE,
					WRAPAROUND_TRACKING,
					CREATURE_MODE,
					STICKY_WALLS,
					GRAVITY),
					
					"Random Map Generation":
					(
					GENERATE_RANDOM_MAP,
					RANDOM_TILE_DENSITY,
					CONGEAL_THOROUGHNESS,
					RANDOM_MAP_LOW,
					RANDOM_MAP_HIGH,
					RANDOM_MAP_RUNS,
					RANDOM_MAP_RADIUS,),

					"Visual":
					(JUICINESS,
					SHOW_EYES,
					SHOW_NAMES,
					BEE_STYLE,
					SPECIES_STYLE),

					"Family Tree":
					(TREE_THICKNESS,
					TREE_V_SPACING,
					TREE_H_SPACING,
					TREE_COLOR_VARIATION,
					TREE_UPDATE_TIME),

					"Brain Type":
					(SENSITIVITY_TO_PLAYER,
					BRAIN_BIAS,
					MEMORY_STRENGTH,
					BRAIN_ACTIVATION),
					}

					miscsettings = copy.deepcopy(settings)
					for family, entries in families.iteritems():
						for name in entries:
							if name in miscsettings:
								del miscsettings[name]

					#miscsettings now has everything not represented by the others
					if miscsettings:
						families["Misc."] = miscsettings.keys()

					'''picking kinds of variables'''
					while not time_to_quit:
						family = getChoiceUnbounded("What kind of variable?", families.keys(), allowcancel = 1)
						if family == "cancel":
							break

						'''picking variable'''
						while not time_to_quit:
							'''takes "name: value" string to "name".'''
							label_to_key = {key + ": " + str(settings[key]) : key for key in families[family]}

							'''this is a bunch of informative labels'''
							options = [x for x in sorted(label_to_key.keys())]


							toChange = getChoiceUnbounded("Pick a variable to modify", options, allowcancel = 1)

							if toChange == "cancel":
								break
							toChange = label_to_key[toChange]
							if toChange in want_bools:
								settings[toChange] = not settings[toChange]
								continue
							elif toChange in want_ints and toChange in max_val and toChange in min_val:
								settings[toChange] += 1
								if settings[toChange] > max_val[toChange]:
									settings[toChange] = min_val[toChange]
								continue
							else:
								'''we have the name of the variable we want to change now'''

								usedindex = 0
								for i, entry in enumerate(options):
									if entry == toChange:
										usedindex = i

								#messages.colorBackground()
								#messages.say("Pick a new value", down = 4)

								allowed_keys = range(pygame.K_0, pygame.K_9 + 1)
								allowed_keys += [pygame.K_PERIOD]
								allowed_keys += [pygame.K_e]
								allowed_keys += [pygame.K_MINUS]

								'''loop is for error checking'''
								while not time_to_quit:
									#message = messages.smallfont.render("Set new value for '%s'" % toChange, 1, [255, 255, 255])
									#pygame.display.get_surface().blit(message, (600, 15 * (usedindex + 3)))
									m = "Set new value for '%s'" % toChange
									position = pygame.Rect(0,0,290,30)
									# position.x = 600 #Leaning right
									position.centerx = graphics.screen_w / 2
									# position.y = 15 * (usedindex + 4.3) #Leaning up
									position.centery = graphics.screen_h / 2
									out = getString(allowed_keys, str(settings[toChange]), textpos = position, message = m)
									#out = getString(allowed_keys, str(settings[toChange]))
									
									# quit
									if out == -1:
										break

									# cancel
									elif out == 0:
										break

									try:
										val = 0
										if "." in out:
											val = float(out)
										else:
											val = int(out)

										problems = problem_with_setting(toChange, val)
										if problems:
											messages.colorBackground()
											messages.say(problems, down = 4)
											continue

										settings[toChange] = val
										break

									except:
										messages.colorBackground()
										messages.say("Error. Pick a new value", down = 4)

								save_settings()

								#for key, value in settings.iteritems():
								#	print key + ":", str(value)
						if family == "quit" or time_to_quit:
							time_to_quit = True
							break

				elif choice == "Modify map":
					messages.colorBackground()
					messages.say("This is where I would modify the map", 500)

				elif choice == "View Shortcuts":
					messages.colorBackground()
					messagecount = 2
					if settings[SHOW_EYES]:
						messagecount = messages.say("[r]: Hide eyes", down = messagecount)
					else:
						messagecount = messages.say("[r]: Show eyes", down = messagecount)

					if r.madness:
						messagecount = messages.say("[m]: Don't draw trails", down = messagecount)
					else:
						messagecount = messages.say("[m]: Draw trails", down = messagecount)

					if settings[GENERATE_RANDOM_MAP]:
						messagecount = messages.say("[t]: Don't randomize maps when loading", down = messagecount)
					else:
						messagecount = messages.say("[t]: Randomize maps when loading", down = messagecount)

					if r.stasis:
						messagecount = messages.say("[a]: Resume deaths and births", down = messagecount)
					else:
						messagecount = messages.say("[a]: Pause deaths and births", down = messagecount)

					messagecount = messages.say("[e]: Examine a random bee", down = messagecount)

					messagecount = messages.say("Click anywhere to continue", down = messagecount)
					waitForEnter(hidemessage = 1)

			if time_to_quit:
				print "Saving game very rapidly, whee"
				game_progress.save_game(r)
				return

			screen.fill(graphics.background)
			dt = clock.tick(400) # This is to trick the computer into thinking no time has passed
			dt = 0


		mod = 20
		#each bee updates once every mod frames

		'''Update'''
		for i, bee in enumerate(r.bees):
			bee.slow = 1# (i + framecount) % mod

		for phys in [p] + r.food + r.bullets:
			phys.update(dt, key_states, key_presses)



		for b in r.bees:
			b.update(dt, key_states, key_presses)
			if b.request_family_tree_update:
				updatefamilytree = 1
				b.request_family_tree_update = 0

		'''draw every frame, since the tree follows the player around'''
		if settings[SPECIES_STYLE] == 3:
			if not framecount % settings[TREE_UPDATE_TIME]:
				myspeciesplot.update(r.bees + r.deadbees)
				for b in r.deadbees:
					if b.dead == 2:
						r.deadbees.remove(b)
			myspeciesplot.draw(world, (int(p.xy[0,0]) - myspeciesplot.w/2, int(p.xy[0,1]) - myspeciesplot.h/2))
		
		else:
			'''update once every few frames'''
			if not framecount % settings[TREE_UPDATE_TIME]:
				myspeciesplot.update(r.bees + r.deadbees)
				myspeciesplot.draw(screen, (840,0))


				for b in r.deadbees:
					if b.dead == 2:
						r.deadbees.remove(b)

		updatefamilytree = 0

		if updatefamilytree:
			myfamilytree.update(r.bees)
			myfamilytree.draw(screen, (840, 0))

		r.update() # Necessarily comes afterwards so that the bees can see the player
		if r.signal_new_tree:
			r.signal_new_tree = 0
			myfamilytree.depth += 2*settings[TREE_V_SPACING]
		c.follow_player(dt) # Here so that room knows what to draw
		c.updatesight()

		
		test.draw(world, r)

		for x in r.bees + r.food + [p] + r.bullets:
			x.draw(world)
		
		# Time
		dt = clock.tick(120)
		dt = min(dt, 45) # Make it seem like a slowed down version of 22fps if necessary
		#print dt, "this is dt"

		c.draw()

		seconds = pygame.time.get_ticks() / 1000

		t0 = ""

		if settings[SPECIES_STYLE] == 1:
			t0 += "Plotted on right: x: horizontal movement, y: generation"
		elif settings[SPECIES_STYLE] == 2:
			t0 += "Plotted on right: x: generation, y: vertical movement"
		elif settings[SPECIES_STYLE] == 3:
			t0 += "angle: direction, radius: generation"

		t.permanent_text = [t0]

		ta = "Time: " + str(seconds)
		tb = " | current bees: " + str(len(r.bees))
		tbb = " | total dead bees " + str(len(r.deadbees))
		tc = " |" + str(int(clock.get_fps()))+"fps"

		t.permanent_text += [
		ta + tb + tbb + tc,]

		if settings[SHOW_HELP]:
			t.permanent_text += [
			"click anywhere for options",
			"plotted on right: Recent lifetimes, max is %s" % (max(t.data) if t.data else "not defined"),
			"[a]: %s birth and deaths" % ("resume" if r.stasis else "pause"),
			"[g]: generate bees",
			"[e]: visualize paths of a random bee",
			"[r]: %s eyes" % ("hide" if settings[SHOW_EYES] else "show"),
			"[n]: %s names" % ("hide" if settings[SHOW_NAMES] else "show"),
			"[m]: %s visual madness" % ("decrease" if r.madness == 2 else "increase"),
			"[SPACE]: teleport to a random position",
			"[t]: turn %s random map generation" % ("off" if settings[GENERATE_RANDOM_MAP] else "on"),
			]

		t.permanent_text.append("[h]: %s help" % ("hide" if settings[SHOW_HELP] else "show"))

		t.draw(screen)
		pygame.display.flip()

		for phys in r.bees + r.food + [p]:
			phys.visible = c.can_see(phys)

		test.summarizetimings(test.segs, test.segdescriptors)
		pygame.event.pump()


def main():
	initialization()

	pygame.event.set_blocked(None)
	pygame.event.set_allowed(pygame.QUIT)

	main_loop()