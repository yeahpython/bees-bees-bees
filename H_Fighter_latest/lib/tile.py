'''This file defines tiles.
init() loads tile information.
To access the different tiles, use tile[code]'''

import os

import pygame

import graphics

import numpy
from numpy import matrix, linalg, array

#This is the dictionary of all tiles
tile = {}

# Tile dimensions
height = graphics.bh
width = graphics.bw
size = (width, height)

##############
##############
##############
USE_IMAGES = 0
##############
##############
##############

image_path = os.path.join("data", "tiles")

tile_info = {
#   Code: (name, solid, image_file, CLOCKWISE_corners)  So that the normals will be pointing out if I rotate them counter-clockwise. MUST BE A LOOP.
	#' ' : ('empty', False, 'empty.bmp', () ),
	#'Q' : ('topleft', True, 'topleft.bmp', ((1, 1), (31, 1), (1, 31)) ),
	#'E' : ('topright', True, 'topright.bmp', ((1, 1), (31, 1), (31, 31)) ),
	#'Z' : ('bottomleft', True, 'bottomleft.bmp', ((1, 1), (31, 31), (1, 31)) ),
	#'C' : ('bottomright', True, 'bottomright.bmp', ((1, 31), (31, 1), (31, 31)) ),
	#'F' : ('floor', True, 'floor.bmp', ((0,16), (32, 16), (24,30), (8, 30)) ),
	#'#' : ('wall', True, 'wall.bmp', ((1, 1), (31,1), (31, 31), (1, 31)) )
	' ' : ('empty', False, 'empty.bmp', () ),
	'Q' : ('topleft', True, 'topleft.bmp', ((0, 0), (32, 0), (0, 32)) ),
	'E' : ('topright', True, 'topright.bmp', ((0, 0), (32, 0), (32, 32)) ),
	'Z' : ('bottomleft', True, 'bottomleft.bmp', ((0, 0), (32, 32), (0, 32)) ),
	'C' : ('bottomright', True, 'bottomright.bmp', ((0, 32), (32, 0), (32, 32)) ),
	'.' : ('floor', True, 'floor.bmp', ((12,12), (20, 12), (20, 20), (12, 20)) ),
	'^' : ('bump', True, 'floor.bmp', ((0,32), (16, 16), (32, 32))),
	'!' : ('start', True, 'floor.bmp', ()),
	'#' : ('wall', True, 'wall.bmp', ((0, 0), (32, 0), (32, 32), (0, 32)) )

}

tile_info2 = {
#   Code: (name, solid, image_file, CLOCKWISE_corners)  So that the normals will be pointing out if I rotate them counter-clockwise. MUST BE A LOOP.
	' ' : ('empty', False, 'empty', () ),
	'Q' : ('topleft', True, 'topleft', ((0, 0), (1, 0), (0, 1)) ),
	'E' : ('topright', True, 'topright', ((0, 0), (1, 0), (1, 1)) ),
	'Z' : ('bottomleft', True, 'bottomleft', ((0, 0), (1, 1), (0, 1)) ),
	'C' : ('bottomright', True, 'bottomright', ((0, 1), (1, 0), (1, 1)) ),
	'.' : ('floor', True, 'floor', ((0.4,0.4), (0.6, 0.4), (0.6, 0.6), (0.4, 0.6)) ),
	'^' : ('bump', True, 'floor', ((0,1), (0.5, 0.5), (1, 1))),
	'!' : ('start', True, 'floor', ()),
	'#' : ('wall', True, 'wall', ((0, 0), (1, 0), (1, 1), (0, 1)) )

}

class Tile(object):
	def __init__(self, name, solid, surface, sides, normals, pointlist):
		self.name = name # Name is here for debug purposes
		self.solid = solid
		self.surface = surface
		self.sides = zip(sides, normals)
		self.improvedsides = []
		self.pointlist = pointlist
		


def init():
	'''Loads tile information into the tile dictionary.'''
	global tile
	# We're making the images edible and accessible
	for t in tile_info2.keys():
		name = tile_info2[t][0]
		solid = tile_info2[t][1]
		tps = [(graphics.bw*x, graphics.bh*y) for x,y in tile_info2[t][3]]
		surface = None
		if USE_IMAGES:
			surface = pygame.image.load(os.path.join(image_path, tile_info[t][2]))
			surface.convert()
		segments = [ (tps[k-1], tps[k]) for k in range(len(tps))]
		normals = []
		for (x1, y1), (x2, y2) in segments:
			m = matrix(((y1 - y2), (x2 - x1))).astype(float)
			m /= linalg.norm(m)
			normals.append(m)
		tile[t] = Tile(name, solid, surface, segments, normals, tps)





