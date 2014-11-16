import pygame
import graphics

pygame.init()
font = pygame.font.Font(None, 50)
smallfont = pygame.font.Font(None, 20)

screen = None

def colorBackground(surface = 0):
	if surface:
		surface.fill(graphics.foreground)
		box = surface.get_rect()
		pygame.draw.rect(surface, graphics.outline, box, 1)
	else:
		screen.fill(graphics.foreground)
		pygame.display.flip()

def say(message, time = 0, down = 0, surface = 0, color = graphics.outline, size = "big"):
	text = 0
	textpos = 0

	if not surface:
		surface = screen

	if size == "big":
		text = font.render(message, 1, color)
		textpos = text.get_rect(centerx = surface.get_width()/2, top= 20 + down * 50)
	else:
		text = smallfont.render(message, 1, color)
		textpos = text.get_rect(left = 20, top = 20 + down * 15)
	if surface:
		surface.blit(text, textpos)
	else:
		screen.blit(text, textpos)
	pygame.display.flip()
	pygame.time.wait(time)
	return down + 1
