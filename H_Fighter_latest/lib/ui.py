import pygame
import graphics
import clicks
import messages

# Should be able to exit nonhorribly now


def waitForEnter(hidemessage=0):
    if not hidemessage:
        messages.say("Press [enter] to continue", down=1)
    pygame.display.flip()
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)
        if pygame.event.get(pygame.QUIT):
            global time_to_quit
            time_to_quit = True
            break

        clicks.get_more_clicks()
        if clicks.mouseups[0]:
            break
        key_states = pygame.key.get_pressed()
        if key_states[pygame.K_RETURN]:
            break


def waitForKey(key, message=0):
    if message:
        messages.say(message, down=1)
    else:
        print "saying Press " + pygame.key.name(key) + " to exit"
        print "graphics.outline is", graphics.outline
        messages.say("Press " + pygame.key.name(key) + " to exit", down=1)
    pygame.display.flip()
    clock = pygame.time.Clock()
    while not pygame.event.get(pygame.QUIT):
        clock.tick(60)
        key_states = pygame.key.get_pressed()
        if key_states[key]:
            break
        if pygame.event.get(pygame.QUIT):
            global time_to_quit
            time_to_quit = True
            break
        pygame.event.pump()


def getChoiceUnbounded(title, options, allowcancel=False):
    page_size = 30
    curr = 0
    pages = (len(options) - 1) / page_size + 1
    if pages <= 1:
        return getChoiceBounded(title, options, allowcancel)
    else:
        while True:
            view = ["prev", "next"] + options[curr::pages]
            out = getChoiceBounded(
                title + " (Page %s of %s)" % (curr + 1, pages), view, allowcancel)
            if out == "prev":
                curr -= 1
                curr %= pages
            elif out == "next":
                curr += 1
                curr %= pages
            else:
                return out


def getChoiceBounded(title, given_options, allowcancel=False):
    '''Prompts you to choose one of the options. If the user clicks outside the box this returns None.'''

    options = given_options[:]
    if allowcancel:
        options.append("cancel")

    disp = pygame.display.get_surface()
    bg = pygame.Surface((disp.get_width(), disp.get_height()))
    bg.blit(disp, (0, 0))

    clock = pygame.time.Clock()
    currpos = 0
    updateview = 1

    hborder = 15

    optiondisplay = pygame.Surface(
        (min(300, graphics.screen_w - 2 * hborder), min(15 * (len(options) + 3), graphics.screen_h - 2 * hborder)))
    selectionimage = pygame.Surface(
        (optiondisplay.get_width() - 10, 50), flags=pygame.SRCALPHA)

    box = pygame.Rect((0, 0), (selectionimage.get_width(), 15))
    pygame.draw.rect(selectionimage, graphics.outline, box, 1)

    smallsteps = 0
    slowness = 6

    previous_key_states = []
    wet = 0

    oldxy = (-1, -1)

    # lean right
    # dest = optiondisplay.get_rect(right = graphics.screen_w - 15, top = 15)
    dest = optiondisplay.get_rect(
        centerx=graphics.screen_w / 2, centery=graphics.screen_h / 2)

    # list out options
    messages.colorBackground(surface=optiondisplay)
    messages.say(title, surface=optiondisplay, size="small")
    messagecount = 1
    for choice in options:
        messagecount = messages.say(
            choice, down=messagecount, surface=optiondisplay, size="small")

    while True:
        if pygame.event.get(pygame.QUIT):
            print "quit from getChoiceUnbounded"
            global time_to_quit
            time_to_quit = True
            return "quit"
        clicks.get_more_clicks()
        wet += 1

        x, y = pygame.mouse.get_pos()

        if oldxy != (x, y):
            oldxy = x, y
            i = (y - dest.y - 5) / 15 - 2
            if 0 <= i < len(options):
                if dest.left < x < dest.right and i != currpos:
                    currpos = i
                    updateview = 1

        if updateview:
            '''messages.colorBackground(surface = optiondisplay)
            messages.say(title, surface = optiondisplay, size = "small")
            messagecount = 1
            for choice in options:
                    messagecount = messages.say(choice, down = messagecount, surface = optiondisplay, size = "small")'''
            disp = pygame.display.get_surface()

            optionx = hborder
            optiony = graphics.screen_h - 15 * (len(options) + 4)
            optionpos = optionx, optiony

            # make it top right
            # center the options
            #dest = optiondisplay.get_rect(centerx = graphics.screen_w / 2, centery = graphics.screen_h / 2)

            disp.blit(optiondisplay, dest, special_flags=0)

            disp.blit(selectionimage, (dest.x + 5, dest.y + 35 + currpos * 15))

            # pygame.display.flip()
            pygame.display.update(dest)
            updateview = 0

        if clicks.mouseups[0]:
            oldxy = x, y
            i = (y - dest.y - 5) / 15 - 2
            if 0 <= i < len(options) and dest.left < x < dest.right:
                disp.blit(bg, (0, 0))
                return options[currpos]
            elif allowcancel:
                disp.blit(bg, (0, 0))
                return "cancel"

        clock.tick(60)

        '''stupid mac...'''
        #key_presses = pygame.event.get()
        key_states = pygame.key.get_pressed()
        #event = pygame.event.poll()

        # if event.type != pygame.NOEVENT:
        #   print event

        # if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
        if key_states[pygame.K_UP]:
            smallsteps -= 1
            if smallsteps == 0 or (previous_key_states and not previous_key_states[pygame.K_UP]):
                smallsteps = slowness
                currpos -= 1
                currpos %= len(options)
                updateview = 1

        # if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
        elif key_states[pygame.K_DOWN]:
            smallsteps -= 1
            if smallsteps == 0 or (previous_key_states and not previous_key_states[pygame.K_DOWN]):
                smallsteps = slowness
                currpos += 1
                currpos %= len(options)
                updateview = 1

        elif key_states[pygame.K_RETURN] and (previous_key_states and not previous_key_states[pygame.K_RETURN]):
            disp.blit(bg, (0, 0))
            return options[currpos]

        elif key_states[pygame.K_q]:
            disp.blit(bg, (0, 0))
            return

        previous_key_states = key_states[:]
        pygame.event.pump()


def getString(allowed_keys=[], string="", textpos=0, message=""):
    '''returns -1 if window is closed
    and 0 for cancel'''
    disp = pygame.display.get_surface()
    bg = pygame.Surface((disp.get_width(), disp.get_height()))
    bg.blit(disp, (0, 0))
    font = pygame.font.SysFont("Droid Serif", 30)
    box = 0
    if textpos:
        box = textpos
    else:
        box = pygame.Rect(0, 0, 300, 50)
        box.centerx = graphics.screen_w / 2
        box.centery = graphics.screen_h / 2
    s = pygame.display.get_surface()

    prompt = font.render(message, 1, graphics.outline)
    promptpos = prompt.get_rect(centerx=box.centerx, bottom=box.y - 10)

    pygame.draw.rect(s, graphics.foreground, box, 0)
    pygame.draw.rect(s, graphics.outline, box, 1)
    pygame.display.flip()
    clock = pygame.time.Clock()
    previous_key_states = []
    key_downs = []
    redraw = 1

    if not(allowed_keys):
        for key in range(pygame.K_a, pygame.K_z + 1):
            allowed_keys.append(key)
        allowed_keys.append(pygame.K_SPACE)

    allowed_keys += [pygame.K_BACKSPACE, pygame.K_RETURN]
    global time_to_quit
    while True:
        clock.tick(60)

        '''check for quit'''
        if pygame.event.get(pygame.QUIT):
            time_to_quit = True
            return -1
        clicks.get_more_clicks()

        '''check for cancel'''
        if clicks.mouseups[0]:
            x, y = pygame.mouse.get_pos()
            if not box.collidepoint(x, y):
                return string

        key_states = pygame.key.get_pressed()
        if previous_key_states:
            key_downs = [
                new and not old for new, old in zip(key_states, previous_key_states)]
        else:
            key_downs = [0 for x in key_states]

        for key in allowed_keys:
            if key_downs[key]:
                if key == pygame.K_BACKSPACE:
                    string = string[:-1]
                elif key == pygame.K_RETURN:
                    disp.blit(bg, (0, 0))
                    return string
                elif len(string) < 20:
                    if key == pygame.K_SPACE:
                        string += " "
                    else:
                        string += pygame.key.name(key)
                redraw = 1

        if redraw:
            s.blit(prompt, promptpos)

            text = font.render(string, 1, graphics.outline)
            textpos2 = text.get_rect(centerx=box.centerx, centery=box.centery)
            pygame.draw.rect(s, [155, 0, 200], box, 0)
            # box = text.get_rect(centerx = s.get_width()/2, height = 50, centery = s.get_height()/2)
            pygame.draw.rect(s, graphics.outline, box, 1)
            s.blit(text, textpos2)
            pygame.display.flip()
            redraw = 0

        previous_key_states = key_states[:]
        pygame.event.pump()
