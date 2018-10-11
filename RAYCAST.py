# This is the script where all the code for raycasting goes. The screen rendering in 2.5D will also go here.

import SETTINGS
import pygame
import math
from GEOM import sort_atan


pygame.init()


class Slice:
    def __init__(self, location, surface, width, vh):
        self.slice = surface.subsurface(pygame.Rect(location, (1, width))).convert()
        self.rect = self.slice.get_rect(center=(0, SETTINGS.canvas_target_height / 2))
        self.distance = None
        self.type = 'slice'
        self.vh = vh
        self.xpos = 0
        self.tempslice = None
        self.darkslice = None

        if SETTINGS.shade:
            self.shade_slice = pygame.Surface(self.slice.get_size()).convert_alpha()
            sv = SETTINGS.shade_visibility / 10
            self.shade_intensity = [sv * 1, sv * 2, sv * 3, sv * 4, sv * 5, sv * 6, sv * 7, sv * 8, sv * 9, sv * 10]

    def update_rect(self, new_slice):
        self.tempslice = new_slice
        self.rect = new_slice.get_rect(center=(self.xpos, int(SETTINGS.canvas_target_height / 2)))

        if self.vh == 'v':
            self.darkslice = pygame.Surface(self.tempslice.get_size()).convert_alpha()
            self.darkslice.fill((0, 0, 0, SETTINGS.texture_darken))

        if SETTINGS.shade:
            # Shade intensity table
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
            self.shade_slice.fill((SETTINGS.shade_rgba[0] * intensity, SETTINGS.shade_rgba[1] * intensity,
                                   SETTINGS.shade_rgba[2] * intensity, SETTINGS.shade_rgba[3] * intensity))


class Raycast:
    '''== Raycasting class ==\ncanvas -> Game canvas'''

    def __init__(self, canvas, canvas2):
        # TODO: Compute and store these known/knowable values instead of recomputing
        self.res = SETTINGS.resolution
        self.fov = SETTINGS.fov
        self.render = SETTINGS.render
        self.tile_size = SETTINGS.tile_size
        self.door_size = self.tile_size / 2
        # rounding up `wall_width` so that we don't clip the walls 
        # on the right hand side of the screen        
        self.wall_width = math.ceil(SETTINGS.canvas_target_width / self.res)
        self.wall_height = int(SETTINGS.canvas_target_height / self.res)
        self.wall_width_to_height_difference = self.wall_width - self.wall_height
        self.fov_mod = self.fov * 0.8
        self.wall_height_mod = (360 / math.tan(math.radians(self.fov_mod))) * self.wall_width_to_height_difference
        self.canvas = canvas
        self.canvas2 = canvas2

        self.current_vtile = None
        self.current_htile = None

    def calculate(self):
        self.res = SETTINGS.resolution
        self.fov = SETTINGS.fov

        step = self.fov / self.res
        fov = int(self.fov / 2)
        ray = -fov
        ray_number = 0

        for tile in SETTINGS.all_solid_tiles:
            tile.distance = tile.get_dist(SETTINGS.player_rect.center)
            tile.atan = sort_atan(tile)
        
        current_h_tile = None
        last_h_tile = None
        current_v_tile = None
        last_v_tile = None
        
        angle = SETTINGS.player_angle

        while ray < fov:
            degree = angle - ray
            if degree <= 0:
                degree += 360
            elif degree > 360:
                degree -= 360

            beta = abs(degree - angle)

            cast_horizontal_tile, cast_vertical_tile = self.cast(
                SETTINGS.player_rect, degree, ray_number, beta,
                current_h_tile, current_v_tile, SETTINGS.rendered_tiles
            )

            # not doing anything with these values at the moment :/
            # still need to work on how to use them to reduce the
            # search space of tiles rather than SETTINGS.rendered_tiles
            if cast_horizontal_tile is not None:
                if last_h_tile != current_h_tile:
                    last_h_tile = current_h_tile
                current_h_tile = cast_horizontal_tile

            if cast_vertical_tile is not None:
                if last_v_tile != current_v_tile:
                    last_v_tile = current_v_tile
                current_v_tile = cast_vertical_tile
                
            ray_number += 1
            ray += step

    @staticmethod
    def find_offset(position, tile, hv):
        # position is H_x or V_y
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

        # Fuck it. Catch all the crashes.
        if offset >= SETTINGS.tile_size:
            offset = SETTINGS.tile_size - 1
        
        return offset

    @staticmethod
    def check_hit(V_hit, H_hit, H_distance, V_distance, full_check):
        # Break loop if any ray has hit a wall
        if H_hit and V_hit:
            return True

        elif full_check:
            if H_hit:
                if H_distance < V_distance:
                    return True

            elif V_hit:
                if V_distance < H_distance:
                    return True

    def set_current_tile(self, tile, is_horizontal):
        if is_horizontal:
            self.current_htile = tile
        else:
            self.current_vtile = tile

    @staticmethod
    # TODO probably can remove this as not resorting tiles
    def resort_tiles(index, tiles):
        if index:
            if index > 0:
                return tiles[index:] + tiles[:index + 1]
        return tiles

    def cast(self, player_rect, angle, ray_number, beta, previous_horizontal_tile, previous_vertical_tile, search_tiles):
        H_hit = False
        V_hit = False
        H_offset = V_offset = 0

        test_tile_for_horizontal_hit = self.test_tile_for_horizontal_hit
        test_tile_for_vertical_hit = self.test_tile_for_vertical_hit

        tile_size = self.tile_size

        H_x, H_y, V_x, V_y, angle, cos_radians_angle, tan_radians_angle = self.get_camera_plane_for_angle(
            angle, player_rect, tile_size
        )

        search_tiles_for_hit = self.search_tiles_for_hit
        check_hit = self.check_hit

        # Extend
        for x in range(0, SETTINGS.render):

            H_distance = abs((player_rect.center[0] - H_x) / cos_radians_angle)
            V_distance = abs((player_rect.center[0] - V_x) / cos_radians_angle)

            if check_hit(V_hit, H_hit, H_distance, V_distance, True):
                break
            
            # test if the last tile(s) are a hit?
            # doors are rendering a little odd so not reusing doors
            if previous_horizontal_tile and previous_horizontal_tile in search_tiles:
                if previous_horizontal_tile.type != 'hdoor':
                    H_hit, H_offset, H_x, H_y = test_tile_for_horizontal_hit(
                        H_hit, H_offset, H_x, H_y, player_rect, tan_radians_angle, previous_horizontal_tile
                    )
                
            if previous_vertical_tile and previous_vertical_tile in search_tiles:
                if previous_vertical_tile.type != 'vdoor':
                    V_hit, V_offset, V_x, V_y = test_tile_for_vertical_hit(
                        V_hit, V_offset, V_x, V_y, player_rect, tan_radians_angle, previous_vertical_tile
                    )

            if check_hit(V_hit, H_hit, H_distance, V_distance, False):
                # print("saved some loops")
                break

            got_H_hit, H_values, got_V_hit, V_values = search_tiles_for_hit(
                H_distance, H_hit, H_offset, H_x, H_y,
                V_distance, V_hit, V_offset, V_x, V_y,
                player_rect, search_tiles, tan_radians_angle
            )

            if got_H_hit:
                H_hit = True
                H_offset, H_x, H_y = H_values
            if got_V_hit:
                V_hit = True
                V_offset, V_x, V_y = V_values

            # Extend actual ray
            if not H_hit:
                if angle < 180:
                    H_y -= tile_size
                else:
                    H_y += tile_size
                if angle >= 180:
                    H_x -= tile_size / tan_radians_angle
                else:
                    H_x += tile_size / tan_radians_angle

            if not V_hit:
                if angle > 270 or angle < 90:  # ->
                    V_x += tile_size
                else:
                    V_x -= tile_size
                if angle >= 270 or angle < 90:  # <-
                    V_y -= tile_size * tan_radians_angle
                else:
                    V_y += tile_size * tan_radians_angle

        if V_hit and H_hit:
            H_hit, V_hit = False, False
            if H_distance < V_distance:
                current_tile, end_pos, offset, texture, tile_len = self.use_horizontal_tile(
                    H_distance, H_offset, H_x, H_y
                )
                H_hit = True
            else:
                current_tile, end_pos, offset, texture, tile_len = self.use_vertical_tile(
                    V_distance, V_offset, V_x, V_y
                )
                V_hit = True

        elif H_hit and not V_hit:
            current_tile, end_pos, offset, texture, tile_len = self.use_horizontal_tile(
                H_distance, H_offset, H_x, H_y
            )

        elif V_hit and not H_hit:
            current_tile, end_pos, offset, texture, tile_len = self.use_vertical_tile(
                V_distance, V_offset, V_x, V_y
            )

        else:
            end_pos = (SETTINGS.player_rect[0], SETTINGS.player_rect[1])
            texture = None
            tile_len = None
            offset = 0
            current_tile = None

        # Mode
        if V_hit:
            vh = 'v'
        else:
            vh = 'h'
            
        self.control(end_pos, ray_number, tile_len, player_rect, texture, offset, current_tile, vh, beta)
        
        return self.current_htile, self.current_vtile

    def search_tiles_for_hit(self, H_distance, H_hit, H_offset, H_x, H_y, V_distance, V_hit, V_offset, V_x, V_y,
                             player_rect, search_tiles, tan_radians_angle):

        if not H_hit:
            H_hit, H_offset, H_x, H_y = self.test_tiles_for_horizontal_hit(
                H_hit, H_offset, H_x, H_y, player_rect, tan_radians_angle, search_tiles
            )

        if not V_hit:
            V_hit, V_offset, V_x, V_y = self.test_tiles_for_vertical_hit(
                V_hit, V_offset, V_x, V_y, player_rect, tan_radians_angle, search_tiles
            )

        return H_hit, (H_offset, H_x, H_y), V_hit, (V_offset, V_x, V_y)


    def test_tiles_for_vertical_hit(self, V_hit, V_offset, V_x, V_y, player_rect, tan_radians_angle, tiles):

        tiles_left = [
            tile for tile in tiles if
            V_x == tile.rect.left and
            tile.rect.topleft[1] <= V_y <= tile.rect.bottomleft[1] and
            player_rect.centerx < tile.rect.left
        ]

        tiles_right = [
            tile for tile in tiles if
            V_x == tile.rect.right and
            tile.rect.topright[1] <= V_y <= tile.rect.bottomright[1] and
            player_rect.centerx > tile.rect.right
        ]

        if len(tiles_left) > 0:

            V_hit, V_offset, V_texture, V_x, V_y = self.set_vertical_hit_values(
                V_x, V_y, tan_radians_angle, tiles_left[0], False
            )
        elif len(tiles_right) > 0:

            V_hit, V_offset, V_texture, V_x, V_y = self.set_vertical_hit_values(
                V_x, V_y, tan_radians_angle, tiles_right[0], True
            )

        return V_hit, V_offset, V_x, V_y


    def test_tile_for_vertical_hit(self, V_hit, V_offset, V_x, V_y, player_rect, tan_radians_angle, tile):
        left_conditions = [
            V_x == tile.rect.left,
            V_y >= tile.rect.topleft[1],
            V_y <= tile.rect.bottomleft[1]
        ]
        right_conditions = [
            V_x == tile.rect.right,
            V_y >= tile.rect.topright[1],
            V_y <= tile.rect.bottomright[1]
        ]
        if all(left_conditions) and player_rect.centerx < tile.rect.left:
            V_hit, V_offset, V_texture, V_x, V_y = self.set_vertical_hit_values(
                V_x, V_y, tan_radians_angle, tile, False
            )
    
        elif all(right_conditions) and player_rect.centerx > tile.rect.right:
            V_hit, V_offset, V_texture, V_x, V_y = self.set_vertical_hit_values(
                V_x, V_y, tan_radians_angle, tile, True
            )
        return V_hit, V_offset, V_x, V_y

    def test_tiles_for_horizontal_hit(self, H_hit, H_offset, H_x, H_y, player_rect, tan_radians_angle, tiles):

        bottom_tiles = [
            tile for tile in tiles if
            H_y == tile.rect.bottom and
            tile.rect.bottomleft[0] <= H_x <= tile.rect.bottomright[0] and
            player_rect.centery > tile.rect.bottom
        ]

        top_tiles = [
            tile for tile in tiles if
            H_y == tile.rect.top and
            tile.rect.topleft[0] <= H_x <= tile.rect.topright[0] and
            player_rect.centery < tile.rect.top
        ]

        if len(bottom_tiles) > 0:
            H_hit, H_offset, H_texture, H_x, H_y = self.set_horizontal_hit_values(
                H_x, H_y, tan_radians_angle, bottom_tiles[0], True
            )
        elif len(top_tiles) > 0:
            H_hit, H_offset, H_texture, H_x, H_y = self.set_horizontal_hit_values(
                H_x, H_y, tan_radians_angle, top_tiles[0], False
            )
        return H_hit, H_offset, H_x, H_y

    def test_tile_for_horizontal_hit(self, H_hit, H_offset, H_x, H_y, player_rect, tan_radians_angle, tile):
        bottom_conditions = [
            H_y == tile.rect.bottom,
            H_x >= tile.rect.bottomleft[0],
            H_x <= tile.rect.bottomright[0]
        ]
        top_conditions = [
            H_y == tile.rect.top,
            H_x >= tile.rect.topleft[0],
            H_x <= tile.rect.topright[0]
        ]
        if all(bottom_conditions) and player_rect.centery > tile.rect.bottom:
            H_hit, H_offset, H_texture, H_x, H_y = self.set_horizontal_hit_values(
                H_x, H_y, tan_radians_angle, tile, True
            )
    
        elif all(top_conditions) and player_rect.centery < tile.rect.top:
            H_hit, H_offset, H_texture, H_x, H_y = self.set_horizontal_hit_values(
                H_x, H_y, tan_radians_angle, tile, False
            )
        return H_hit, H_offset, H_x, H_y

    def set_vertical_hit_values(self, V_x, V_y, tan_radians_angle, tile, player_rect_gt):
        V_hit = True
        V_texture = SETTINGS.tile_texture[tile.ID]
        
        self.set_current_tile(tile, False)
        door_size = self.door_size
        
        if tile.type == 'vdoor':
            if not player_rect_gt:
                V_x += door_size
                V_y -= door_size * tan_radians_angle
            else:
                V_x -= door_size
                V_y += door_size * tan_radians_angle

            V_offset = self.find_offset(V_y, tile, 'v')
            
            if V_offset < 0:
                V_hit = False
                if not player_rect_gt:
                    V_x -= door_size
                    V_y += door_size * tan_radians_angle
                else:
                    V_x += door_size
                    V_y -= door_size * tan_radians_angle

        else:
            V_offset = self.find_offset(V_y, tile, 'v')

        return V_hit, V_offset, V_texture, V_x, V_y

    def set_horizontal_hit_values(self, H_x, H_y, tan_radians_angle, tile, player_rect_gt):
        H_hit = True
        H_texture = SETTINGS.tile_texture[tile.ID]
        
        self.set_current_tile(tile, True)
        door_size = self.door_size
        
        if tile.type == 'hdoor':
            if player_rect_gt:
                H_y -= door_size
                H_x += door_size / tan_radians_angle
            else:
                H_y += door_size
                H_x -= door_size / tan_radians_angle

            H_offset = self.find_offset(H_x, tile, 'h')
            
            if H_offset < 0:
                H_hit = False
                
                if player_rect_gt:
                    H_y += door_size
                    H_x -= door_size / tan_radians_angle
                else:
                    H_y -= door_size
                    H_x += door_size / tan_radians_angle

        else:
            H_offset = self.find_offset(H_x, tile, 'h')
            
        return H_hit, H_offset, H_texture, H_x, H_y

    def use_vertical_tile(self, V_distance, V_offset, V_x, V_y):
        end_pos = (V_x, V_y)
        tile_len = V_distance
        offset = V_offset
        current_tile = self.current_vtile
        texture = SETTINGS.tile_texture[current_tile.ID]

        return current_tile, end_pos, offset, texture, tile_len

    def use_horizontal_tile(self, H_distance, H_offset, H_x, H_y):
        end_pos = (H_x, H_y)
        tile_len = H_distance
        offset = H_offset
        current_tile = self.current_htile
        texture = SETTINGS.tile_texture[current_tile.ID]

        return current_tile, end_pos, offset, texture, tile_len

    @staticmethod
    def get_camera_plane_for_angle(angle, player_rect, tile_size):
        # tan for right angle values result in undefined value
        # therefore add a tiny amount to the angle to mitigate this
        angle -= 0.001
        
        # Horizontal
        if angle < 180:
            H_y = int(player_rect.center[1] / tile_size) * tile_size
        else:
            H_y = int(player_rect.center[1] / tile_size) * tile_size + tile_size
            
        # numba could shave off some ns on this
        tan_radians_angle = math.tan(math.radians(angle))
        cos_radians_angle = math.cos(math.radians(angle))
        
        H_x = player_rect.center[0] + (player_rect.center[1] - H_y) / tan_radians_angle
        
        # Vertical
        if angle > 270 or angle < 90:
            V_x = int(player_rect.center[0] / tile_size) * tile_size + tile_size
        else:
            V_x = int(player_rect.center[0] / tile_size) * tile_size
            
        V_y = player_rect.center[1] + (player_rect.center[0] - V_x) * tan_radians_angle
        
        return H_x, H_y, V_x, V_y, angle, cos_radians_angle, tan_radians_angle

    def control(self, end_pos, ray_number, tile_len, player_rect, texture, offset, current_tile, vh, beta):
        if SETTINGS.mode == 1:
            if tile_len:
                wall_dist = tile_len * math.cos(math.radians(beta))
            else:
                wall_dist = None
                
            self.render_screen(ray_number, wall_dist, texture, int(offset), current_tile, vh, end_pos)

        else:
            self.draw_line(player_rect, end_pos)

    def render_screen(self, ray_number, wall_dist, texture, offset, current_tile, vh, end_pos):
        if wall_dist:
            # wall_height = int((self.tile_size / wall_dist) * (360 / math.tan(math.radians(SETTINGS.fov * 0.8))))
            
            wall_height = int((self.tile_size / wall_dist) * self.wall_height_mod)
            SETTINGS.zbuffer.append(Slice((texture.slices[offset], 0), texture.texture, texture.rect.width, vh))
            SETTINGS.zbuffer[ray_number].distance = wall_dist
            rendered_slice = pygame.transform.scale(SETTINGS.zbuffer[ray_number].slice, (self.wall_width, wall_height))
            SETTINGS.zbuffer[ray_number].update_rect(rendered_slice)
            SETTINGS.zbuffer[ray_number].xpos = ray_number * self.wall_width

        else:
            SETTINGS.zbuffer.append(None)

        # Middle ray info
        if ray_number == int(self.res / 2):
            SETTINGS.middle_slice_len = wall_dist
            SETTINGS.middle_slice = current_tile
            SETTINGS.middle_ray_pos = end_pos

    @staticmethod
    def draw_line(player_rect, end_pos):
        SETTINGS.raylines.append((player_rect.center, end_pos))
