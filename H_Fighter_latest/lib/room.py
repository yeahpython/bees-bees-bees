'''This file defines a room for the platformer.'''

import graphics
from graphics import bw, bh
import tile
import pygame
import collision
import random
from numpy import matrix, linalg, array
import test
import bee
import convex
import messages
import math
from random import randrange
import time
import palette
from game_settings import *
# Tile count in a room
# rows = None #graphics.world_h / bh
# cols = None #graphics.world_w / bw

USE_IMAGES = 0
DRAW_RANDOM_CIRCLES = 1
VISUALIZE_MAP_LOAD = 1
TIME_INITIALIZATION = 0

# increase this to make a every distint and impermeable floor / wall
forcewall = 0
forcefloor = 1
noceiling = 1

horizontalbias = 0

mapcolors = {
    "#": graphics.foreground,
    " ": graphics.background,
    "!": [0, 0, 255],
    "Q": [255, 0, 255],
    "E": [0, 255, 255],
    "Z": [255, 255, 0],
    "C": [255, 0, 0],
    "~": [100, 100, 100],
    "^": [100, 100, 100],
    "*": [255, 0, 255],
}


def tuplefrommatrix(mat):
    return (mat[0, 0], mat[0, 1])


def substitute(lines, i, j, character):
    lines[i] = lines[i][:j] + character + lines[i][j + 1:]

'''add slanted walls and extra walls where necessary to make the map smooth'''


def roundedges(lines, columnoverride=0, rowoverride=0):
    substitutions = []
    # for i in range(rows):
    #   print lines[i][:cols]
    if not columnoverride:
        columnoverride = cols
    if not rowoverride:
        rowoverride = rows

    for i in range(rowoverride):
        for j in range(columnoverride):
            if lines[i][j] == "#":
                continue
            # print i, j, "------"
            adjacents = []
            for di in range(-1, 2):
                #thisline = ""
                r = (i + di) % rows
                for dj in range(-1, 2):
                    c = (j + dj) % cols
                    #thisline += "["
                    #thisline += lines[r][c]
                    #thisline += "]"
                    if (di + dj) % 2 == 1:
                        adjacents.append(lines[r][c])
                # print thisline

            above = adjacents[0]
            left = adjacents[1]
            right = adjacents[2]
            below = adjacents[3]

            wall_above = (above in "Z#C")
            wall_left = (left in "E#C")
            wall_right = (right in "Q#Z")
            wall_below = (below in "Q#E")
            # print above, left, right, below
            # print wall_above, wall_left, wall_right, wall_below
            tag = " "
            if wall_above and wall_below:
                tag = "#"
            elif wall_left and wall_right:
                tag = "#"
            elif (wall_above and wall_left):
                tag = "Q"
            elif (wall_above and wall_right):
                tag = "E"
            elif (wall_below and wall_left):
                tag = "Z"
            elif (wall_below and wall_right):
                tag = "C"
            if tag != " ":
                drawpoint(i, j, lines, tag)
            # print tag
            #substitute(lines, i, j, tag)
            substitutions.append((i, j, tag))

    for i, j, tag in substitutions:
        substitute(lines, i, j, tag)

    # for i in range(rows):
    #   print lines[i][:cols]


def congeal(lines, thoroughness):
    to_add = []
    for i in range(rows):
        for j in range(cols):
            if random.random() > thoroughness:
                continue
            nonspacecount = 0
            for di in range(-1, 2):
                for dj in range(-1, 2):
                    if not (di and dj):
                        r = (i + di) % rows
                        c = (j + dj) % cols
                        if lines[r][c] != ' ':
                            nonspacecount += 1
            if nonspacecount:
                to_add.append((i, j))
                drawpoint(i, j, lines, "#")

    n = 0
    for i, j in to_add:
        n += 1
        substitute(lines, i, j, "#")


def generateringmap(r, c, inrad, outrad):
    out = []
    for i in range(-r / 2, r / 2):
        out.append("")
        for j in range(-c / 2, c / 2):
            norm2 = i**2 + j**2
            next = " "
            if norm2 > outrad**2 or norm2 < inrad**2:
                next = "#"

            out[-1] = out[-1] + next

    roundedges(out, c, r)
    for line in out:
        print line
    return out


def drawpoint(i, j, lines, override=0):
    if not VISUALIZE_MAP_LOAD:
        return
    m_dy = 250.0 / rows
    m_dx = m_dy

    predictedwidth = m_dx * cols
    predictedheight = m_dy * rows

    m_offset_x = graphics.disp_w / 2 - predictedwidth / 2
    m_offset_y = 20

    left = m_offset_x + j * m_dx
    top = m_offset_y + i * m_dy
    right = m_offset_x + (j + 1) * m_dx
    bottom = m_offset_y + (i + 1) * m_dy
    left, top, right, bottom = int(left), int(top), int(right), int(bottom)

    box = pygame.Rect(left, top, right - left, bottom - top)

    character = lines[i][j]
    if override:
        character = override

    color = mapcolors[character]

    if character == "#":
        pygame.draw.rect(pygame.display.get_surface(), [255, 255, 255], box)
    else:
        pygame.draw.rect(
            pygame.display.get_surface(), graphics.background, box)
        c = character
        centerx = m_offset_x + (j + 0.5) * m_dx
        centery = m_offset_y + (i + 0.5) * m_dy
        centerx = int(centerx)
        centery = int(centery)
        if c != " " and c != "!":
            pointlist = []
            if c == "Q":
                pointlist.append((left, top))
                pointlist.append((right, top))
                pointlist.append((left, bottom))
            elif c == "E":
                pointlist.append((left, top))
                pointlist.append((right, top))
                pointlist.append((right, bottom))
            elif c == "Z":
                pointlist.append((left, top))
                pointlist.append((right, bottom))
                pointlist.append((left, bottom))
            elif c == "C":
                pointlist.append((left, bottom))
                pointlist.append((right, top))
                pointlist.append((right, bottom))
            else:
                print "didn't know what to do with character", c
                return
            pygame.draw.polygon(
                pygame.display.get_surface(), [255, 255, 255], pointlist)


def movecharacter(lines, low, high, rad, i, j):
    nonspacecount = 0
    for di in range(-rad, rad + 1):
        for dj in range(-rad, rad + 1):
            if di or dj:
                # set floor from 0 to 1 to set how fixed the floor is
                floor = forcefloor
                wall = forcewall

                if noceiling and i + di < 3:
                    nonspacecount -= 10
                    continue
                if floor and i + di >= rows and random.random() < floor:
                    nonspacecount += 2
                    continue
                if wall and (j + dj == cols or j + dj == -1) and random.random() < wall:
                    nonspacecount += 1
                    continue

                r = (i + di) % rows
                c = (j + dj) % cols
                if lines[r][c] != ' ':
                    nonspacecount += 1
                    if di == 0:
                        nonspacecount += int(random.random()
                                             * 2 * horizontalbias)
                    if dj == 0:
                        nonspacecount -= int(random.random()
                                             * 2 * horizontalbias)
    # case for wall

    if (nonspacecount < low and lines[i][j] != ' ') or (nonspacecount > high and lines[i][j] == ' '):
        mrad = 5

        movement_directions = [(x, y) for x in range(-1, 2)
                               for y in range(1, 2) if x or y]
        movement_directions = [(-1, 1), (0, 1), (1, 1)]
        di, dj = random.choice(movement_directions)

        i2, j2 = i + 0, j + 0

        for x in range(100):
            if lines[(i2 + di) % rows][(j2 + dj) % cols] != " ":
                break
            i2 += di
            j2 += dj
            #i2 = i+randrange(2*mrad + 1) - mrad
            #j2 = j+randrange(2*mrad + 1) - mrad
            i2 %= rows
            j2 %= cols

        char = lines[i2][j2]
        substitute(lines, i2, j2, lines[i][j])
        substitute(lines, i, j, char)
        drawpoint(i2, j2, lines)
        drawpoint(i, j, lines)


def movecharacters(lines, low, high, runs, r):
    for x in range(runs):
        for i in range(rows):
            for j in range(cols):
                movecharacter(
                    lines, low, high, r, randrange(rows), randrange(cols))
            # if VISUALIZE_MAP_LOAD:
            #   pygame.display.flip()


def randomlymodify(lines):
    # for i in range(rows):
    #   for j in range(cols):
    # if lines[i][j] == "#":
    #           drawpoint(i,j,lines)
    # pygame.display.flip()

    for i in range(rows):
        for j in range(cols):
            if random.random() < settings[RANDOM_TILE_DENSITY]:
                substitute(lines, i, j, '#')
            else:
                substitute(lines, i, j, ' ')
            drawpoint(i, j, lines)

    low = settings[RANDOM_MAP_LOW]
    high = settings[RANDOM_MAP_HIGH]
    runs = settings[RANDOM_MAP_RUNS]
    r = settings[RANDOM_MAP_RADIUS]
    movecharacters(lines, low, high, runs, r)

    #movecharacters(lines, 2, 7, 10, 1)

    congeal(lines, thoroughness=settings[CONGEAL_THOROUGHNESS])
    roundedges(lines)
    if VISUALIZE_MAP_LOAD:
        pygame.display.flip()
    for s in lines:
        print s


def globalize_dimensions(r, c):
    global rows, cols
    rows = r
    cols = c


def load(file_in):
    messages.colorBackground()
    file_descriptor = open(file_in)
    lines = file_descriptor.readlines()
    global rows, cols
    rows = len(lines) - 1
    cols = len(lines[-1])

    if settings[GENERATE_RANDOM_MAP]:
        messages.say('generating random terrain', down=5)
        randomlymodify(lines)
        for line in lines:
            print line[:cols]

    file_descriptor.close()
    tiles = []
    for c in range(cols):
        tiles.append([])
        for r in range(rows):
            # Essentially we used the character (e.g. 'Q') to access the
            # dictionary entries (which are Tile object instances)
            tiles[c].append(tile.tile[lines[r][c]])
            # Notice that there is a transposition here.

    return Room(tiles, lines)


def normal_and_normpos(s):
    normal = s[1][0, 0], s[1][0, 1]
    point = s[0][0]
    pos = point[0] * normal[0] + point[1] * normal[1]
    if normal[0] < 0 or normal[1] == -1:
        pos *= -1
        normal = [-x for x in normal]
    else:
        normal = [x for x in normal]
    return normal, pos


def flipkey(k):
    (normal1, normal2), pos = k
    return (-1 * normal1, -1 * normal2), -1 * pos


def waitforkey(k):
    clock = pygame.time.Clock()
    done = 0
    while not done:
        clock.tick(60)
        key_presses = pygame.event.get(pygame.KEYDOWN)
        if pygame.key.get_pressed()[k]:
            break

LABEL_SIDES = 0


class Room(object):

    def __init__(self, tiles, lines):
        #generateringmap(80, 60, 20, 30)
        self.lines = lines
        graphics.extract_dimensions(self.lines)
        nextmessage = 6
        self.cols, self.rows = cols, rows

        for i in range(rows):
            for j in range(cols):
                drawpoint(i, j, lines)

        self.tiles = tiles
        self.camera = 0
        self.madness = 0
        self.stasis = False
        self.roomnumber = 0
        self.signal_new_tree = 0

        nextmessage = messages.say("reducing sides", 0, down=nextmessage)
        self.reduce_sides()

        nextmessage = messages.say("collision stuff", 0, down=nextmessage)
        self.optimize_convexes()

        if (DRAW_RANDOM_CIRCLES):
            nextmessage = messages.say(
                "computing density", 0, down=nextmessage)
            self.compute_densities()

        self.object_directory = [[[]
                                  for r in range(rows)] for c in range(cols)]
        self.background = pygame.Surface((graphics.world_w, graphics.world_h))
        self.collisionfield = pygame.Surface(
            (graphics.world_w, graphics.world_h))
        self.bgw = graphics.world_w
        self.bgh = graphics.world_h
        self.a = 0
        self.start_position = matrix([100, 100])
        for r in range(rows):
            for c in range(cols):
                if self.lines[r][c] == '!':
                    self.start_position = matrix(
                        [bw * c + bw / 2, bh * r + bh / 2])

        nextmessage = messages.say("drawing background", 0, down=nextmessage)
        if TIME_INITIALIZATION:
            backgroundstarttime = time.time()
        # Note that this sets the start position to wherever the '!' is
        self.draw(self.background)
        self.background.convert()
        self.draw(self.collisionfield, collision_only=1)
        self.collisionfield.convert()
        self.pixels = pygame.PixelArray(self.collisionfield)
        if TIME_INITIALIZATION:
            print "drawing background took", time.time() - backgroundstarttime, "seconds"

        self.food = []
        self.bees = []
        self.deadbees = []
        self.player = None
        self.topbar = None
        self.beehistory = 0
        self.bestbees = []
        self.timetosave = 100
        self.h = None
        self.dirtyareas = []
        self.visibles = []
        self.bullets = []
        self.painter = palette.Palette()
        self.recentdeaths = 0
        self.freespots = [(r, c) for r in range(rows)
                          for c in range(cols) if self.lines[r][c] == " "]

        # for r,c in self.freespots:
        #   pygame.draw.circle(self.background, [255, 255, 255], (int((c+0.5)*bw), int((r+0.5)*bh)), 10, 1)

        nextmessage = messages.say("precomputing vision", 0, down=nextmessage)
        self.precompute_vision()

    def globalize_dimensions(self):
        global rows, cols
        rows = self.rows
        cols = self.cols

    def precompute_vision(self):

        if TIME_INITIALIZATION:
            visionstarttime = time.time()
        self.visiondirectory = [[[] for r in range(rows)] for c in range(cols)]
        eyes = [(1, 0), (1, 1), (0, 1), (-1, 0),
                (1, -1), (-1, 1), (-1, -1), (0, -1)]
        #eyes = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        sight_distance = graphics.screen_h / 2

        directions = [] + eyes
        for c in range(cols):
            for r in range(rows):
                sights = []
                xy = matrix([(c + 0.5) * bw, (r + 0.5) * bh])
                for x, y in directions:
                    n = (x**2 + y**2)**0.5
                    x0 = x / n
                    y0 = y / n
                    sights.append(
                        bee.look2(self, xy[0, 0], xy[0, 1], x0, y0, sight_distance, bw, bh))

                infoz = []
                for targ in sights:
                    if targ:
                        (x, y), name = targ
                        posx, posy = x * bw + 16, y * bh + 16

                        '''finding the real shortest-path distance with wraparound'''
                        displacement = matrix(
                            [posx - xy[0, 0], posy - xy[0, 1]])
                        center = matrix(
                            [graphics.world_w / 2, graphics.world_h / 2])
                        displacement += center
                        displacement[0, 0] %= graphics.world_w
                        displacement[0, 1] %= graphics.world_h
                        displacement -= center

                        dist = linalg.norm(displacement)
                        infoz.append(dist / sight_distance)
                    else:
                        infoz.append(1.0)
                self.visiondirectory[c][r] = infoz

        if TIME_INITIALIZATION:
            print "vision took", time.time() - visionstarttime, "seconds"

    def compute_densities(self):
        if TIME_INITIALIZATION:
            densitystarttime = time.time()

        rs = len(self.tiles[0])
        cs = len(self.tiles)
        self.density = [[0 for y in range(rs)] for x in range(cs)]
        for y in range(rs):
            for x in range(cs):
                for x0 in range(-10, 11):
                    for y0 in range(-10, 11):
                        otherx = (x + x0) % cs
                        othery = (y + y0) % rs
                        self.density[x][
                            y] += self.tiles[otherx][othery].name != 'empty'
                self.density[x][y] *= (y + 1)**0.9
                self.density[x][y] /= 200
        if TIME_INITIALIZATION:
            print "density took", time.time() - densitystarttime, "seconds"

    def optimize_convexes(self):
        '''creates and improves convexes by showing which directions they'll push things.'''

        if TIME_INITIALIZATION:
            convexstarttime = time.time()
        self.convex_directory = [
            [None for r in range(rows + 4)] for c in range(cols + 4)]

        if TIME_INITIALIZATION:
            whoabro = time.time()

        '''creating all the convexes. They're put in the convex_directory.'''
        for c in range(-2, cols + 2):
            for r in range(-2, rows + 2):
                tps = self.tiles[c % cols][r % rows].pointlist
                if not tps:
                    continue
                mps = [matrix([x, y]) for x, y in tps]
                offset = matrix([bw * c, bh * r])

                adjacents = []
                adj_string = ""
                for di in range(-1, 2):
                    #thisline = ""
                    r2 = (r + di) % rows
                    for dj in range(-1, 2):
                        c2 = (c + dj) % cols
                        #thisline += "["
                        #thisline += lines[r][c]
                        #thisline += "]"
                        if (di + dj) % 2 == 1:
                            adjacents.append(self.lines[r2][c2])
                        adj_string += self.lines[r2][c2]
                    # print thisline

                above = adjacents[0]
                left = adjacents[1]
                right = adjacents[2]
                below = adjacents[3]

                extranormals = []

                if adj_string not in ["   ######", "#########", "Z  ######", "#  ######", "  #######"]:
                    if above in "Z#" and right in "Z#" and adj_string[2] in " QEC":
                        extranormals.append(matrix([1, -1]))
                    if below in "E#" and left in "E#" and adj_string[6] in " QZC":
                        extranormals.append(matrix([-1, 1]))
                    if above in "C#" and left in "C#" and adj_string[0] in " QZE":
                        extranormals.append(matrix([-1, -1]))
                    if below in "Q#" and right in "Q#" and adj_string[8] in " ZCE":
                        extranormals.append(matrix([1, 1]))

                a = convex.Convex(mps, offset, extranormals)
                a.name = self.tiles[c % cols][r % rows].name
                self.convex_directory[c][r] = a

        chrbro = time.time()

        if TIME_INITIALIZATION:
            print "loading convexes took", chrbro - whoabro, "seconds."

        '''make a list of all sides'''
        all_sides = []
        for s in self.sides:
            all_sides.extend(s.side)

        pointcounter = 0
        for p in all_sides:
            ex, ey = p[0, 0], p[0, 1]
            l = math.ceil(ex / bw) - 1
            r = math.floor(ex / bw)
            t = math.ceil(ey / bh) - 1
            b = math.floor(ey / bh)

            l = int(l)
            r = int(r)
            t = int(t)
            b = int(b)
            '''l, r, t, b tell you the range of cells spanned by the side.
            The ceiling and floor stuff is designed so that, say,
            in the case that a point is in the middle, l = r'''

            mx = int(ex / bw)
            my = int(ey / bh)

            if l == r or t == b:
                continue

            '''we've filtered out the points in the middles of blocks'''

            '''essentially we only activate points that are at endpoints of lines'''
            for posx in range(l, r + 1):
                for posy in range(t, b + 1):
                    c = self.convex_directory[posx][posy]
                    if c:
                        for q in c.points:
                            if linalg.norm(p - q) == 0:
                                if not c.use[q]:
                                    pointcounter += 1
                                c.use[q] = 1
                                # print "we're using {0} now".format(q)
                                # print "\n", c.use, "\n"
                                break
                        else:
                            pass
                            # print "none of the elements of {0} equal
                            # {1}".format(c.points, p)

            # print "found", pointcounter, "points"

        '''elimating overlapping normals'''
        self.adjust_convexes()

        if TIME_INITIALIZATION:
            print "convexes took", time.time() - convexstarttime, "seconds"

    # def pointcheck(self, point):
    #   '''true if given tuple is solid'''
    #   x, y = point[0] % self.collisionfield.get_width(),point[1] %self.collisionfield.get_height()
    #   if not isinstance(x, int) or not isinstance(y, int):
    #       print "watch out, pointcheck wants the inputs to be integers!"
    #       print "type(", x, ")", "aint an integer, it's", type(x)
    # coloratpoint = self.collisionfield.get_at((x, y))
    #   return bool(self.pixels[x, y])

    def pointcheck(self, point):
        x, y = point[0] % self.collisionfield.get_width(
        ), point[1] % self.collisionfield.get_height()
        col, row = x / bw, y / bh
        dx, dy = x % bw, y % bw
        char = self.lines[row][col]
        if char == " ":
            return False
        elif char == "#":
            return True
        elif char == "Q":
            # will not work if bw != bh
            return dx + dy < bw
        elif char == "E":
            return dy < dx
        elif char == "Z":
            return dy > dx
        elif char == "C":
            return dx + dy > bw
        else:
            return False

    def reduce_sides(self):
        if TIME_INITIALIZATION:
            sidestarttime = time.time()
        self.sides = self.get_sides(matrix(
            [[-1, -1]]), matrix([[graphics.world_w + 1, graphics.world_h + 1]]), checknormals=0, verbose=1)
        # print "I have", len(self.sides), "sides."
        self.side_directory = [[[]
                                for r in range(rows + 2)] for c in range(cols + 2)]
        self.give_tiles_better_sides()

        #self.lines = []
        # numbering the sides
        self.sidelabels = []
        if LABEL_SIDES:
            for i, side in enumerate(self.sides):  # For all numbered sides
                # print "\n\n\n\n\n\n", array(side.side[0])[0], "\n\n\n"#,
                # array(side.side[0])[0]
                start = array(side.side[0])[0]
                n = array(side.normal)[0]
                start = [x - 0.05 * y for (x, y) in zip(start, n)]
                end = array(side.side[1])[0]
                end = [x - 0.05 * y for (x, y) in zip(end, n)]

                font = pygame.font.SysFont("Droid Serif", 15)
                text = font.render(str(i), 1, (255, 255, 255))
                textpos = text.get_rect(
                    centerx=(start[0] + end[0]) / 2, centery=(start[1] + end[1]) / 2)
                self.sidelabels.append([start, end, text, textpos])
        if TIME_INITIALIZATION:
            print "sides took", time.time() - sidestarttime, "seconds"

    def adjust_convexes(self):
        '''modifies shadows and deactivates sides as necessary to improve collision testing'''
        optimize = True

        if optimize:

            known_side_mods = {}

            dirs = {}
            dirs[(0, 1)] = "right"
            dirs[(0, -1)] = "left"
            dirs[(1, 0)] = "bottom"
            dirs[(-1, 0)] = "top"

            '''side modification'''
            for x in range(cols):
                for y in range(rows):
                    '''want to kill some sides of this shape'''
                    c = self.convex_directory[x][y]
                    if not c:
                        continue

                    for x0, y0 in dirs:
                        '''check each neighbor for stickiness'''
                        xo = x + x0
                        yo = y + y0
                        co = self.convex_directory[xo][yo]
                        if not co:
                            continue
                        for normal in c.shadowDict:
                            for other_normal in co.shadowDict:
                                if linalg.norm(other_normal + normal) < 0.1:
                                    # if there is an opposing normal
                                    if c.shadowDict[normal][1] + co.shadowDict[other_normal][1] < 0.1:
                                        c.shadowDict[normal] = c.shadowDict[
                                            normal][0], float('infinity')
                                        co.shadowDict[other_normal] = co.shadowDict[
                                            other_normal][0], float('infinity')
            for row, entries in enumerate(self.convex_directory):
                for col, c in enumerate(entries):
                    if c != None:
                        d = {}
                        for n, r in c.shadowDict.iteritems():
                            if r != (-float('infinity'), float('infinity')):
                                d[n] = r
                        c.shadowDict = d

        '''deleting convexes and drawing testlines'''
        for x in range(cols):
            for y in range(rows):
                c = self.convex_directory[x][y]
                if not c:
                    continue
                if not c.shadowDict and all([use == False for point, use in c.use.iteritems()]):
                    self.convex_directory[x][y] = None
                else:
                    '''draw normals'''
                    ex, ey = (x + 0.5) * bw, (y + 0.5) * bh
                    for n in c.shadowDict:
                        mi, ma = c.shadowDict[n]
                        if ma != float('infinity'):
                            test.backgroundmarkers.append(
                                ((ex, ey), (ex + 10 * n[0, 0], ey + 10 * n[0, 1])))
                        # if mi != -float('infinity'):
                        #   test.backgroundmarkers.append(( (ex,ey), (ex-10*n[0,0], ey-10*n[0,1])))

                    '''draw corner'''
                    for k, v in c.use.iteritems():
                        if v:
                            #ex, ey = k[0,0], k[0,1]
                            test.backgroundmarkers.append(
                                ((ex, ey), (k[0, 0], k[0, 1])))
                            test.backgroundpointmarkers.append(
                                (k[0, 0], k[0, 1]))

                    '''draw box'''
                    p = ((x + 0.4) * bw, (y + 0.4) * bh)
                    q = ((x + 0.6) * bw, (y + 0.4) * bh)
                    r = ((x + 0.6) * bw, (y + 0.6) * bh)
                    s = ((x + 0.4) * bw, (y + 0.6) * bh)
                    test.backgroundmarkers.extend(
                        [(p, q), (q, r), (r, s), (s, p)])

    def update(self):
        self.a += 1
        '''self.timetosave -= 1

                                if self.timetosave < 0:
                                    for b in self.bestbees:
                                        #print b.score,
                                        self.h.save_bee(b)
                                    self.h.savedata()
                                    self.timetosave = 100'''

        self.object_directory = [[[]
                                  for r in range(rows)] for c in range(cols)]

        '''key_presses = pygame.event.get(pygame.KEYDOWN)
                                if pygame.key.get_pressed()[pygame.K_m]:
                                    self.madness +=1
                                    self.madness %=2
                                    for bee in self.bees:
                                        bee.madness = self.madness'''

        if not self.bees:
            self.topbar.flash("extinction :(")
            self.generate_bees(settings[MAXIMUM_BEES] + 1)
            self.signal_new_tree = 1
        elif not self.a % 1:
            self.painter.renew_coloring_rule(self.bees)

    def generate_bees(self, n):
        '''yo, make sure self.player is actually valid'''
        for k in range(n):
            b = bee.Bee(self)
            b.randomize_color()
            b.findplayer(self.player)
            b.xy = self.player.xy * 1
            b.randomize_position(100)
            self.bees.append(b)
            b.rank = k
            b.ancestry = (k,)

        self.painter.renew_coloring_rule(self.bees, 1)

    def draw(self, surface, collision_only=0):
        '''flat color'''

        if collision_only:
            surface.fill([0, 0, 0])
        else:
            surface.fill(graphics.background)
        # surface.fill([70,70,70])

        '''random circles'''
        if DRAW_RANDOM_CIRCLES and not collision_only:
            for k in range(rows * cols * 8):
                x = random.random() * graphics.world_w
                y = random.random() * graphics.world_h
                xvar = 0
                yvar = 0
                x0, y0 = int(x / bw + random.random() * (2 * xvar) -
                             xvar), int(y / bh + random.random() * (2 * yvar) - yvar)
                x0 %= cols
                y0 %= rows
                r = random.random() * graphics.bw * 2
                #r = random.random()*graphics.bw * (1 + 0.12*self.density[x0][y0])
                red = min(1 * self.density[x0][y0] + random.random() * 10, 255)
                green = min(
                    1 * self.density[x0][y0] + 0 + random.random() * 20, 255)
                blue = min(
                    3 * self.density[x0][y0] + 3 + random.random() * 20, 255)
                c = (red, green, blue)
                for a in range(-1, 2, 1):
                    for b in range(-1, 2, 1):
                        pygame.draw.circle(
                            surface, c, [int(x) + a * graphics.world_w, int(y) + b * graphics.world_h], int(r))
                        #box = pygame.Rect(int(x) - r, int(y) - r, 2*r, 2*r)
                        #pygame.draw.rect(surface, c, box, 0)
            for t in range(10000):
                x = random.randrange(-100, surface.get_width(), 1)
                y = random.randrange(-100, surface.get_height(), 1)
                dx = random.randrange(-4, 5, 1)
                dy = random.randrange(-4, 5, 1)
                surface.blit(
                    surface, (x, y, 100, 100), (x + dx, y + dy, 100, 100))

        # for x in range(cols):
        #   for y in range(rows):
        #       r = pygame.Rect(x*bw, y*bh, bw, bh)
        #       pygame.draw.rect(surface, [min(27*self.density[x][y] + random.random() * 100, 255)]*3, r)
        if collision_only:
            tilecolor = [0, 0, 1]
        else:
            tilecolor = graphics.foreground

        '''Tiles'''
        if collision_only:
            for x in range(cols):
                for y in range(rows):
                    this_tile = self.tiles[x][y]  # For each tile
                    if this_tile.name == 'empty':
                        continue
                    else:
                        if not this_tile.pointlist:
                            continue
                        pointlist = [(x * bw + x0, y * bh + y0)
                                     for x0, y0 in this_tile.pointlist]  # Draw shape
                        pygame.draw.polygon(surface, tilecolor, pointlist)

        else:
            for x in range(cols):
                power = 15
                for y in [Y % rows for Y in range(10 * rows)]:
                    rand = random.random()
                    if rand > 0.95:
                        x += 1
                        x %= cols
                    if rand < 0.05:
                        x -= 1
                        x %= cols
                    this_tile = self.tiles[x][y]  # For each tile
                    if this_tile.name == 'empty':
                        power = 15
                    elif this_tile.name == 'start':
                        pass
                    else:
                        if this_tile.name in ['bottomleft', 'bottomright'] or self.tiles[(x + 1) % cols][(y - 1) % rows].name == 'empty' or self.tiles[(x - 1) % cols][(y - 1) % rows].name == 'empty':
                            power = 15
                        if USE_IMAGES:
                            # Blit image
                            surface.blit(this_tile.surface, (x * bw, y * bh))
                        else:
                            if this_tile.name == 'bounce':
                                pointlist = [(x * bw + x0, y * bh + y0)
                                             for x0, y0 in ((15, 0), (30, 15), (30, 30), (15, 15), (0, 30), (0, 15))]
                                pygame.draw.polygon(
                                    surface, [0, 255, 100], pointlist)
                                # pygame.draw.circle(
                                # surface, (255, 0, 0), (x * bw + bw / 2, y *
                                # bh + bh / 2), bh / 2)
                            elif this_tile.name == 'end':
                                pointlist = [(x * bw + x0, y * bh + y0)
                                             for x0, y0 in ((15, 0), (30, 15), (15, 30), (0, 15))]
                                pygame.draw.polygon(
                                    surface, [0, 200, 200], pointlist)
                                # pygame.draw.circle(
                                # surface, (255, 0, 0), (x * bw + bw / 2, y *
                                # bh + bh / 2), bh / 2)
                            if not this_tile.pointlist:
                                continue
                            # Draw shape
                            pointlist = [(x * bw + x0, y * bh + y0)
                                         for x0, y0 in this_tile.pointlist]
                            #g = len(self.side_directory[x][y])
                            # if collision_only:
                            #   pygame.draw.polygon(surface, tilecolor, pointlist)
                            # else:
                            #   pygame.draw.polygon(surface, graphics.foreground, pointlist)
                            pygame.draw.polygon(
                                surface, [100 + 10 * power for k in graphics.foreground, 0, 255], pointlist)
                            if power > 0:
                                power -= 1

        '''Sides'''
        if not collision_only:
            for i, side in enumerate(self.sides):  # For all numbered sides
                start = array(side.side[0])[0]
                n = array(side.normal)[0]
                #start = [x - 0.05*y for (x,y) in zip(start, n)]
                end = array(side.side[1])[0]
                #end = [x - 0.05*y for (x,y) in zip(end, n)]

                font = pygame.font.SysFont("Droid Serif", 15)
                text = font.render(str(i), 1, (255, 255, 255))
                textpos = text.get_rect(
                    centerx=(start[0] + end[0]) / 2, centery=(start[1] + end[1]) / 2)

                # print "\n\n\n\n\n\n", array(side.side[0])[0], "\n\n\n"#, array(side.side[0])[0]
                # try:
                    #start, end, text, textpos = self.sidelabels[i]
                # pygame.draw.line(surface, graphics.outline, start, end, 1) #
                # Draw the offsetted lines
                approxpoints = []

                juiciness = settings[JUICINESS]
                if juiciness == 3:
                    '''experimental'''
                    pieces, dev, bulge, thickness = 1, 0, 0, 5
                elif juiciness == 2:
                    '''choose this for juiciness'''
                    pieces, dev, bulge, thickness = 5, 1, 5, 5
                elif juiciness == 1:
                    '''choose this for semijuiciness'''
                    pieces, dev, bulge, thickness = 2, 2, 0, 1
                else:
                    '''choose this for futuristicness'''
                    pieces, dev, bulge, thickness = 1, 0, 0, 1

                for x in range(pieces + 1):
                    approxpoints.append(
                        [start[0] + x * float(end[0] - start[0]) / pieces, start[1] + x * float(end[1] - start[1]) / pieces])

                for x in range(1, pieces):
                    d = min(x, pieces - x)
                    for i in range(2):
                        # pass
                        approxpoints[x][i] += (random.random() * 2 - 1) * dev
                        approxpoints[x][i] -= bulge * float(d) / pieces * n[i]

                for x in range(pieces):
                    pygame.draw.line(surface, graphics.outline, approxpoints[x], approxpoints[
                                     x + 1], thickness)  # Draw the offsetted lines

                #pygame.draw.circle(surface, [0,0,255], [int(k) for k in start], 2)
                #pygame.draw.circle(surface, [0,0,255], [int(k) for k in end], 2)
                #surface.blit(text, textpos)
                # except:
                #   continue

    def repair(self, surface):
        for a in self.dirtyareas:
            surface.blit(self.background, a, a)
        self.dirtyareas = []

    def get_sides(self, xy, dxy, checknormals=1, verbose=0):
        '''Given a start and end, returns a list of sides'''
        # Selecting bounding box
        x, y = array(xy)[0]
        dx, dy = array(dxy)[0]
        qleft = int(min(x, x + dx) - 1) / bw
        qright = int(max(x, x + dx) + 1) / bw + 1
        qtop = int(min(y, y + dy) - 1) / bh
        qbottom = int(max(y, y + dy) + 1) / bh + 1

        sides = []  # This will be a huge list of Side objects.
        testboxes = []  # Here are the tiles that I will check for sides
        # Getting tiles from bounding box
        for col in range(qleft, qright):
            for row in range(qtop, qbottom):
                if -1 <= col <= cols + 1 and -1 <= row <= rows + 1:
                    i = row
                    j = col
                    adjacents = []
                    for di in range(-1, 2):
                        #thisline = ""
                        r = (i + di) % rows
                        for dj in range(-1, 2):
                            c = (j + dj) % cols
                            #thisline += "["
                            #thisline += lines[r][c]
                            #thisline += "]"
                            if (di + dj) % 2 == 1:
                                adjacents.append(self.lines[r][c])
                        # print thisline

                    above = adjacents[0]
                    left = adjacents[1]
                    right = adjacents[2]
                    below = adjacents[3]

                    wall_above = (above in "Z#C")
                    wall_left = (left in "E#C")
                    wall_right = (right in "Q#Z")
                    wall_below = (below in "Q#E")

                    if self.lines[i % rows][j % cols] == "#" and wall_above and wall_left and wall_right and wall_below:
                        continue

                    # we can definitely do more checks, but for now I'll just
                    # be naive about it.
                    tile = self.tiles[col % cols][row % rows]
                    for ((x1, y1), (x2, y2)), normal in tile.sides:
                        if linalg.norm(normal - matrix([0, 1])) < 0.1 and wall_above:
                            continue
                        if linalg.norm(normal - matrix([0, -1])) < 0.1 and wall_below:
                            continue
                        if linalg.norm(normal - matrix([1, 0])) < 0.1 and wall_left:
                            continue
                        if linalg.norm(normal - matrix([-1, 0])) < 0.1 and wall_right:
                            continue
                        offset_x, offset_y = col * bw, row * bh
                        sides.append(
                            (((x1 + offset_x, y1 + offset_y), (x2 + offset_x, y2 + offset_y)), normal))
                        #testboxes.append( pygame.Rect(offset_x, offset_y, bw, bh) )
        # print sides[0]
        # print normal_and_normpos(sides[0])
        sides.sort(key=normal_and_normpos)
        #groups = []
        #uniquekeys = []
        # print "position 1"
        # print "position 2"
        # for k, g in groupby(sides, normal_and_normpos):
        #   groups.append(list(g))
        #   uniquekeys.append(list(k))
        # print uniquekeys, "hey"
        fams = []
        for s in sides:
            if not fams or fams[-1][0] != normal_and_normpos(s):
                fams.append([normal_and_normpos(s), [s]])
            else:
                fams[-1][1].append(s)
        # print "position 3"
        #families = zip(uniquekeys, groups)
        # print "position 5"
        families = [(k, combine_sides(g)) for k, g in fams]
        # print [k for k,g in families], "whoa"
        sides2 = []
        for k, g in families:
            sides2.extend(g)

        # print len(sides2), "rofl"
        #zeros = [(k,g) for k,g in families if k[1] == 0]
        # print "position 6"
        #positives = [(k,g) for k,g in families if k[1] > 0]
        # print "position 7"
        #negatives = [(k,g) for k,g in families if (k,g) not in zeros and (k,g) not in positives]
        # if negatives:
        #   print "problem!"

        #sides = [ (s, matrix(s[0][0])*s[1].T, s[1]) for s in sides]
        # print sides[0]
        #sides.sort(key = lambda s: ( (s[2][0,0], s[2][0,1]), s[1][0,0]))
        #sides = [s[0] for s in sides]
        # print sides[0]
        #divided_up = sorted(sides, key = lambda s: tuplefrommatrix(s[1]))
        # print "mkay"
        '''
        Pseudocode time:
        take all the sides and sort them by normal and normpos.
        take them and group them by if the normals are negative and the normpos are negative.
        remove doubled sides.

        for the remaining sides, do the adjacent addition.
        '''

        # sides = combine_sides(sides, verbose) # package the sides. Could be a lot more efficient.
        # print [s for s in sides2 if s not in sides]
        sides = sides2
        # print len(sides), "mao"
        if checknormals:
            # Here I filter the sides by checking if you're travelling inward
            # to the side. (simple dot product stuff
            return [collision.Side(segment, normal) for segment, normal in sides if (matrix(normal) * dxy.T)[0, 0] > 0]
        else:
            return [collision.Side(segment, normal) for segment, normal in sides]

    def give_tiles_better_sides(self):
        if TIME_INITIALIZATION:
            starttime = time.time()
        '''sends all the tiles a list of the sides that overlap with them'''
        counter = 1
        # print "self.sides has", len(self.sides), "elements."
        '''for every side'''
        for i, side in enumerate(self.sides):
            side.number = i
            s = side.side  # A list of points in the form of matrices [[ x, y]]
            my_x, my_y = array(s[0])[0]
            vx, vy = array(s[1] - s[0])[0]
            targets = collision.find_all_tiles(my_x, my_y, vx, vy, 1.0, bw, bh)
            # print "So this side has", len(targets), "targets"
            for x, y in targets:
                if -1 <= x < cols + 1 and -1 <= y < rows + 1:
                    # print "now I will add the term", i, ", to position",
                    # (x,y), "which currently records",
                    # self.side_directory[x][y]
                    self.side_directory[x][y].append(i)
                    counter += 1
        # print "phew, added", counter, "references"
        for c in range(cols):
            for r in range(rows):
                t = self.side_directory[c][r]
                # ;print "position", (c,r), "links to", len(t), "sides,", t
                t[:] = list(set(t))
        endtime = time.time()
        if TIME_INITIALIZATION:
            print "telling each grid locations what sides were near it took", endtime - starttime, "seconds"


def combine_sides(unoptimised_sides, verbose=0):
    no_interior = []
    for s in unoptimised_sides:
        add_side_except_interior(s, no_interior, verbose)

    combined_adjacent = []
    for s in no_interior:
        add_side_combining_adjacent(s, combined_adjacent)
    return combined_adjacent


def add_side_except_interior(new_side, list_of_sides, verbose=0):
    rotate_180 = matrix(((-1, 0), (0, -1)))
    cancelled = 0
    (n_start, n_end), n_normal = new_side
    for old_side in list_of_sides:
        (o_start, o_end), o_normal = old_side

        # n_normal[0] == -o_normal[0] and n_normal[1] == -o_normal[1]:
        if linalg.norm(n_normal + o_normal) == 0:
            # Basically if there are two sides pressed together and of the same
            # size: #print "KILLED DOUBLE SIDES"
            if n_start == o_end and n_end == o_start:
                a = len(list_of_sides)
                if verbose:
                    print a, "is the length of the list of sides before removal"
                list_of_sides[:] = [
                    s for s in list_of_sides if s not in [old_side]]
                if verbose:
                    print len(list_of_sides), "is the length of the list of sides after removal"
                if a - len(list_of_sides) == 2 and verbose:
                    print old_side, new_side, "Somehow cancellation of these two sides removed two sides (instead of one)"
                cancelled = 1
    if not cancelled:
        list_of_sides.append(new_side)
    return list_of_sides


def add_side_combining_adjacent(new_side, list_of_sides):
    combined = 0
    (n_start, n_end), n_normal = new_side
    for old_side in list_of_sides:
        (o_start, o_end), o_normal = old_side
        if linalg.norm(n_normal - o_normal) == 0:
            if n_start == o_end:  # print "COMBINED TWO SIDES"
                modified_side = ((o_start, n_end), n_normal)
                list_of_sides[:] = add_side_combining_adjacent(
                    modified_side, [s for s in list_of_sides if s != old_side])
                combined = 1
            elif n_end == o_start:  # print "COMBINED TWO SIDES"
                modified_side = ((n_start, o_end), n_normal)
                list_of_sides[:] = add_side_combining_adjacent(modified_side, [
                                                               s for s in list_of_sides if s != old_side])  # There's plenty of inefficiency here!
                combined = 1
    if not combined:
        list_of_sides.append(new_side)
    return list_of_sides
