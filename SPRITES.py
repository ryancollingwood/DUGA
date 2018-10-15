import pygame
import math
import SETTINGS
from GEOM import straight_line_distance, tan_radians

 # I noticed, that the sprites are not projected correctly. However, I do not have the guts to fix it. Feel free to take a look.

class Sprite:
    '''== Create a sprite ==\ntexture -> loaded texture | ID -> unique\npos -> px coords          | texture_type -> sprite, npc'''
    def __init__(self, texture, ID, pos, texture_type, parent = None):
        self.texture = texture
        self.texture = pygame.transform.scale(self.texture, (SETTINGS.tile_size*2, SETTINGS.tile_size*4)).convert_alpha()
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

        self.current_frame = 0
        self.last_frame = 0
        self.drawn_width = None
        self.drawn_height = None


        #If this sprite belongs to an NPC, make the NPC a parent of this sprite
        #This will help calculating the position of the NPC
        if self.texture_type == 'npc':
            self.parent = parent
        else:
            self.parent = None

        SETTINGS.all_sprites.append(self)

    def __str__(self):
        return str(vars(self))

    def get_pos(self, canvas):
        angle = SETTINGS.player_angle
        fov = SETTINGS.fov

        xpos = self.rect.centerx - SETTINGS.player_rect[0]
        ypos = SETTINGS.player_rect[1] - self.rect.centery

        dist = math.sqrt(xpos*xpos + ypos*ypos)
        if dist == 0:
            dist += 0.0001
        self.distance = dist

        thetaTemp = math.atan2(ypos, xpos)
        thetaTemp = math.degrees(thetaTemp)
        if thetaTemp < 0:
            thetaTemp += 360
            
        self.theta = thetaTemp

        yTmp = angle + (fov/2) - thetaTemp
        if thetaTemp > 270 and angle < 90:
            yTmp = angle + (fov/2) - thetaTemp + 360
        if angle > 270 and thetaTemp < 90:
            yTmp = angle + (fov/2) - thetaTemp - 360

        xTmp = yTmp * SETTINGS.canvas_actual_width / fov
                                                    
        sprite_height = int((self.rect.height / dist) * (100 / tan_radians(fov * 0.8)))
        if sprite_height > 2500:
            sprite_height = 2500

        sprite_width = int(self.rect.width / self.rect.height * sprite_height)
        
        if xTmp > (0 - sprite_width) and xTmp < (SETTINGS.canvas_actual_width + sprite_width):
            SETTINGS.zbuffer.append(self)
            
            if self.parent:
                self.parent.in_canvas = True
        else:
            if self.parent:
                self.parent.in_canvas = False

        # todo does this help?
        sprite_height = int(sprite_height * SETTINGS.canvas_aspect_ratio) 

        if (self.drawn_height != sprite_height and self.drawn_width != sprite_width) or (self.current_frame != self.last_frame):
            self.drawn_height = sprite_height
            self.drawn_width = sprite_width

            self.new_size = pygame.transform.scale(self.texture, (sprite_width, sprite_height))
            self.new_rect = self.new_size.get_rect()

        if SETTINGS.original_aspect:
            self.new_rect.center = (xTmp, SETTINGS.canvas_target_height/2)
        else:
            self.new_rect.center = (xTmp, SETTINGS.canvas_target_height/2)

        if self.parent:
            self.parent.hit_rect = self.new_rect

    def draw(self, canvas):
        canvas.blit(self.new_size, self.new_rect)

    def update_pos(self, pos):
        self.rect.centerx = pos[0]
        self.rect.centery = pos[1]
            









        

        
