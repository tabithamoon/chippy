import pygame

color_wht = pygame.Color(255, 255, 255, 255)
color_blk = pygame.Color(0, 0, 0, 255)

def initialize():
    pygame.init()
    screen = pygame.display.set_mode((640,320))
    return screen

def flip(screen):
    pygame.display.flip()
    screen.fill(color_blk)

def draw_pixel(screen, x, y):
    pixel = pygame.Rect(x * 10, y * 10, 10, 10)
    pygame.draw.rect(screen, color_wht, pixel)

def cls(screen):
    screen.fill(color_blk)