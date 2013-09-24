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
		print "loaded", len(h.specimens), "specimens",
		for k in h.specimens:
			print k[0] + k[1] + ", ",
		print ""

	def save_bee(self, bee):
		self.specimens.append((bee.name, bee.ancestry, bee.color, bee.brain._all_edges, bee.eyes))

	def preserved_bees(self, room, player):
		newbees = []
		for name, ancestry, color, edges, eyes in self.specimens:
			b = bee.Bee(room)
			b.findplayer(player)
			b.name = name
			b.color = color
			b.ancestry = ancestry
			b.brain._all_edges = edges
			b.eyes = eyes
			newbees.append(b)
		return newbees

	def savedata(self):
		self.specimens = self.specimens[-3:]
		g = open(os.path.join("data", "saved", "brains", "specimens.txt"), "wb")
		pickle.dump(self.specimens, g)
		g.close()
		#print "saved", len(self.specimens), "specimens"

	def loaddata(self):
		g = open(os.path.join("data", "saved", "brains", "specimens.txt"))
		self.specimens = pickle.load(g)
		g.close()