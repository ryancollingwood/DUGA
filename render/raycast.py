import math

import pygame

import SETTINGS
import consts.geom
import consts.player
import consts.raycast
import consts.tile
import gamedata.tiles
import gamestate.player
import gamestate.rendering
from consts.geom import DEGREES_360, DEGREES_0, DEGREES_180, DEGREES_270, DEGREES_90
from render.slice import Slice

pygame.init()


def get_tan_in_radians(angle):
    return math.tan(math.radians(angle))


class Raycast:
    '''== Raycasting class ==\ncanvas -> Game canvas'''
    def __init__(self, canvas, canvas2):
        # TODO: Compute and store these known/knowable values instead of recomputing
        self.res = consts.raycast.resolution
        self.fov = consts.raycast.fov
        self.render = consts.raycast.render
        self.tile_size = consts.tile.TILE_SIZE
        self.door_size = self.tile_size / 2
        # rounding up `wall_width` so that we don't clip the walls
        # on the right hand side of the screen
        self.wall_width = math.ceil(SETTINGS.canvas_target_width / self.res)
        self.wall_height = int(SETTINGS.canvas_target_height / self.res)
        self.wall_width_to_height_difference = self.wall_width - self.wall_height
        self.fov_mod = self.fov * 0.8
        self.wall_height_mod = (DEGREES_360 / math.tan(math.radians(self.fov_mod))) * (self.wall_width_to_height_difference)
        self.canvas = canvas
        self.canvas2 = canvas2

        self.current_vtile = None
        self.current_htile = None


    def calculate(self):
        self.res = consts.raycast.resolution
        self.fov = consts.raycast.fov
        angle = consts.player.player_angle

        step = self.fov / self.res
        fov = int(self.fov/2)
        ray = -fov
        ray_number = 0

        for tile in SETTINGS.all_solid_tiles:
            tile.distance = tile.get_dist(gamestate.player.player_rect.center)

        while ray < fov:
            degree = angle - ray
            if degree <= DEGREES_0:
                degree += DEGREES_360
            elif degree > DEGREES_360:
                degree -= DEGREES_360

            self.beta = abs(degree - angle)

            self.cast(gamestate.player.player_rect, degree, ray_number)

            ray_number += 1
            ray += step


    @staticmethod
    def find_offset(position, ray_number, angle, tile, hv):
        #position is H_x or V_y
        if hv == 'v':
            if tile.type == 'vdoor':
                offset = abs(int(position - tile.rect.y)) - tile.open
            else:
                offset = abs(int(position - tile.rect.y))

        else:
            if tile.type == 'hdoor':
                offset = abs(int(position - tile.rect.x)) - tile.open
            else:
                offset = abs(int(position - tile.rect.x))

        #Fuck it. Catch all the crashes.
        if offset >= consts.tile.TILE_SIZE:
            offset = consts.tile.TILE_SIZE - 1
        return(offset)

    @staticmethod
    def check_hit(V_hit, H_hit, H_distance, V_distance, full_check):
        #Break loop if any ray has hit a wall
        if H_hit and V_hit:
            return True

        elif full_check:
            if H_hit:
                if H_distance < V_distance:
                    return True

            elif V_hit:
                if V_distance < H_distance:
                    return True


    def cast(self, player_rect, angle, ray_number):
        H_hit = False
        V_hit = False
        H_offset = V_offset = 0
        end_pos = (0, 0)

        angle -= 0.001

        #Horizontal
        if angle < DEGREES_180:
            H_y = int(player_rect.center[1] / self.tile_size) * self.tile_size
        else:
            H_y = int(player_rect.center[1] / self.tile_size) * self.tile_size + self.tile_size

        H_x = player_rect.center[0] + (player_rect.center[1] - H_y) / get_tan_in_radians(angle)

        #Vertical
        if angle > DEGREES_270 or angle < DEGREES_90:
            V_x = int(player_rect.center[0] / self.tile_size) * self.tile_size + self.tile_size
        else:
            V_x = int(player_rect.center[0] / self.tile_size) * self.tile_size

        V_y = player_rect.center[1] + (player_rect.center[0] - V_x) * get_tan_in_radians(angle)

        #Extend
        for x in range(0, consts.raycast.render):

            H_distance = abs((player_rect.center[0] - H_x) / math.cos(math.radians(angle)))
            V_distance = abs((player_rect.center[0] - V_x) / math.cos(math.radians(angle)))

            if self.check_hit(V_hit, H_hit, H_distance, V_distance, True):
                break

            for tile in SETTINGS.rendered_tiles:

                if self.check_hit(V_hit, H_hit, H_distance, V_distance, False):
                    break

                if not H_hit:
                    if (H_y == tile.rect.bottom and H_x >= tile.rect.bottomleft[0] and H_x <= tile.rect.bottomright[0]) and player_rect.centery > tile.rect.bottom:
                        H_hit = True
                        H_texture = gamedata.tiles.tile_texture[tile.ID]
                        self.current_htile = tile
                        if tile.type == 'hdoor':
                            H_y -= self.door_size
                            H_x += self.door_size / get_tan_in_radians(angle)
                            H_offset = offset = self.find_offset(H_x, ray_number, angle, tile, 'h')
                            if H_offset < 0:
                                H_hit = False
                                H_y += self.door_size
                                H_x -= self.door_size / get_tan_in_radians(angle)
                        else:
                            H_offset = offset = self.find_offset(H_x, ray_number, angle, tile, 'h')

                    elif (H_y == tile.rect.top and H_x >= tile.rect.topleft[0] and H_x <= tile.rect.topright[0]) and player_rect.centery < tile.rect.top:
                        H_hit = True
                        H_texture = gamedata.tiles.tile_texture[tile.ID]
                        self.current_htile = tile
                        if tile.type == 'hdoor':
                            H_y += self.door_size
                            H_x -= self.door_size / get_tan_in_radians(angle)
                            H_offset = offset = self.find_offset(H_x, ray_number, angle, tile, 'h')
                            if H_offset < 0:
                                H_hit = False
                                H_y -= self.door_size
                                H_x += self.door_size / get_tan_in_radians(angle)
                        else:
                            H_offset = self.find_offset(H_x, ray_number, angle, tile, 'h')

                if self.check_hit(V_hit, H_hit, H_distance, V_distance, False):
                    break

                if not V_hit:
                    if (V_x == tile.rect.left and V_y >= tile.rect.topleft[1] and V_y <= tile.rect.bottomleft[1]) and player_rect.centerx < tile.rect.left:
                        V_hit = True
                        V_texture = gamedata.tiles.tile_texture[tile.ID]
                        self.current_vtile = tile
                        if tile.type == 'vdoor':
                            V_x += self.door_size
                            V_y -= self.door_size * get_tan_in_radians(angle)
                            V_offset = self.find_offset(V_y, ray_number, angle, tile, 'v')
                            if V_offset < 0:
                               V_hit = False
                               V_x -= self.door_size
                               V_y += self.door_size * get_tan_in_radians(angle)
                        else:
                            V_offset = self.find_offset(V_y, ray_number, angle, tile, 'v')

                    elif (V_x == tile.rect.right and V_y >= tile.rect.topright[1] and V_y <= tile.rect.bottomright[1]) and player_rect.centerx > tile.rect.right:
                        V_hit = True
                        V_texture = gamedata.tiles.tile_texture[tile.ID]
                        self.current_vtile = tile
                        if tile.type == 'vdoor':
                            V_x -= self.door_size
                            V_y += self.door_size * get_tan_in_radians(angle)
                            V_offset = self.find_offset(V_y, ray_number, angle, tile, 'v')
                            if V_offset < 0:
                               V_hit = False
                               V_x += self.door_size
                               V_y -= self.door_size * get_tan_in_radians(angle)
                        else:
                            V_offset = self.find_offset(V_y, ray_number, angle, tile, 'v')

            #Extend actual ray
            if not H_hit:
                if angle < DEGREES_180:
                    H_y -= self.tile_size
                else:
                    H_y += self.tile_size
                if angle >= DEGREES_180:
                    H_x -= self.tile_size / get_tan_in_radians(angle)
                else:
                    H_x += self.tile_size / get_tan_in_radians(angle)

            if not V_hit:
                if angle > DEGREES_270 or angle < DEGREES_90: # ->
                    V_x += self.tile_size
                else:
                    V_x -= self.tile_size
                if angle >= DEGREES_270 or angle < DEGREES_90: # <-
                    V_y -= self.tile_size * get_tan_in_radians(angle)
                else:
                    V_y += self.tile_size * get_tan_in_radians(angle)


        if V_hit and H_hit:
            H_hit, V_hit = False, False
            if H_distance < V_distance:
                end_pos = (H_x, H_y)
                texture = H_texture
                tile_len = H_distance
                offset = H_offset
                current_tile = self.current_htile
                H_hit = True
            else:
                end_pos = (V_x, V_y)
                texture = V_texture
                tile_len = V_distance
                offset = V_offset
                current_tile = self.current_vtile
                V_hit = True

        elif H_hit and not V_hit:
            end_pos = (H_x, H_y)
            texture = H_texture
            tile_len = H_distance
            offset = H_offset
            current_tile = self.current_htile

        elif V_hit and not H_hit:
            end_pos = (V_x, V_y)
            texture = V_texture
            tile_len = V_distance
            offset = V_offset
            current_tile = self.current_vtile

        else:
            end_pos = (gamestate.player.player_rect[0], gamestate.player.player_rect[1])
            texture = None
            tile_len = None
            offset = 0
            current_tile = None

        if V_hit:
            vh = 'v'
        else:
            vh = 'h'

        #Mode
        self.control(end_pos, ray_number, tile_len, player_rect, texture, offset, current_tile, vh)


    def control(self, end_pos, ray_number, tile_len, player_rect, texture, offset, current_tile, vh):
        if SETTINGS.mode == 1:
            if tile_len:
                wall_dist = tile_len * math.cos(math.radians(self.beta))
            else:
                wall_dist = None
            self.render_screen(ray_number, wall_dist, texture, int(offset), current_tile, vh, end_pos)

        else:
            self.draw_line(player_rect, end_pos)



    def render_screen(self, ray_number, wall_dist, texture, offset, current_tile, vh, end_pos):
        if wall_dist:
            #wall_height = int((self.TILE_SIZE / wall_dist) * (360 / math.tan(math.radians(SETTINGS.fov * 0.8))))

            wall_height = int((self.tile_size / wall_dist) * self.wall_height_mod)
            gamestate.rendering.zbuffer.append(Slice((texture.slices[offset], 0), texture.texture, texture.rect.width, vh))
            gamestate.rendering.zbuffer[ray_number].distance = wall_dist
            rendered_slice = pygame.transform.scale(gamestate.rendering.zbuffer[ray_number].slice, (self.wall_width, wall_height))
            gamestate.rendering.zbuffer[ray_number].update_rect(rendered_slice)
            gamestate.rendering.zbuffer[ray_number].xpos = ((ray_number) * self.wall_width)

        else:
            gamestate.rendering.zbuffer.append(None)

        #Middle ray info
        if ray_number == int(self.res/2):
            gamestate.rendering.middle_slice_len = wall_dist
            gamestate.rendering.middle_slice = current_tile
            gamestate.rendering.middle_ray_pos = end_pos

    @staticmethod
    def draw_line(player_rect, end_pos):
        gamestate.rendering.raylines.append((player_rect.center, end_pos))