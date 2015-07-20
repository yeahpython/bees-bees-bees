import pygame
from numpy import matrix, nditer
import graphics
from game_settings import settings, want_bools, want_ints, min_val, max_val, problem_with_setting, save_settings, DEBUG_PANEL
from ui import getString
import messages


class Panel(object):

    '''
    Finally, something that holds onto a screen and paints it if necessary.
    Has a bunch of child objects that each draw from their personal surfaces to the
    main surface! Rectangles for panels are relative to their parent.

    We should never be calling update() from the outside.
    '''

    def __init__(self, x, y, width, height, visible=True):
        self.rect = pygame.Rect((x, y), (width, height))
        self.children = []
        self.visible = visible
        self.surface = pygame.Surface((width, height))
        self.children = []
        self.needs_update = False
        # needs_update means that all children need to be
        # blitted onto my surface.
        self.onclick = []

    # point is in my frame of reference.
    # returns true anything receives it.
    def handle_event(self, point, event_type):
        # child responses cover my responses.
        for child in self.children:
            if child.visible and child.rect.collidepoint(point):
                x, y = point
                rel_x = x - child.rect.x
                rel_y = y - child.rect.y
                rel_point = rel_x, rel_y
                return child.handle_event(rel_point, event_type)
        if self.onclick:
            for function in self.onclick:
                function()
            return True
        return False

    def update_children(self):
        # ensures that all children have up-to-date surfaces.
        # Returns true if any children are modify their surfaces
        # as a result.
        modified = False
        if self.visible:
            for child in self.children:
                if child.update():
                    modified = True
        return modified

    def update(self):
        # The surface needs to be ready-to-draw after update is called
        # Returns true if surface has been modified.
        modified = self.update_children()
        self_changed = False
        if modified or self_changed:
            self.surface.fill(graphics.random_color())
            for child in self.children:
                child.draw_to(self.surface)
        return modified

    def random_outline(self):
        pygame.draw.rect(
            self.surface, graphics.random_color(), self.surface.get_rect(), 2)

    def draw_to(self, target_surface):
        if not self.visible:
            return
        self.update()
        if settings[DEBUG_PANEL]:
            self.random_outline()
        target_surface.blit(self.surface, self.rect.topleft)


class StackingPanel(Panel):

    def __init__(self, x=0, y=0, width=100, height=100, mode=1):
        super(StackingPanel, self).__init__(x, y, width, height)
        self.surface.set_colorkey((0, 0, 0))
        self.mode = mode

    def update(self):
        children_modified = super(StackingPanel, self).update_children()
        modified = children_modified or self.needs_update
        if modified:
            if self.mode == 0:
                left = 0
                top = 0
                h = 0
                for child in self.children:
                    child.rect.topleft = left, top
                    left += child.rect.width + 5
                    if child.rect.h > h:
                        h = child.rect.h
                newsize = (left, h)
            else:
                left = 5
                top = 5
                nextleft = left
                new_height = 0
                new_width = 0
                for child in self.children:
                    child.rect.topleft = left, top
                    top += child.rect.h
                    top += 5
                    if top > graphics.screen_h:
                        left = nextleft
                        top = 5
                        child.rect.topleft = left, top
                        top += child.rect.h
                        top += 5
                    nextleft = max(child.rect.w + left + 5, nextleft)
                    new_width = max(new_width, child.rect.right + 5)
                    new_height = max(new_height, child.rect.bottom + 5)
                newsize = new_width, new_height

            # Align bottomleft
            if self.surface.get_size() != newsize:
                self.surface = pygame.Surface(newsize)
                self.surface.set_colorkey((0, 0, 0))
                self.rect.size = self.surface.get_size()
                self.rect.topleft = 0, 0
            else:
                self.surface.fill((0, 0, 0))
            for child in self.children:
                child.draw_to(self.surface)

        self.needs_update = False
        return modified


class ShrinkingPanel(Panel):

    def __init__(self, x=0, y=0, width=100, height=100, min_width=None):
        super(ShrinkingPanel, self).__init__(x, y, width, height)
        self.min_width = min_width

    def update(self):
        modified = super(ShrinkingPanel, self).update() or self.needs_update
        if modified:
            self.shrink()
            self.surface.fill((50, 50, 50))
            for child in self.children:
                child.draw_to(self.surface)
        self.needs_update = False
        return modified

    def shrink(self):
        # Shinks around visible children.
        visible_children = [child for child in self.children if child.visible]
        if visible_children:
            mega_rect = visible_children[0].rect.unionall(
                [c.rect for c in visible_children])
            x, y, w, h = mega_rect.x, mega_rect.y, mega_rect.w, mega_rect.h

            # making the rectangle a little larger
            x -= 5
            y -= 5
            w += 10
            h += 10

            if self.min_width is not None:
                w = max(w, self.min_width)

            self.rect.x += x
            self.rect.y += y
            self.rect.w = w
            self.rect.h = h

            if self.surface.get_size() != (w, h):
                self.surface = pygame.Surface((w, h))

            for c in visible_children:
                c.rect.x -= x
                c.rect.y -= y

            self.needs_update = True
        else:
            print "error, no children"

    def draw_to(self, target_surface):
        super(ShrinkingPanel, self).draw_to(target_surface)


class StatisticsPanel(Panel):

    def __init__(self, gameobjects, x=0, y=0, width=250, height=250):
        super(StatisticsPanel, self).__init__(x, y, width, height)

        def update_func():
            self.surface.fill((10, 10, 10))
            histogram = [0] * 25
            for i, bee in enumerate(gameobjects["room"].bees):
                for unit in bee.brain.computation_units:
                    for name, m in unit.matrices.iteritems():
                        for x in nditer(m):
                            bucket = int(x * 12 + 12)
                            if bucket < 0:
                                bucket = 0
                            if bucket > 24:
                                bucket = 24
                            histogram[bucket] += 1

            m = max(histogram)
            m = max(m, 1.0)
            for i, val in enumerate(histogram):
                h = int(val * 250 / m)
                rect = pygame.Rect(
                    i * 10, 250 - h, 9, h).clip(pygame.Rect(0, 0, 250, 250))
                pygame.draw.rect(
                    self.surface, (255, 255, 255), rect)
            '''
            self.surface.fill((10, 10, 10))
            for i, bee in enumerate(gameobjects["room"].bees):
                outputs = matrix([0.0, 0.0])
                bee.brain.get_outputs(outputs)
                i1 = int(1 + outputs[0, 0] * 254)
                i2 = int(1 + outputs[0, 1] * 254)  # black is transparent
                try:
                    h = 10
                    pygame.draw.rect(
                        self.surface, (i1, i1, i1), pygame.Rect(0, i * h, 125, h))
                    pygame.draw.rect(
                        self.surface, (i2, i2, i2), pygame.Rect(125, i * h, 125, h))
                except Exception:
                    print "failed to draw"
            '''
            self.needs_update = True

        update_func()

        self.onclick.append(update_func)

    def update(self):
        if self.needs_update:
            self.needs_update = False
            return True
        return False


class SettingButton(Panel):

    '''
    Controls a setting.
    '''

    def __init__(self, setting, x=0, y=0, width=100, height=100,
                 typeface="DejaVu Sans", fontsize=20, bold=False, italic=False, visible=True):
        super(SettingButton, self).__init__(
            x, y, width, height, visible=visible)
        self.setting = setting
        pygame.font.init()
        self.font = pygame.font.SysFont(
            typeface, 12, bold, italic)
        self.color = (255, 255, 255)
        self.needs_update = True
        self.message = "not initialized"

        def clickhandler():
            self.modify_setting()
        self.onclick.append(clickhandler)

    def modify_setting(self):
        if self.setting in want_bools:
            settings[self.setting] = not settings[self.setting]
        elif self.setting in want_ints and self.setting in max_val and self.setting in min_val:
            settings[self.setting] += 1
            if settings[self.setting] > max_val[self.setting]:
                settings[self.setting] = min_val[self.setting]
        else:
            messages.colorBackground()
            # messages.say("Pick a new value", down = 4)

            allowed_keys = range(
                pygame.K_0, pygame.K_9 + 1)
            allowed_keys += [pygame.K_PERIOD]
            allowed_keys += [pygame.K_e]
            allowed_keys += [pygame.K_MINUS]

            '''loop is for error checking'''
            while True:
                # message = messages.smallfont.render("Set new value for '%s'" % toChange, 1, [255, 255, 255])
                # pygame.display.get_surface().blit(message, (600, 15 * (usedindex + 3)))
                m = "Set new value for '%s'" % self.setting
                position = pygame.Rect(0, 0, 290, 30)
                # position.x = 600 #Leaning right
                position.centerx = graphics.screen_w / 2
                # position.y = 15 * (usedindex + 4.3)
                # Leaning up
                position.centery = graphics.screen_h / 2
                out = getString(
                    allowed_keys, str(settings[self.setting]), textpos=position, message=m)
                # out = getString(allowed_keys, str(settings[toChange]))

                # quit
                if out == -1:
                    break

                # cancel
                elif out == 0:
                    break

                try:
                    val = 0
                    if "." in out:
                        val = float(out)
                    else:
                        val = int(out)

                    problems = problem_with_setting(
                        self.setting, val)
                    if problems:
                        messages.colorBackground()
                        messages.say(problems, down=4)
                        continue

                    settings[self.setting] = val
                    break

                except:
                    messages.colorBackground()
                    messages.say(
                        "Error. Pick a new value", down=4)

            save_settings()
        self.needs_update = True

    def update(self):
        modified = super(SettingButton, self).update()
        if self.needs_update:
            self.message = self.setting + ": " + str(settings[self.setting])
            self.surface = self.font.render(self.message, 1, self.color)
            self.rect.size = self.surface.get_size()
            modified = True
            self.needs_update = False
        return modified

    def draw_to(self, target_surface):
        super(SettingButton, self).draw_to(target_surface)


class MessagePanel(Panel):

    '''
    Has a message that can be updated.
    '''

    def __init__(self, message, x=0, y=0, width=100, height=100, typeface="Droid Serif", fontsize=20):
        super(MessagePanel, self).__init__(x, y, width, height)
        self.message = message  # message is a list of strings
        pygame.font.init()
        self.font = pygame.font.SysFont(typeface, fontsize)
        self.color = (255, 255, 255)
        self.needs_update = True

        # def cycle_colors():
        #     self.color = (self.color[1], self.color[2], self.color[0])
        #     self.needs_update = True
        # self.onclick.append(cycle_colors)

    def update(self):
        modified = super(MessagePanel, self).update()
        if self.needs_update:
            self.surface = self.font.render(self.message, 1, self.color)
            self.rect.size = self.surface.get_size()
            modified = True
            self.needs_update = False
        return modified

    def draw_to(self, target_surface):
        super(MessagePanel, self).draw_to(target_surface)
