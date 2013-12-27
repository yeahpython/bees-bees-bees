import pygame
from numpy import linalg, matrix, array
import graphics

trackerradius = 250
vertalert = 100

class Camera(object):
	def __init__(self, player, world, screen, room):
		self.p = player
		self.w = world
		self.s = screen
		self.r = room
		self.r.camera = self
		self.xy = player.xy + matrix([0,0])
		self.recs = [[pygame.Rect( (0,0), graphics.disp_size) for x in range(3)] for y in range(3)]
		self.sight = []
		self.v_bounded = 1
		self.h_bounded = 1
		self.vxy = matrix([0,0])
		self.tracker = self.xy * 1
		self.speed = 0


	def can_see(self, phys):
		return any([r.collidepoint(phys.xy[0,0], phys.xy[0,1]) for r in self.sight])

	def jump_to_player(self):
		self.xy = self.p.xy * 1
		self.tracker = self.p.xy * 1

	def jump_to_tracker(self):
		self.xy = self.tracker * 1

	def follow_player(self, dt):
		center = matrix([graphics.world_w/2, graphics.world_h/2])

		#teleport the tracker to the player if necessary
		playerfromtracker = self.p.xy - self.tracker
		playerfromtracker += center
		if not self.h_bounded:
			playerfromtracker[0,0] %= graphics.world_w
		if not self.v_bounded:
			playerfromtracker[0,1] %= graphics.world_h
		playerfromtracker -= center

		distancefromtracker = linalg.norm(playerfromtracker)

		#effectively we're checking if we're in the curcle and not too low in the circle
		if distancefromtracker > trackerradius:# or playerfromtracker[0,1] > vertalert:
			self.tracker = self.p.xy * 1  + 0.9 * trackerradius * playerfromtracker / distancefromtracker

		if not self.h_bounded:
			self.tracker[0,0] %= graphics.world_w
		if not self.v_bounded:
			self.tracker[0,1] %= graphics.world_h

		if self.v_bounded:
			if self.tracker[0,1] + trackerradius >= graphics.world_h:
				self.tracker[0,1] = graphics.world_h - trackerradius
			elif self.tracker[0, 1] < trackerradius:
				self.tracker[0,1] = trackerradius

		if self.h_bounded:
			if self.tracker[0,0] + trackerradius >= graphics.world_w:
				self.tracker[0,0] = graphics.world_w - trackerradius
			elif self.tracker[0,0] < trackerradius:
				self.tracker[0,0] = trackerradius

		#find out how to follow the tracker
		trackeroffset = self.tracker - self.xy
		trackeroffset += center
		if not self.h_bounded:
			trackeroffset[0,0] %= graphics.world_w
		if not self.v_bounded:
			trackeroffset[0,1] %= graphics.world_h
		#this should be the direction of the nearest offset
		trackeroffset -= center

		distance = linalg.norm(trackeroffset)
		

		#modify speed
		if distance > 1000:
			self.jump_to_tracker()
		elif distance > 10:
			self.speed += 0.002 * dt
			if self.speed >= 0.3:
				self.speed = 0.3
		else:
			self.speed -= 0.002 * dt
			if self.speed <= 0:
				self.speed = 0

		#modify position
		if distance > 10:
			self.xy += trackeroffset / distance * self.speed * dt

		self.xy[0,0] %= graphics.world_w
		self.xy[0,1] %= graphics.world_h

		#if graphics.disp_

		if self.v_bounded:
			if graphics.disp_h > graphics.world_h:
				self.xy[0,1] = graphics.world_h/2# - graphics.world_h/2
			else:
				if self.xy[0, 1] <= graphics.disp_h/2:
					self.xy[0,1] = graphics.disp_h/2
				if self.xy[0,1] + graphics.disp_h/2 >= graphics.world_h:
					self.xy[0,1] = graphics.world_h - graphics.disp_h/2
			

		if self.h_bounded:
			if graphics.disp_w > graphics.world_w:
				self.xy[0,0] = graphics.world_w/2# - graphics.world_w/2
			else:
				if self.xy[0,0] <= graphics.disp_w/2:
					self.xy[0,0] = graphics.disp_w/2
				if self.xy[0,0] + graphics.disp_w/2 >= graphics.world_w:
					self.xy[0,0] = graphics.world_w - graphics.disp_w/2

		'''
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
		'''

	def updatesight(self):
		self.sight = []
		for x in range(-1, 2, 1):
			for y in range(-1, 2, 1):
				self.recs[x][y].centerx = self.xy[0,0] + graphics.world_w*x
				self.recs[x][y].centery = self.xy[0,1] + graphics.world_h*y
				self.sight.append( self.w.get_rect().clip(self.recs[x][y] ) )
		self.r.visibles = (self.sight)

	def draw(self):
		#the circle that follows you around
		showtracker = 0
		if showtracker:
			center = matrix([graphics.world_w/2, graphics.world_h/2])
			playerfromtracker = self.p.xy - self.tracker
			playerfromtracker += center
			if not self.h_bounded:
				playerfromtracker[0,0] %= graphics.world_w
			if not self.v_bounded:
				playerfromtracker[0,1] %= graphics.world_h
			playerfromtracker -= center

			pos = self.p.xy - playerfromtracker

			pygame.draw.circle(self.w, (255, 255, 255), (int(pos[0,0]), int(pos[0,1])), trackerradius, 1)
		
		for x in range(-1, 2, 1):
			for y in range(-1, 2, 1):
				self.s.blit(self.w, (graphics.border_thickness, graphics.top_space), self.recs[x][y])