import SETTINGS
import consts.colours
import pygame

import consts.raycast


class GameCanvas:
    '''== Create game canvas ==\nwidth -> px\nheight -> px'''
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.res_width = 0
        if SETTINGS.mode == 1:
            #self.width = int(SETTINGS.canvas_target_width / SETTINGS.resolution) * SETTINGS.resolution
            #self.height = SETTINGS.canvas_target_height
            self.width = SETTINGS.canvas_target_width
            self.height = SETTINGS.canvas_target_height
            self.res_width = SETTINGS.canvas_actual_width

        if SETTINGS.fullscreen:
            self.window = pygame.display.set_mode((self.width, self.height) ,pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode((self.width, self.height))
        self.canvas = pygame.Surface((self.width, self.height))

        pygame.display.set_caption("DUGA")

        self.shade = [pygame.Surface((self.width, self.height)).convert_alpha(),
                      pygame.Surface((self.width, self.height/1.2)).convert_alpha(),
                      pygame.Surface((self.width, self.height/2)).convert_alpha(),
                      pygame.Surface((self.width, self.height/4)).convert_alpha(),
                      pygame.Surface((self.width, self.height/8)).convert_alpha(),
                      pygame.Surface((self.width, self.height/18)).convert_alpha()]
        self.rgba = [consts.raycast.shade_rgba[0], consts.raycast.shade_rgba[1], consts.raycast.shade_rgba[2], int(min(255, consts.raycast.shade_rgba[3] * (50 / consts.raycast.shade_visibility)))]

    def change_mode(self):
        if SETTINGS.mode == 1: #1 - 3D / 0 - 2D
            SETTINGS.mode = 0
            self.__init__(SETTINGS.canvas_actual_width, SETTINGS.canvas_target_height)
        else:
            SETTINGS.mode = 1
            self.__init__(self.res_width, SETTINGS.canvas_target_height)
        SETTINGS.switch_mode = False

    def draw(self):
        if SETTINGS.mode == 1:
            self.canvas.fill(SETTINGS.levels_list[SETTINGS.current_level].sky_color)
            self.window.fill(consts.colours.BLACK)
            pygame.draw.rect(self.canvas, SETTINGS.levels_list[SETTINGS.current_level].ground_color, (0, self.height/2, self.width, self.height/2))

            if consts.raycast.shade:
                for i in range(len(self.shade)):
                    if i != 5:
                        self.shade[i].fill((self.rgba[0], self.rgba[1], self.rgba[2], self.rgba[3]))
                    else:
                        self.shade[i].fill((self.rgba[0], self.rgba[1], self.rgba[2], consts.raycast.shade_rgba[3]))
                    self.canvas.blit(self.shade[i], (0, self.height/2 - self.shade[i].get_height()/2))

        else:
            self.window.fill(consts.colours.WHITE)