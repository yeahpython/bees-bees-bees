import pygame
import graphics
from game_settings import settings, want_bools, want_ints, min_val, max_val, problem_with_setting, save_settings
from ui import getString
import messages


class Panel(object):

    '''
    Finally, something that holds onto a screen and paints it if necessary.
    Has a bunch of child objects that each draw from their personal surfaces to the
    main surface! Rectangles for panels are relative to their parent.

    We should never be calling update() from the outside.
    '''

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect((x, y), (width, height))
        self.children = []
        self.visible = True
        self.surface = pygame.Surface((width, height))
        self.children = []
        self.needs_update = False
        # needs_update means that all children need to be
        # updated and blitted onto my surface.

    # point is in my frame of reference.
    # returns true anything receives it.
    def handle_event(self, point, event_type):
        for child in self.children:
            if child.visible and child.rect.collidepoint(point):
                x, y = point
                rel_x = x - child.rect.x
                rel_y = y - child.rect.y
                rel_point = rel_x, rel_y
                return child.handle_event(rel_point, event_type)
        return False

    def update_children(self):
        # ensures that all children have up-to-date surfaces.
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
        if modified:
            self.surface.fill((0, 0, 0))
            for child in self.children:
                child.draw_to(self.surface)
        return modified

    def draw_to(self, target_surface):
        self.update()
        target_surface.blit(self.surface, self.rect.topleft)


class StackingPanel(Panel):

    def __init__(self, x, y, width, height):
        super(StackingPanel, self).__init__(x, y, width, height)
        self.surface.set_colorkey((0, 0, 0))

    def update(self):
        modified = super(StackingPanel, self).update_children()
        modified = modified or self.needs_update
        if modified:
            left = 0
            top = 0
            h = 0
            for child in self.children:
                child.rect.topleft = left, top
                left += child.rect.width + 5
                if child.rect.h > h:
                    h = child.rect.h
            newsize = (left, h)
            if self.surface.get_size() != newsize:
                self.surface = pygame.Surface(newsize)
                self.surface.set_colorkey((0, 0, 0))
                self.rect.size = self.surface.get_size()
                self.rect.top = graphics.screen_h - self.rect.h
                self.rect.left = 0
            for child in self.children:
                child.draw_to(self.surface)

        self.needs_update = False
        return modified

    def draw_to(self,  target_surface):
        self.update()
        target_surface.blit(self.surface, self.rect.topleft, )


class ShrinkingPanel(Panel):

    def update(self):
        modified = super(ShrinkingPanel, self).update()

        if modified:
            self.shrink()
            self.surface.fill((50, 50, 50))
            for child in self.children:
                child.draw_to(self.surface)
            print "refreshed shrinking panel."
        return modified

    def shrink(self):
        if self.children:
            mega_rect = self.children[0].rect.unionall(
                [c.rect for c in self.children])
            x, y, w, h = mega_rect.x, mega_rect.y, mega_rect.w, mega_rect.h

            # making the rectangle a little larger
            x -= 5
            y -= 5
            w += 10
            h += 10

            self.rect.x += x
            self.rect.y += y
            self.rect.w = w
            self.rect.h = h
            if self.surface.get_size() != (w, h):
                self.surface = pygame.Surface((w, h))

            for c in self.children:
                c.rect.x -= x
                c.rect.y -= y

            self.needs_update = True
        else:
            print "error, no children"


class SettingButton(Panel):

    '''
    Controls a setting.
    '''

    def __init__(self, x, y, width, height, setting,
                 typeface="Droid Serif", fontsize=20):
        super(SettingButton, self).__init__(x, y, width, height)
        self.setting = setting
        pygame.font.init()
        self.font = pygame.font.SysFont(typeface, fontsize)
        self.color = (0, 255, 0)
        self.needs_update = True
        self.message = "not initialized"

    def handle_event(self, point, event_type):
        event_taken = super(SettingButton, self).handle_event(
            point, event_type)
        if not event_taken:
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
            event_taken = True
        return event_taken

    def update(self):
        modified = super(SettingButton, self).update()
        if self.needs_update:
            self.message = self.setting + ": " + str(settings[self.setting])
            self.surface = self.font.render(self.message, 1, self.color)
            print "refreshed setting button", self.setting
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

    def __init__(self, x, y, width, height, message, typeface="Droid Serif", fontsize=20):
        super(MessagePanel, self).__init__(x, y, width, height)
        self.message = message  # message is a list of strings
        pygame.font.init()
        self.font = pygame.font.SysFont(typeface, fontsize)
        self.color = (255, 255, 255)
        self.needs_update = True

    def handle_event(self, point, event_type):
        event_taken = super(MessagePanel, self).handle_event(
            point, event_type)
        if not event_taken:
            self.color = (self.color[1], self.color[2], self.color[0])
            self.needs_update = True
            event_taken = True
        return event_taken

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
