import pygame

import SETTINGS
import consts.raycast


class Slice:

    def __init__(self, location, surface, width, vh):
        self.slice = surface.subsurface(pygame.Rect(location, (1, width))).convert()
        self.rect = self.slice.get_rect(center = (0, SETTINGS.canvas_target_height/2))
        self.distance = None
        self.type = 'slice'
        self.vh = vh
        self.xpos = 0

        if consts.raycast.shade:
            self.shade_slice = pygame.Surface(self.slice.get_size()).convert_alpha()
            sv = consts.raycast.shade_visibility / 10
            self.shade_intensity = [sv*1, sv*2, sv*3, sv*4, sv*5, sv*6, sv*7, sv*8, sv*9, sv*10]

    def update_rect(self, new_slice):
        self.tempslice = new_slice
        self.rect = new_slice.get_rect(center = (self.xpos, int(SETTINGS.canvas_target_height/2)))

        if self.vh == 'v':
            self.darkslice = pygame.Surface(self.tempslice.get_size()).convert_alpha()
            self.darkslice.fill((0, 0, 0, consts.raycast.texture_darken))

        if consts.raycast.shade:
            #Shade intensity table
            intensity = 0
            if self.distance < self.shade_intensity[0]:
                intensity = 0
            elif self.distance < self.shade_intensity[1]:
                intensity = 0.1
            elif self.distance < self.shade_intensity[2]:
                intensity = 0.2
            elif self.distance < self.shade_intensity[3]:
                intensity = 0.3
            elif self.distance < self.shade_intensity[4]:
                intensity = 0.4
            elif self.distance < self.shade_intensity[5]:
                intensity = 0.5
            elif self.distance < self.shade_intensity[6]:
                intensity = 0.6
            elif self.distance < self.shade_intensity[7]:
                intensity = 0.7
            elif self.distance < self.shade_intensity[8]:
                intensity = 0.8
            elif self.distance < self.shade_intensity[9]:
                intensity = 0.9
            else:
                intensity = 1

            self.shade_slice = pygame.Surface(self.tempslice.get_size()).convert_alpha()
            self.shade_slice.fill((consts.raycast.shade_rgba[0] * intensity, consts.raycast.shade_rgba[1] * intensity,
                                   consts.raycast.shade_rgba[2] * intensity, consts.raycast.shade_rgba[3] * intensity))