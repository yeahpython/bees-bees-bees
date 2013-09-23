import pygame
import graphics

pygame.init()
font = pygame.font.Font(None, 50)

screen = None

def say(message, time = 1000):
	screen.fill(graphics.foreground)
	text = font.render(message, 1, [200,200,200])
	textpos = text.get_rect(centerx = graphics.screen_w/2, centery = graphics.screen_h/2)
	screen.blit(text, textpos)
	pygame.display.flip()
	pygame.time.wait(time)