import pygame
import math
import SETTINGS
import consts.geom
import consts.player
import consts.raycast
import consts.tile
import gamestate.player
import gamestate.rendering
import gamestate.sprites
from consts.geom import DEGREES_360, DEGREES_270, DEGREES_180, DEGREES_90
 # I noticed, that the sprites are not projected correctly. However, I do not have the guts to fix it. Feel free to take a look.

SPRITE_MAX_HEIGHT = 2500


class Sprite:
    '''== Create a sprite ==\ntexture -> loaded texture | ID -> unique\npos -> px coords          | texture_type -> sprite, npc'''
    def __init__(self, texture, ID, pos, texture_type, parent = None):
        self.texture = texture
        #These constant values should be determined rather than hard coded
        #self.texture = pygame.transform.scale(self.texture, (SETTINGS.TILE_SIZE*2, SETTINGS.TILE_SIZE*4)).convert_alpha()
        self.texture = pygame.transform.scale(self.texture, (
            consts.tile.TILE_SIZE * 4, consts.tile.TILE_SIZE * 8)).convert_alpha()
        self.texture_type = texture_type
        self.type = texture_type
        self.ID = ID

        self.rect = self.texture.get_rect()
        self.rect_size = (self.rect.width, self.rect.height)
        self.rect.centerx = pos[0]
        self.rect.centery = pos[1]

        self.new_rect = None
        self.distance = None

        self.theta = None
        

        #If this sprite belongs to an NPC, make the NPC a parent of this sprite
        #This will help calculating the position of the NPC
        if self.texture_type == 'npc':
            self.parent = parent
        else:
            self.parent = None

        gamestate.sprites.all_sprites.append(self)

    def get_pos(self, canvas):
        angle = consts.player.player_angle
        fov = consts.raycast.fov

        xpos = self.rect.centerx - gamestate.player.player_rect[0]
        ypos = gamestate.player.player_rect[1] - self.rect.centery

        dist = math.sqrt(xpos*xpos + ypos*ypos)
        if dist == 0:
            dist += 0.0001
        self.distance = dist

        thetaTemp = math.atan2(ypos, xpos)
        thetaTemp = math.degrees(thetaTemp)
        
        if thetaTemp < 0:
            thetaTemp += DEGREES_360
            
        self.theta = thetaTemp

        yTmp = angle + (fov/2) - thetaTemp
        
        if thetaTemp > DEGREES_270 and angle < DEGREES_90:
            yTmp = angle + (fov/2) - thetaTemp + DEGREES_360
        if angle > DEGREES_270 and thetaTemp < DEGREES_90:
            yTmp = angle + (fov/2) - thetaTemp - DEGREES_360

        xTmp = yTmp * SETTINGS.canvas_actual_width / fov
                                                    
        sprite_height = int((self.rect.height / dist) * (100 / math.tan(math.radians(fov * 0.8))))
        
        if sprite_height > SPRITE_MAX_HEIGHT:
            sprite_height = SPRITE_MAX_HEIGHT

        sprite_width = int(self.rect.width / self.rect.height * sprite_height)
        
        if xTmp > (0 - sprite_width) and xTmp < (SETTINGS.canvas_actual_width + sprite_width):
            gamestate.rendering.zbuffer.append(self)
            
            if self.parent:
                self.parent.in_canvas = True
        else:
            if self.parent:
                self.parent.in_canvas = False

        # todo does this help?
        sprite_height = int(sprite_height * SETTINGS.canvas_aspect_ratio) 

        self.new_size = pygame.transform.scale(self.texture, (sprite_width, sprite_height))
        self.new_rect = self.new_size.get_rect()
        # I think my changes to HUD screwed this up
        #self.new_rect.center = (xTmp, SETTINGS.canvas_target_height/2)
        # TODO Fix this
        self.new_rect.center = (xTmp, (SETTINGS.canvas_target_height/2) )
        
        if self.parent:
            self.parent.hit_rect = self.new_rect

    def draw(self, canvas):
        canvas.blit(self.new_size, self.new_rect)

    def update_pos(self, pos):
        self.rect.centerx = pos[0]
        self.rect.centery = pos[1]
            









        

        
