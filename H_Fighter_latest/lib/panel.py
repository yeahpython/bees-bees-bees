import pygame


class Panel(object):

    '''
    Finally, something that holds onto a screen and paints it if necessary.
    Has a bunch of child objects that each draw from their personal surfaces to the
    main surface! Rectangles for panels are relative to their parent.
    '''

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect((x, y), (width, height))
        self.children = []
        self.visible = True
        self.surface = pygame.Surface((width, height))
        # these should all know if they're visible or active

    def take_event(self, point, event_type):
        for child in self.children:
            if child.rect.collidepoint(point):
                x, y = point
                rel_x = child.rect.x - x
                rel_y = child.rect.y - y
                rel_point = rel_x, rel_y
                child.take_event(rel_point, event_type)

    def update(self):
        # The surface needs to be ready-to-draw after update is called
        if not self.visible:
            pass
        for child in self.children:
            child.draw()

        # maybe sort them by layer

        for child in self.children:
            child.draw_to(self.surface)

        # do actual drawing in the future

    def draw_to(self, target_surface):
        target_surface.blit(self.surface, self.rect.topleft)


class MessagePanel(Panel):

    '''
    Has a message that can be updated.
    '''

    def __init__(self, x, y, width, height, message, typeface="Droid Serif", fontsize=12):
        super(MessagePanel, self).__init__(x, y, width, height, message)
        self.message = message  # message is a list of strings
        pygame.font.init()
        self.font = pygame.font.SysFont(typeface, fontsize)

    def take_event(self, point, event_type):
        super(MessagePanel, self).take_event(point, event_type)

    def update(self):
        super(MessagePanel, self).update()

    def draw_to(self, target_surface):
        super(MessagePanel, self).draw(target_surface)
