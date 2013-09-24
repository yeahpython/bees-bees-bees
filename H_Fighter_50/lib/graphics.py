bw = 30
bh = 30

world_tw = 0
world_th = 0

def load(file_in):
	file_descriptor = open(file_in)
	lines = file_descriptor.readlines()
	global world_th, world_tw, world_w, world_h, world_size
	world_th = len(lines)-1
	world_tw = len(lines[-1])
	world_w = world_tw * bw
	world_h = world_th * bh
	world_size = (world_w, world_h)
	file_descriptor.close()

#world_w = world_tw * bw
#world_h = world_th * bh
#world_size = (world_w, world_h)

screen_w = 910
screen_h = 610
screen_size = (screen_w, screen_h)

border_thickness = 5

top_space = 5

disp_w = screen_w - 2*(border_thickness)
disp_h = screen_h - top_space - border_thickness
disp_size = (disp_w, disp_h)


background = [10, 30, 0]#(80, 128, 75)
foreground = [0, 0, 0]
outline = [255,255,0]
CLEAR_SCREEN = 0
REDRAW_ROOM = 0

colorcycle = [(0, 0, 255), (0, 255, 255), (0, 255, 0), (255, 0, 0), (255, 0, 255),]
colorcycle2 = [(255,55,155)]#[(100, 230, 230)]

