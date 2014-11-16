from graphics import screen_w, screen_h
import pygame
from game_settings import *

scroll = 200

class FamilyTree(object):
	def __init__(self):
		self.w = 600
		self.h = 800
		self.tree = pygame.Surface((self.w, self.h))
		self.horizontal_position = 0
		self.depth = 5
		self.tree.fill([0,0,0])

	def update(self, bees):
		ancestries = sorted([b.ancestry for b in bees])
		#ancestries = [b.ancestry for b in bees]
		ranks = { ancestry:i for i,ancestry in enumerate(ancestries)}
		newdepth = (self.depth+settings[TREE_V_SPACING])
		if newdepth > self.h:
			if 1:
				self.tree.blit(self.tree, (0,-scroll))
				r = pygame.Rect(0,self.h - scroll, self.w, scroll)
				pygame.draw.rect(self.tree, [0,0,0], r)
				self.depth = self.h - scroll
			else:
				self.depth = 5
				self.horizontal_position += (len(bees) + 10) * settings[TREE_H_SPACING]
			return

		h_spacing = settings[TREE_H_SPACING]
		#h_spacing = self.w / len(bees)

		for b in bees:
			b.prevrank = b.rank
			b.rank = ranks[b.ancestry]
			pygame.draw.line(self.tree, b.treecolor, (b.prevrank*h_spacing + self.horizontal_position, self.depth), (b.rank*h_spacing + self.horizontal_position, newdepth), settings[TREE_THICKNESS])
		
		self.depth = newdepth

	def draw(self, surface, position = (0,0)):
		surface.blit(self.tree, position)