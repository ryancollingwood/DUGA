from typing import Tuple
import pygame

from NPC import NpcSideName
from NPC import NpcAnimation
from NPC import NpcSide

SpriteSheet = Tuple[pygame.Surface, ...]

class DirectionalSprite:

    def __init__(self, texture_path):

        self.sides = tuple((
            NpcSide(NpcSideName.FRONT, 337.5, 22.5, True, 0),
            NpcSide(NpcSideName.FRONT_LEFT, 22.5, 67.5, True, 7),
            NpcSide(NpcSideName.LEFT, 67.5, 112.5, False, 6),
            NpcSide(NpcSideName.BACK_LEFT, 112.5, 157.5, False, 5),
            NpcSide(NpcSideName.BACK, 157.5, 202.5, False, 4),
            NpcSide(NpcSideName.BACK_RIGHT, 202.5, 247.5, False, 3),
            NpcSide(NpcSideName.RIGHT, 247.5, 292.5, False, 2),
            NpcSide(NpcSideName.FRONT_RIGHT, 292.5, 337.5, True, 1),
        ))

        self.texture_path = texture_path # Used for creating new NPCS
        self.texture = pygame.image.load(texture_path).convert_alpha()

        self.stand_texture = tuple((
            self.texture.subsurface(0, 0, 64, 128).convert_alpha(),
            self.texture.subsurface(64, 0, 64, 128).convert_alpha(),
            self.texture.subsurface(128, 0, 64, 128).convert_alpha(),
            self.texture.subsurface(192, 0, 64, 128).convert_alpha(),
            self.texture.subsurface(256, 0, 64, 128).convert_alpha(),
            self.texture.subsurface(320, 0, 64, 128).convert_alpha(),
            self.texture.subsurface(384, 0, 64, 128).convert_alpha(),
            self.texture.subsurface(448, 0, 64, 128).convert_alpha(),
        ))

        self.front_texture = tuple((
            self.texture.subsurface(0, 128, 64, 128).convert_alpha(),
            self.texture.subsurface(64, 128, 64, 128).convert_alpha(),
            self.texture.subsurface(128, 128, 64, 128).convert_alpha(),
            self.texture.subsurface(192, 128, 64, 128).convert_alpha(),
            self.texture.subsurface(256, 128, 64, 128).convert_alpha(),
            self.texture.subsurface(320, 128, 64, 128).convert_alpha(),
            self.texture.subsurface(384, 128, 64, 128).convert_alpha(),
            self.texture.subsurface(448, 128, 64, 128).convert_alpha(),
            self.texture.subsurface(512, 128, 64, 128).convert_alpha(),
            self.texture.subsurface(576, 128, 64, 128).convert_alpha(),
        ))

        self.frontright_texture = tuple((
            self.texture.subsurface(0, 256, 64, 128).convert_alpha(),
            self.texture.subsurface(64, 256, 64, 128).convert_alpha(),
            self.texture.subsurface(128, 256, 64, 128).convert_alpha(),
            self.texture.subsurface(192, 256, 64, 128).convert_alpha(),
            self.texture.subsurface(256, 256, 64, 128).convert_alpha(),
            self.texture.subsurface(320, 256, 64, 128).convert_alpha(),
            self.texture.subsurface(384, 256, 64, 128).convert_alpha(),
            self.texture.subsurface(448, 256, 64, 128).convert_alpha(),
            self.texture.subsurface(512, 256, 64, 128).convert_alpha(),
            self.texture.subsurface(576, 256, 64, 128).convert_alpha()
        ))

        self.right_texture = tuple((
            self.texture.subsurface(0, 384, 64, 128).convert_alpha(),
            self.texture.subsurface(64, 384, 64, 128).convert_alpha(),
            self.texture.subsurface(128, 384, 64, 128).convert_alpha(),
            self.texture.subsurface(192, 384, 64, 128).convert_alpha(),
            self.texture.subsurface(256, 384, 64, 128).convert_alpha(),
            self.texture.subsurface(320, 384, 64, 128).convert_alpha(),
            self.texture.subsurface(384, 384, 64, 128).convert_alpha(),
            self.texture.subsurface(448, 384, 64, 128).convert_alpha(),
            self.texture.subsurface(512, 384, 64, 128).convert_alpha(),
            self.texture.subsurface(576, 384, 64, 128).convert_alpha()
        ))

        self.backright_texture = tuple((
            self.texture.subsurface(0, 512, 64, 128).convert_alpha(),
            self.texture.subsurface(64, 512, 64, 128).convert_alpha(),
            self.texture.subsurface(128, 512, 64, 128).convert_alpha(),
            self.texture.subsurface(192, 512, 64, 128).convert_alpha(),
            self.texture.subsurface(256, 512, 64, 128).convert_alpha(),
            self.texture.subsurface(320, 512, 64, 128).convert_alpha(),
            self.texture.subsurface(384, 512, 64, 128).convert_alpha(),
            self.texture.subsurface(448, 512, 64, 128).convert_alpha(),
            self.texture.subsurface(512, 512, 64, 128).convert_alpha(),
            self.texture.subsurface(576, 512, 64, 128).convert_alpha(),
        ))

        self.back_texture = tuple((
            self.texture.subsurface(0, 640, 64, 128).convert_alpha(),
            self.texture.subsurface(64, 640, 64, 128).convert_alpha(),
            self.texture.subsurface(128, 640, 64, 128).convert_alpha(),
            self.texture.subsurface(192, 640, 64, 128).convert_alpha(),
            self.texture.subsurface(256, 640, 64, 128).convert_alpha(),
            self.texture.subsurface(320, 640, 64, 128).convert_alpha(),
            self.texture.subsurface(384, 640, 64, 128).convert_alpha(),
            self.texture.subsurface(448, 640, 64, 128).convert_alpha(),
            self.texture.subsurface(512, 640, 64, 128).convert_alpha(),
            self.texture.subsurface(576, 640, 64, 128).convert_alpha(),
        ))

        self.backleft_texture = tuple((
            pygame.transform.flip(frame, True, False) for frame in self.backright_texture
        ))
        self.left_texture = tuple((
            pygame.transform.flip(frame, True, False) for frame in self.right_texture
        ))
        self.frontleft_texture = tuple((
            pygame.transform.flip(frame, True, False) for frame in self.frontright_texture
        ))

        self.die_texture = tuple((
            self.texture.subsurface(0, 768, 64, 128).convert_alpha(),
            self.texture.subsurface(64, 768, 64, 128).convert_alpha(),
            self.texture.subsurface(128, 768, 64, 128).convert_alpha(),
            self.texture.subsurface(192, 768, 64, 128).convert_alpha(),
            self.texture.subsurface(256, 768, 64, 128).convert_alpha(),
            self.texture.subsurface(320, 768, 64, 128).convert_alpha(),
            self.texture.subsurface(384, 768, 64, 128).convert_alpha(),
            self.texture.subsurface(448, 768, 64, 128).convert_alpha(),
            self.texture.subsurface(512, 768, 64, 128).convert_alpha(),
            self.texture.subsurface(576, 768, 64, 128).convert_alpha(),
            self.texture.subsurface(640, 768, 64, 128).convert_alpha()
        ))

        self.hit_texture = tuple((
            self.texture.subsurface(0, 896, 64, 128).convert_alpha(),
            self.texture.subsurface(64, 896, 64, 128).convert_alpha(),
            self.texture.subsurface(128, 896, 64, 128).convert_alpha(),
            self.texture.subsurface(192, 896, 64, 128).convert_alpha(),
            self.texture.subsurface(256, 896, 64, 128).convert_alpha(),
            self.texture.subsurface(320, 896, 64, 128).convert_alpha()
        ))

        self.hurt_texture = tuple((self.die_texture[0],))

    def get_direction_textures(self, is_moving: bool = False, direction: NpcSideName = None) -> SpriteSheet:

        if is_moving:
            if direction == NpcSideName.FRONT:
                return self.front_texture
            elif direction == NpcSideName.FRONT_LEFT:
                return self.frontleft_texture
            elif direction == NpcSideName.LEFT:
                return self.left_texture
            elif direction == NpcSideName.BACK_LEFT:
                return self.backleft_texture
            elif direction == NpcSideName.BACK:
                return self.back_texture
            elif direction == NpcSideName.BACK_RIGHT:
                return self.backright_texture
            elif direction == NpcSideName.RIGHT:
                return self.right_texture
            elif direction == NpcSideName.FRONT_RIGHT:
                return self.frontright_texture

        return self.stand_texture

    def default(self) -> pygame.Surface:
        return self.stand_texture[0]

    def animate(self, animation: NpcAnimation, side: NpcSide, current_frame: int) -> (pygame.Surface, int):
        """

        :param animation:
        :param side:
        :param current_frame:
        :return:
            pygame.Surface - the next surface to be drawn
            int - the next frame, if -1 then the animation has concluded
        """
        next_frame = current_frame + 1

        # walk animation
        if animation == NpcAnimation.WALKING:
            texture = self.get_direction_textures(True, side.name)
            if next_frame == len(texture):
                # loop back to begining
                next_frame = 0
            return texture[current_frame], next_frame
        # die animation
        elif animation == NpcAnimation.DYING:
            if next_frame == len(self.die_texture):
                # we stay dead on last frame
                next_frame = current_frame

            return self.die_texture[current_frame], next_frame
        # hurt animation
        elif animation == NpcAnimation.HURTING:
            # we might still be hurting or changing animations
            next_frame = 0
            return self.hurt_texture[0], next_frame
        # attack animation
        elif animation == NpcAnimation.ATTACKING:
            if next_frame == len(self.hit_texture):
                # we stay dead on last frame
                next_frame = -1

            return self.hit_texture[current_frame], next_frame

        # No Animation? Just stand there
        if side is not None:
            return self.stand_texture[side.stand_index], 0
        else:
            return self.default(), 0

    def get_side_for_theta(self, theta) -> NpcSide:
        # What side is the NPC facing?
        # (or not self.side is to make sure it finds the right angle from initialization)
        for side in self.sides:
            # need OR for SIDE_FRONT, as the degree_min is numerically
            # larger than the degree_max value
            if (side.degree_min < side.degree_max and side.degree_min <= theta <= side.degree_max) or \
                    (side.degree_min > side.degree_max and (theta >= side.degree_min or theta <= side.degree_max)):

                return side

        raise Warning(f"Unknown side for {theta}")
