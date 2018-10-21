import pygame
import math
import SETTINGS
from typing import Tuple, List


# I noticed, that the sprites are not projected correctly.
# However, I do not have the guts to fix it. Feel free to take a look.

class Sprite:
    def __init__(self, texture: pygame.Surface, ID: int, pos: Tuple[int, int], texture_type: str, parent: str = None):
        """
        Create a sprite
        :param texture: loaded texture
        :param ID: unique identifier
        :param pos: px coords
        :param texture_type: either 'sprite' or 'npc'
        :param parent: either None or 'sprite'
        """
        self.texture = texture
        self.texture = pygame.transform.scale(
            self.texture,
            (SETTINGS.tile_size * 2, SETTINGS.tile_size * 4)
        ).convert_alpha()

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

        # If this sprite belongs to an NPC, make the NPC a parent of this sprite
        # This will help calculating the position of the NPC
        if self.texture_type == 'npc':
            self.parent = parent
        else:
            self.parent = None

        SETTINGS.all_sprites.append(self)

    def get_pos(self):
        """
        Determine position relative to the player.
        :return:
        """
        angle = SETTINGS.player_angle
        fov = SETTINGS.fov

        xpos = self.rect.centerx - SETTINGS.player_rect[0]
        ypos = SETTINGS.player_rect[1] - self.rect.centery

        dist = math.sqrt(xpos * xpos + ypos * ypos)
        if dist == 0:
            dist += 0.0001
        self.distance = dist

        thetaTemp = math.atan2(ypos, xpos)
        thetaTemp = math.degrees(thetaTemp)
        if thetaTemp < 0:
            thetaTemp += 360

        self.theta = thetaTemp

        yTmp = angle + (fov / 2) - thetaTemp
        if thetaTemp > 270 and angle < 90:
            yTmp = angle + (fov / 2) - thetaTemp + 360
        if angle > 270 and thetaTemp < 90:
            yTmp = angle + (fov / 2) - thetaTemp - 360

        xTmp = yTmp * SETTINGS.canvas_actual_width / fov

        sprite_height = int((self.rect.height / dist) * (100 / math.tan(math.radians(fov * 0.8))))
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

        self.new_size = pygame.transform.scale(self.texture, (sprite_width, sprite_height))
        self.new_rect = self.new_size.get_rect()
        self.new_rect.center = (xTmp, SETTINGS.canvas_target_height / 2)
        if self.parent:
            self.parent.hit_rect = self.new_rect

    def draw(self, canvas: pygame.Surface):
        """
        Render the sprite onto the surface
        :param canvas:
        :return:
        """
        canvas.blit(self.new_size, self.new_rect)

    def update_pos(self, pos: List[int]):
        """
        Center the rectangle center position
        :param pos:
        :return:
        """
        self.rect.centerx = pos[0]
        self.rect.centery = pos[1]
