import pygame
from numpy import linalg, matrix, array
import graphics

class Camera(object):
	def __init__(self, player, world, screen, room):
		self.p = player
		self.w = world
		self.s = screen
		self.r = room
		self.xy = player.xy + matrix([0,0])
		self.recs = [[pygame.Rect( (0,0), graphics.disp_size) for x in range(3)] for y in range(3)]
		self.sight = []
		self.v_bounded = 1
		self.h_bounded = 0
		self.vxy = matrix([0,0])


	def can_see(self, phys):
		return any([r.collidepoint(phys.xy[0,0], phys.xy[0,1]) for r in self.sight])

	def follow_player(self, dt):
		if self.h_bounded:
			htargs = [0]
		else:
			htargs = [-1, 0, 1]
		if self.v_bounded:
			vtargs = [0]
		else:
			vtargs = [-1, 0, 1]



		potential_targets = [(self.p.xy+graphics.world_w*x*matrix([1,0]) + graphics.world_h*y*matrix([0,1])) for x in htargs for y in vtargs]
		potential_movements = [target - self.xy for target in potential_targets]		
		distances = [ linalg.norm(m) for m in potential_movements]
		m = min(distances)
		if 1:#m > 200:
			for i, k in enumerate(distances):
				if k == m:
					if m > 100:
						self.vxy += potential_movements[i]*0.003*dt
					self.vxy *= 0.87
					self.xy += self.vxy*0.003*dt
					self.xy[0,0] %= graphics.world_w
					self.xy[0,1] %= graphics.world_h

					if self.v_bounded:
						if self.xy[0,1] + graphics.disp_h/2 > graphics.world_h:
							self.xy[0,1] = graphics.world_h - graphics.disp_h/2
						elif self.xy[0, 1] < graphics.disp_h/2:
							self.xy[0,1] = graphics.disp_h/2

					if self.h_bounded:
						if self.xy[0,0] + graphics.disp_w/2 > graphics.world_w:
							self.xy[0,0] = graphics.world_w - graphics.disp_w/2
						elif self.xy[0,0] < graphics.disp_w/2:
							self.xy[0,0] = graphics.disp_w/2
					break

	def updatesight(self):
		self.sight = []
		for x in range(-1, 2, 1):
			for y in range(-1, 2, 1):
				self.recs[x][y].centerx = self.xy[0,0] + graphics.world_w*x
				self.recs[x][y].centery = self.xy[0,1] + graphics.world_h*y
				self.sight.append( self.w.get_rect().clip(self.recs[x][y] ) )
		self.r.visibles = (self.sight)

	def draw(self):
		for x in range(-1, 2, 1):
			for y in range(-1, 2, 1):
				self.s.blit(self.w, (graphics.border_thickness, graphics.top_space), self.recs[x][y])