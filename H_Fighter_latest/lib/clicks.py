import pygame

mouseups = [0,0,0]
prevstates = [0,0,0]

def get_more_clicks():
	pygame.event.get()
	mousestates = pygame.mouse.get_pressed()

	for i in range(3):
		mouseups[i] = prevstates[i] and not mousestates[i]
		prevstates[i] = mousestates[i]
	#mouseups = [old and not new for new, old in zip(mousestates, prevstates)]
	#prevstates = mousestates[:]