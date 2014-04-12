from numpy import matrix, linalg

import test

rotation = matrix([[0,1], [-1,0]])
'''
def combine(c1,c2):
	adjacent_count = 0
	newshadowDict = c1.shadowDict[:]
	for k,v in c2.shadowDict:
		if
'''

class Convex(object):
	'''should typically be used to describe tiles in the map'''
	def __init__(self, pointlist, offset, extranormals = []):
		'''
		pointlist is a list of matrices in the shape of horizontal vectors.
		offset is one vector.
		'''

		#locations of points relative to world
		self.points = [p + offset for p in pointlist]

		#vectors going clockwise around the shape
		sides = [p - pointlist[i-1] for i, p in enumerate(pointlist)]

		#it's an anti-clockwise rotation by 90 degrees
		rotation = matrix([[0,1],[-1,0]])

		#these vectors point outward and have length 1
		normals = [(rotation * side.T).T for side in sides]
		normals += extranormals
		normals = [w / linalg.norm(w) for w in normals]

		# not sure what this is for
		self.usepoints = 0
		self.name = None

		# flipping it so that on a clock its between 1 o'clock and 6 o'clock inclusive
		# strictly speaking, have x nonnegative and y > -1
		for n in normals:
			if n[0,0] < 0 or n[0,1] == -1:
				n *= -1

		# remove parallels from the normals
		betternormals = no_parallels(normals)

		# tells you the shadow of itself after you project it along each normal
		self.shadowDict = find_shadows(betternormals, self.points)

		# 
		self.use = {p:0 for p in self.points}

	def repel(self, other = None, circle = None, radius = -1, corners = 0):
		'''
		returns the minimum displacement, if any, 
		required to push the other convex out.

		 bool circle:  - tells you whether it's a circle or a polygon
		  int radius:  - tells you the radius for collision
		               - if negative, use the object's own radius
		       other:  - does... nothing?
		bool corners:  - tells you whether or not to spend extra time and
		                 push using corners too.
		'''

		'''the basic way that this works is you
		look at each potential separating axis
		find the shadow of both guys on each one
		and push the guy out out as quickly as possible.'''
		
		'''set the normals to consider'''
		ns_to_consider = []
		my_ns = [k for k in self.shadowDict]
		other_ns = []

		if radius < 0 and circle:
			radius = circle.radius

		if circle:
			if corners:
				for p in self.points:
					if self.use[p]:
						disp = circle.xy - p
						disp = disp.astype(float)
						dist = linalg.norm(disp)
						if dist == 0:
							continue
						disp /= dist
						other_ns.append(disp)
		else:
			other_ns = [k for k in other.shadowDict]
		
		ns_to_consider = no_parallels(my_ns + other_ns)


		'''find all possible displacements'''
		disps = []
		for n in ns_to_consider:
			try:
				my_sh = self.shadowDict[n]
			except:
				my_sh = find_shadows([n], self.points)[n]

			if circle:
				center_sh = find_shadows(([n]), [circle.xy])[n]
				other_sh = (center_sh[0] - radius, center_sh[0] + radius)
			else:
				try:
					other_sh = self.shadowDict[n]
				except:
					other_sh = find_shadows([n], other.points)[n]

			my_l, my_r = my_sh
			other_l, other_r = other_sh

			if my_r <= other_l or my_l >= other_r:
				return matrix([0,0])
			else:
				move_it_left = my_l - other_r
				move_it_right = my_r - other_l
				if move_it_right < abs(move_it_left):
					disps.append((n, move_it_right))
				else:
					disps.append((n, move_it_left))

		'''pick the shortest displacement'''
		if disps:
			for n,m in disps:
				push = m * n
				test.lines.append(((circle.xy[0,0], circle.xy[0,1]), ((circle.xy + push)[0,0], (circle.xy + push)[0,1])))
			best_n, best_move = min(disps, key = lambda (n, m): abs(m))
			#best_n = best_n / linalg.norm(best_n)
			push = best_move * best_n
			test.lines.append(((circle.xy[0,0], circle.xy[0,1]), ((circle.xy + push)[0,0], (circle.xy + push)[0,1])))

			direction = best_n*rotation
			#if (best_n*vdir.T)[0,0] > 0:
			circle.vxy = (circle.vxy * direction.T)[0,0] * direction

			return best_move * best_n
		else:
			"no collision 2"
			return matrix([0,0])

def find_shadows(normals, points):
	'''makes a dictionarys of normals to shadows'''
	d = {}
	for n in normals:
		t = []
		for p in points:
			q = p*n.T
			t.append(q[0,0])
		d[n] = min(t), max(t)

	return d

def no_parallels(duped):
	'''cutting down vectors so that only one scalar multiple of each vector is present'''
	deco_duped = []
	for m in duped:
		if m[0,0]:
			a = m[0,1] / m[0,0]
			deco_duped.append((a,m))
		else:
			a = float('infinity')
			deco_duped.append((a,m))

	if len(duped) != len(deco_duped):
		print 'fail'
		return

	deco_no_dupes = []

	for a, m in deco_duped:
		if a not in (a0 for a0, m0 in deco_no_dupes):
			deco_no_dupes.append((a,m))

	no_dupes = [m for a, m in deco_no_dupes]
	return no_dupes