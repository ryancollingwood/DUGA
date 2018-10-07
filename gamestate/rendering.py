import pygame

zbuffer = []
blitted = []
last_blitted = []
middle_slice_len = None
middle_slice = None
middle_ray_pos = None
raylines = []

def add_blit(rect):
    global blitted
    blitted.append(rect)

def update_display():
    global blitted
    global last_blitted

    if blitted != last_blitted:
        pygame.display.update(blitted)
        last_blitted = blitted
        blitted = []