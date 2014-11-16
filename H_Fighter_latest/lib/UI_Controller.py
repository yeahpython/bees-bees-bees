import pygame
import graphics

class UI_Controller(object):
	'''
	Finally, something that holds onto a screen and paints it if necessary.
	Has a bunch of child objects that each draw from their personal surfaces to the 
	main surface!
	'''

	def __init__(self, width, height):
		self.w = width
		self.h = height
		self.children = []
		#these should all know if they're visible or active


	def take_event(x, y):
		# For all the active children pass on the event

	def draw():
		# for all the visible children draw them
