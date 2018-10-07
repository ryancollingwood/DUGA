import math
import os

import pygame

import SETTINGS
import SOUND
import SPRITES
import consts.tile
import gamedata.tiles
import gamestate.npcs
import gamestate.player
import gamestate.sprites
from gamestate.rendering import add_blit

class Tile:

    def __init__(self, ID, pos, map_pos):
        self.ID = ID
        #position in pixels
        self.pos = pos
        self.type = gamedata.tiles.texture_type[self.ID]
        #position in tiles
        self.map_pos = map_pos
        self.distance = None
        self.solid = gamedata.tiles.tile_solid[self.ID]
        #For doors opening
        self.state = None
        self.timer = 0

        if self.type == 'sprite':
            current_number = len(gamestate.sprites.all_sprites)
            #Need some weird coordinates to make it centered.
            self.texture = SPRITES.Sprite(gamedata.tiles.tile_texture[self.ID], self.ID, (self.pos[0] + consts.tile.TILE_SIZE / 3, self.pos[1] + consts.tile.TILE_SIZE / 3), 'sprite')

            self.rect = pygame.Rect(pos[0], pos[1], consts.tile.TILE_SIZE / 2, consts.tile.TILE_SIZE / 2)

        else:
            self.texture = gamedata.tiles.tile_texture[self.ID].texture
            self.icon = pygame.transform.scale(self.texture, (16,16)).convert()
            self.texture = pygame.transform.scale(self.texture, (
                consts.tile.TILE_SIZE, consts.tile.TILE_SIZE)).convert()
            self.rect = self.texture.get_rect()
            self.rect.x = pos[0]
            self.rect.y = pos[1]

            if self.type == consts.tile.VERTICAL_DOOR or self.type == consts.tile.HORIZONTAL_DOOR:
                self.open = 0
                self.state = 'closed'
                #states: closed, opening, open, closing

                self.open_sound = pygame.mixer.Sound(os.path.join('sounds', 'other', 'door_open.ogg'))
                self.close_sound = pygame.mixer.Sound(os.path.join('sounds', 'other', 'door_close.ogg'))

                SETTINGS.all_doors.append(self)

    def __str__(self):
        return f"{self.type}, solid: {self.solid}, state: {self.state}, map_pos: {self.map_pos}"


    def draw(self, canvas):
        add_blit(canvas.blit(self.icon, (self.rect.x/4, self.rect.y/4)))

    def get_dist(self, pos, *called):
        xpos = self.rect.center[0] - pos[0]
        ypos = pos[1] - self.rect.center[1]
        self.distance = math.sqrt(xpos*xpos + ypos*ypos)

        if (self.state and self.state != 'closed') and called != ('npc',): #lol
            self.sesam_luk_dig_op()

        return self.distance

    def sesam_luk_dig_op(self):
        if self.open > consts.tile.TILE_SIZE:
            self.open = consts.tile.TILE_SIZE
        elif self.open < 0:
            self.open = 0

        if self.state == 'closed':
            self.state = 'opening'

        elif self.state == 'opening':
            if self.open == 0:
                SOUND.play_sound(self.open_sound, self.distance)

            if self.open < consts.tile.TILE_SIZE:
                self.open += consts.tile.TILE_SIZE * SETTINGS.dt
            else:
                self.state = 'open'
                self.solid = False
            if self.open > consts.tile.TILE_SIZE /1.4:
                self.solid = False

        elif self.state == 'open':
            self.timer += SETTINGS.dt
            if self.timer > 5 and not self.rect.colliderect(gamestate.player.player_rect):
                for i in gamestate.npcs.npc_list:
                    if self.rect.colliderect(i.rect):
                        break
                else:
                    self.state = 'closing'
                    self.solid = True
                    self.timer = 0

        elif self.state == 'closing':
            if self.open >= consts.tile.TILE_SIZE:
                SOUND.play_sound(self.close_sound, self.distance)
            if self.open > 0:
                self.open -= consts.tile.TILE_SIZE * SETTINGS.dt
            else:
                self.state = 'closed'