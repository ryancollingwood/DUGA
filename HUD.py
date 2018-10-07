import SETTINGS
import TEXT
import pygame
import os
import math

import consts.colours
import gamestate.inventory
import gamestate.player
from gamestate.rendering import add_blit


class hud:

    def __init__(self):
        self.health = gamestate.player.player_health
        self.armor = gamestate.player.player_armor
        self.ammo = 0
        self.scale_width = 0
        self.scale_height = 0

        self.sprite = pygame.image.load(os.path.join('graphics', 'hud.png')).convert()
        self.rect = self.sprite.get_rect()
        # get the unscaled dimensions for figuring out the scale of the transform once done
        self.scale_width = self.rect.width
        self.scale_height = self.rect.height    
        self.sprite = pygame.transform.scale(self.sprite, (SETTINGS.canvas_target_width, int(self.rect.height * SETTINGS.canvas_aspect_ratio)))
        self.rect = self.sprite.get_rect()
        
        self.scale_width = self.rect.width / self.scale_width
        self.scale_height = self.rect.height / self.scale_height
        # use relative postioning to set the actual playable area
        SETTINGS.canvas_game_area_height = SETTINGS.canvas_target_height - self.rect.height
        self.rect.topleft = (0, SETTINGS.canvas_game_area_height)

        self.text = [TEXT.Text(int(self.rect.width/35), self.rect.y + int(self.rect.height/2.5), 'PLAYER ARMOR',
                               consts.colours.DARKGRAY, 'DUGAFONT.ttf', 35),
                     TEXT.Text(int(self.rect.width/3.4), self.rect.y + int(self.rect.height/2.5), 'PLAYER HEALTH',
                               consts.colours.DARKGRAY, 'DUGAFONT.ttf', 35),
                     TEXT.Text(int(self.rect.width/1.8), self.rect.y + int(self.rect.height/2.5), 'AMMUNITION',
                               consts.colours.DARKGRAY, 'DUGAFONT.ttf', 35)]

        self.arrow_spritesheet = pygame.image.load(os.path.join('graphics', 'arrows.png')).convert_alpha()


        self.arrow = self.arrow_spritesheet.subsurface(0,0,17,17)
        self.arrow = pygame.transform.scale(self.arrow, (50,50))
        self.original_arrow = self.arrow
        self.arrow_rect = self.arrow.get_rect()
        self.arrow_rect.center = (self.rect.topright[0] - math.ceil(46 * self.scale_width), self.rect.topright[1] + math.ceil(66 * self.scale_height))
        self.arrow_center = (self.arrow_rect.centerx - self.arrow_rect.width / 2,
                             self.arrow_rect.centery - self.arrow_rect.height / 2)

        self.arrow2 = self.arrow_spritesheet.subsurface(0,17,17,17)
        self.arrow2 = pygame.transform.scale(self.arrow2, (50,50))
        self.original_arrow2 = self.arrow2
        self.arrow3 = self.arrow_spritesheet.subsurface(0,34,17,17)
        self.arrow3 = pygame.transform.scale(self.arrow3, (50,50))
        self.original_arrow3 = self.arrow3

    def render(self, canvas):
        
        add_blit(canvas.blit(self.sprite, self.rect))
        self.text[0].update_string('%s / 100' % gamestate.player.player_armor)
        self.text[1].update_string('%s / 100' % gamestate.player.player_health)
        if gamestate.inventory.current_gun and gamestate.inventory.current_gun.ammo_type:
            self.text[2].update_string('%s / %s' % (gamestate.inventory.current_gun.current_mag, gamestate.inventory.held_ammo[
                gamestate.inventory.current_gun.ammo_type]))
        else:
            self.text[2].update_string('-- / --')
        for string in self.text:
            string.draw(canvas)

  
        self.arrow = pygame.transform.rotate(self.original_arrow, SETTINGS.end_angle)
        self.arrow_rect.topleft = (self.arrow_center[0] - self.arrow.get_rect().width /2,
                                   self.arrow_center[1] - self.arrow.get_rect().height /2)
        add_blit(canvas.blit(self.arrow, self.arrow_rect))

        #test
        self.arrow2 = pygame.transform.rotate(self.original_arrow2, SETTINGS.end_angle)
        self.arrow3 = pygame.transform.rotate(self.original_arrow3, SETTINGS.end_angle)

        add_blit(canvas.blit(self.arrow2, (self.arrow_rect[0], self.arrow_rect[1] - 4)))
        add_blit(canvas.blit(self.arrow3, (self.arrow_rect[0], self.arrow_rect[1] - 8)))

