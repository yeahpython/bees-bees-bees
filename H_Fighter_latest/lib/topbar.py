import pygame
from numpy import linalg, matrix, array
import graphics

font = pygame.font.Font(None, 20)

info_c = [255,100,55]

class TopBar(object):
	'''This class involves a couple of pieces of information
	box that flashes messages including 'evade', 'extinction', etc.
	text for previous lifespans
	graph of lifespans'''

	def __init__(self, screen):
		self.permanent_text = ["evade"]
		self.flashtext = "start!"
		self.time_to_clear = 100
		self.data = []
		self.saved_text_images = []

	def flash(self, text):
		self.flashtext = text
		self.time_to_clear = 150

	def draw(self, screen):
		self.time_to_clear -= 1

		# Clearing everything
		#pygame.draw.rect(screen, graphics.foreground, pygame.Rect(0,0, graphics.screen_w, 100))

		# Top text
		nextmessage = 10
		for i, message in enumerate(self.permanent_text):
			text = 0
			if i < len(self.saved_text_images) and self.saved_text_images[i][0] == message:
				text = self.saved_text_images[i][1]
			else:
				text = font.render(message, 1, info_c)
				if i == len(self.saved_text_images):
					self.saved_text_images.append((message, text))
			textpos = text.get_rect(left = 20, top = nextmessage)
			nextmessage = textpos.bottom + 5
			screen.blit(text, textpos)



		#Data
		if len(self.data) > 200:
			self.data = [self.data[i:i+2] for i in range(0, len(self.data), 2)]
			self.data = [sum(l) / len(l) for l in self.data]
		lines = []
		l = 200
		r = graphics.screen_w - 100
		if len(self.data) > 1:
			spacing = float(r - l) / (len(self.data) - 1)
			g = max(self.data)
			if g:
				for k in range(0, len(self.data) - 1):
					xstart = l+(k) * spacing
					xend = l+(k + 1) * spacing
					a = float(self.data[k]) / g
					b = float(self.data[k+1]) / g
					#top = graphics.screen_h * 0.2
					#bottom = graphics.screen_h * 0.8
					top = 30
					bottom = 90
					ystart = (a * (top - bottom)) + bottom
					yend = (b * (top - bottom)) + bottom
					lines.append(  ((xstart, ystart), (xend, yend))  )

		'''plotting info'''
		#for p1, p2 in lines:
		#	pygame.draw.line(screen, info_c, p1, p2, 1)
			#pygame.draw.circle(screen, graphics.foreground, [int(k) for k in p1], 2)


		# Flashtext
		if self.time_to_clear > 0:
			if  self.time_to_clear % 20 > 10:
				text = font.render(self.flashtext, 1, info_c)
				textpos = text.get_rect(right = graphics.screen_w - 20, top = 10)
				screen.blit(text, textpos)



		#pygame.display.flip()

		