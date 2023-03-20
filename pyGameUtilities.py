import pygame
if not pygame.get_init():
    pygame.init()

BASICFONT=pygame.font.Font("freesansbold.ttf",20)
SMALLFONT=pygame.font.Font("freesansbold.ttf",10)

def makeText(text, color, bgcolor, left, top, font=None):
    '''
    Creates the pygame Surface and Rect objects for text rendering.
    @param text: a string object representing the text.
    @param color: a RGB tuple of length 3 for the font color.
    @param bgcolor: a RGB tuple of length 3 for the background color of the surface.
    @param left: an integer to specify the x-coodinate of the top-left corner of the surface.
    @param top: an integer to specify the y-coodinate of the top-left corner of the surface.
    @param font (optional): a pygame font object to render the text.
    @returns (pygame surface, pygame rect)
    '''
    if not pygame.get_init(): pygame.init()
    if font: textSurf = font.render(text, True, color, bgcolor)
    else: textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (left, top)
    return (textSurf, textRect)