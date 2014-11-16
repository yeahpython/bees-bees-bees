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


class Beehive(object):
	'''Container that accesses bees stored between games.
	specimens.txt: container for brains with names'''
	def __init__(self, title = None):
		self.specimens = []
		if title == None:
			return
		self.loaddata()
		print "Zoo currently contains", len(self.specimens), "specimens",
		for k in self.specimens:
			print str(k[0]) + ", ",
		print ""

	def save_bee(self, bee):
		self.specimens.append((bee.name, bee.ancestry, bee.color, bee.brain._all_edges, bee.eyes, bee.eyepoints))
		self.savedata()

	def preserved_bees(self, room, player):
		newbees = []
		for name, ancestry, color, edges, eyes, eyepoints in self.specimens:
			b = bee.Bee(room, eyepoints = eyepoints)
			b.findplayer(player)
			b.name = name
			b.color = color
			b.ancestry = ancestry
			b.brain._all_edges = edges
			b.eyes = eyes
			newbees.append(b)
		return newbees

	def make_bee(self, specified_name, room, player):
		for name, ancestry, color, edges, eyes, eyepoints in self.specimens:
			if name != specified_name:
				continue
			b = bee.Bee(room, eyepoints = eyepoints)
			b.findplayer(player)
			b.name = name
			b.color = color
			b.ancestry = ancestry
			b.brain._all_edges = edges
			b.eyes = eyes
			return b
		print "Could not load bee %s" % specified_name

	def savedata(self):
		g = open(os.path.join("data", "saved", "brains", "specimens.txt"), "wb")
		pickle.dump(self.specimens, g)
		g.close()

	def loaddata(self):
		g = open(os.path.join("data", "saved", "brains", "specimens.txt"))
		try:
			self.specimens = pickle.load(g)
		except:
			print "Failed to load saved bees. (File may have been corrupted or empty.)"
		g.close()