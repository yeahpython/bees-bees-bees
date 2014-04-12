class Palette(object):
	def __init__(self):
		self.max = [1.0, 1.0, 1.0, 1.0]
		self.min = [0.0, 0.0, 0.0, 0.0]
		self.scaling = [1.0, 1.0, 1.0, 1.0]
	
	def renew_coloring_rule(self, bees, speed = 0.1):
		x = zip(*[b.outputs for b in bees])
		newmax = [max(x[i]) for i in range(4)]
		newmin = [min(x[i]) for i in range(4)]
		for i in range(4):
			self.max[i] *= (1-speed)
			self.max[i] += speed * newmax[i]
			self.min[i] *= (1-speed)
			self.min[i] += speed * newmin[i]
		self.scaling = [1.0 / (abs(M- m) + 0.01) for M, m in zip(self.max, self.min)]

	def get_color(self, b):
		outputs = b.outputs[:]
		for i in range(4):
			outputs[i] = (outputs[i] - self.min[i]) * self.scaling[i]
		color = [outputs[1], outputs[0], (outputs[2] - outputs[3] + 1) / 2]
		color = [min(i, 1) for i in color]
		color = [max(i, 0) for i in color]
		color = [int(50 + i*205) for i in color]
		return color