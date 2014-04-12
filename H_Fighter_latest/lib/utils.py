import graphics

def body_copies(xy, radius):
	copies = []
	ixy = xy.astype(int)
	for x in range(-1, 2, 1):
		if x and 0 < ixy[0,0] + radius * -x < graphics.world_w:
			continue
		for y in range(-1, 2, 1):
			if y and 0 < ixy[0,1] + radius * -y < graphics.world_h:
				continue
			copies.append((x, y))
	return copies