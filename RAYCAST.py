#This is the script where all the code for raycasting goes. The screen rendering in 2.5D will also go here.

import SETTINGS
import PLAYER
import pygame
import math

pygame.init()

class Slice:

    def __init__(self, tile_id, location, vh, pos, ray_number, wall_width, distance, height, other_pos, offset):
        # tile_id determines which texture we will draw
        self.tile_id = tile_id
        self.location = location
        self.vh = vh
        # the x value where this slice is drawn
        self.xpos = ray_number * wall_width
        self.ray_number = ray_number
        self.wall_width = wall_width
        # where in the game map is the slice
        self.pos = pos
        self.distance = distance
        self.height = height
        self.type = "slice"
        self.intensity = 1
        self.other_pos = other_pos
        self.offset = offset

        self.slice = None
        self.alpha_slice = None
        self.dark_slice = None
        self.shade_slice = None
        self.blit_dest = None

    def __eq__(self, other):
        try:
            # self.other_pos is excluded as
            # it doesn't define a slice
            return all([
                self.distance == other.distance,
                self.height == other.height,
                self.location == other.location,
                self.pos == other.map_pos,
                self.ray_number == other.ray_number,
                self.tile_id == other.tile_id,
                self.type == other.type,
                self.vh == other.vh,
                self.wall_width == other.wall_width,
                self.xpos == other.xpos,
                self.intensity == other.intensity,
                self.offset == other.offset
             ])
        except AttributeError:
            return False

    def __str__(self):
        return str(vars(self))

    def get_slice_surface(self):
        tile_texture = SETTINGS.tile_texture[self.tile_id].texture
        texture_width = tile_texture.get_rect().width
        slice_texture = tile_texture.subsurface(pygame.Rect(self.location, (1, texture_width))).convert()
        self.slice = pygame.transform.scale(slice_texture, (self.wall_width, self.height))

        if SETTINGS.shade or self.vh == 'v':
            self.alpha_slice = pygame.Surface(self.slice.get_size()).convert_alpha()

        rect = self.slice.get_rect(center=(self.xpos, int(SETTINGS.canvas_target_height / 2)))
        self.blit_dest = (self.xpos, rect.y)

    def get_blit_surface_and_location(self):
        self.get_slice_surface()

        if self.vh == 'v':
            self.dark_slice = self.alpha_slice.fill((0, 0, 0, SETTINGS.texture_darken))

        if SETTINGS.shade:
            #Shade intensity table
            sv = SETTINGS.shade_visibility / 10
            shade_intensity = [sv * 1, sv * 2, sv * 3, sv * 4, sv * 5, sv * 6, sv * 7, sv * 8, sv * 9, sv * 10]

            if self.distance < shade_intensity[0]:
                self.intensity = 0
            elif self.distance < shade_intensity[1]:
                self.intensity = 0.1
            elif self.distance < shade_intensity[2]:
                self.intensity = 0.2
            elif self.distance < shade_intensity[3]:
                self.intensity = 0.3
            elif self.distance < shade_intensity[4]:
                self.intensity = 0.4
            elif self.distance < shade_intensity[5]:
                self.intensity = 0.5
            elif self.distance < shade_intensity[6]:
                self.intensity = 0.6
            elif self.distance < shade_intensity[7]:
                self.intensity = 0.7
            elif self.distance < shade_intensity[8]:
                self.intensity = 0.8
            elif self.distance < shade_intensity[9]:
                self.intensity = 0.9
            else:
                self.intensity = 1

            self.shade_slice = self.alpha_slice_surface.fill(
                (SETTINGS.shade_rgba[0]*self.intensity, SETTINGS.shade_rgba[1]*self.intensity,
                 SETTINGS.shade_rgba[2]*self.intensity, SETTINGS.shade_rgba[3]*self.intensity)
            )

        return self.slice_surface, self.blit_dest


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
        self.wall_height_mod = (360 / math.tan(math.radians(self.fov_mod))) * (self.wall_width_to_height_difference)        
        self.canvas = canvas
        self.canvas2 = canvas2

        self.current_vtile = None
        self.current_htile = None
        self.next_zbuffer = None
        # smaller numbers result in less oddity
        # smallest effective value is 2
        self.interpolation = 2

    def calculate(self):
        angle = SETTINGS.player_angle

        ray_values = self.get_ray_values_for_angle(angle)

        for tile in SETTINGS.all_solid_tiles:
            tile.distance = tile.get_dist(SETTINGS.player_rect.center)


        middle_ray_number = int(self.res / 2)

        # initialise an array for our rays
        self.next_zbuffer = [None for x in range(self.res + 1)]

        #while ray < fov:
        for ray_value in ray_values:
            ray_number = ray_value[0]
            degree = ray_value[1]
            beta = ray_value[3]

            self.beta = beta

            if ray_number % self.interpolation != 0:
                # need the start and end for filling in blanks
                # need the middle for player interaction
                if ray_number != middle_ray_number:
                    self.next_zbuffer[ray_number] = None
                    continue

            self.next_zbuffer[ray_number] = self.cast(SETTINGS.player_rect, degree, ray_number)

        # fill in the gaps
        self.fill_in_interpolate_gaps(ray_values)

        SETTINGS.zbuffer = self.next_zbuffer

        return self.next_zbuffer

    def get_ray_values_for_angle(self, angle):

        # slightly adjust angle to prevent undefined
        # results for right angles etc.
        angle -= 0.001
        step = self.fov / self.res
        fov = int(self.fov / 2)
        ray = -fov
        # pre calc ray values
        # could possibly do this for
        # a number of angles?
        values = list()
        for ray_number in range(0, self.res+1):
            degree = angle - ray
            if degree <= 0:
                degree += 360
            elif degree > 360:
                degree -= 360

            beta = abs(degree - angle)
            ray += step

            values.append((ray_number, degree, ray, beta, angle))
        return values

    def fill_in_interpolate_gaps(self, ray_values):
        left_slice = None
        right_slice = None

        for i, slice in enumerate(self.next_zbuffer):
            if slice is not None:
                if left_slice is None and right_slice is None:
                    left_slice = slice
                elif left_slice is not None and right_slice is None:
                    right_slice = slice
                elif left_slice is not None and right_slice is not None:
                    right_slice = left_slice
                    left_slice = slice
            else:
                degree = ray_values[i][1]
                ray_number = ray_values[i][0]
                self.beta = ray_values[i][3]
                ray_origin = None

                if left_slice is not None:

                    # this covers the case of the very first
                    # gap where we haven't found a pair
                    if right_slice is None:
                        next_right = self.interpolation - i + 1
                        right_slice = self.next_zbuffer[next_right]

                    if left_slice.vh == right_slice.vh:
                        if left_slice.vh == "h":
                            left_H_y = left_slice.pos[1]
                            left_V_x = left_slice.other_pos[0]
                            right_H_y = right_slice.pos[1]
                            right_V_x = right_slice.other_pos[0]
                        else:
                            left_H_y = left_slice.other_pos[1]
                            left_V_x = left_slice.pos[0]
                            right_H_y = right_slice.other_pos[1]
                            right_V_x = right_slice.pos[0]

                        H_y = left_H_y
                        H_x = left_V_x
                        if right_H_y < H_y:
                            H_y = right_H_y
                        if right_V_x < H_x:
                            H_x = right_V_x

                        offset = left_slice.offset
                        if right_slice.offset < left_slice.offset:
                            offset = right_slice.offset

                        ray_origin = (left_slice.vh, H_x, H_y, offset)

                new_ray = self.cast(SETTINGS.player_rect, degree, ray_number, ray_origin)
                if new_ray is None and ray_origin is not None:
                    new_ray = self.cast(SETTINGS.player_rect, degree, ray_number)
                    print("rescan")
                self.next_zbuffer[i] = new_ray


    def find_offset(self, position, ray_number, angle, tile, hv):
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
        if offset >= SETTINGS.tile_size:
            offset = SETTINGS.tile_size - 1
        return(offset)

    def check_hit(self, V_hit, H_hit, H_distance, V_distance, full_check):
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
            

    def cast(self, player_rect, angle, ray_number, ray_origrin = None):
        H_hit = False
        V_hit = False
        H_offset = V_offset = 0
        end_pos = (0, 0)
        passed_offset = None

        if ray_origrin is None:
            H_x, H_y, V_x, V_y = self.get_ray_origin(angle, player_rect)
        else:
            V_x, H_y  = ray_origrin[1], ray_origrin[2]
            H_x, V_y = self.get_ray_origin_for_angle(V_x, H_y, angle, player_rect)
            passed_offset = ray_origrin[3]

        #Extend
        for x in range(0, SETTINGS.render):
            
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
                        H_texture_id = tile.ID
                        self.current_htile = tile

                        if tile.type == 'hdoor':
                            H_y -= self.door_size
                            H_x += self.door_size / math.tan(math.radians(angle))
                            H_offset = self.find_offset(H_x, ray_number, angle, tile, 'h')
                            if H_offset < 0:
                                H_hit = False
                                H_y += self.door_size
                                H_x -= self.door_size / math.tan(math.radians(angle))
                        else:
                            H_offset = self.find_offset(H_x, ray_number, angle, tile, 'h')
                            
                    elif (H_y == tile.rect.top and H_x >= tile.rect.topleft[0] and H_x <= tile.rect.topright[0]) and player_rect.centery < tile.rect.top:
                        H_hit = True
                        H_texture_id = tile.ID
                        self.current_htile = tile

                        if tile.type == 'hdoor':
                            H_y += self.door_size
                            H_x -= self.door_size / math.tan(math.radians(angle))
                            H_offset = self.find_offset(H_x, ray_number, angle, tile, 'h')
                            if H_offset < 0:
                                H_hit = False
                                H_y -= self.door_size
                                H_x += self.door_size / math.tan(math.radians(angle))
                        else:
                            H_offset = self.find_offset(H_x, ray_number, angle, tile, 'h')
                                
                if self.check_hit(V_hit, H_hit, H_distance, V_distance, False):
                    break
                        
                if not V_hit:
                    if (V_x == tile.rect.left and V_y >= tile.rect.topleft[1] and V_y <= tile.rect.bottomleft[1]) and player_rect.centerx < tile.rect.left:
                        V_hit = True
                        V_texture_id = tile.ID
                        self.current_vtile = tile

                        if tile.type == 'vdoor':
                            V_x += self.door_size
                            V_y -= self.door_size * math.tan(math.radians(angle))
                            V_offset = self.find_offset(V_y, ray_number, angle, tile, 'v')
                            if V_offset < 0:
                               V_hit = False
                               V_x -= self.door_size
                               V_y += self.door_size * math.tan(math.radians(angle))
                        else:
                            V_offset = self.find_offset(V_y, ray_number, angle, tile, 'v')
                            
                    elif (V_x == tile.rect.right and V_y >= tile.rect.topright[1] and V_y <= tile.rect.bottomright[1]) and player_rect.centerx > tile.rect.right:
                        V_hit = True
                        V_texture_id = tile.ID
                        self.current_vtile = tile

                        if tile.type == 'vdoor':
                            V_x -= self.door_size
                            V_y += self.door_size * math.tan(math.radians(angle))
                            V_offset = self.find_offset(V_y, ray_number, angle, tile, 'v')
                            if V_offset < 0:
                               V_hit = False
                               V_x += self.door_size
                               V_y -= self.door_size * math.tan(math.radians(angle))
                        else:
                            V_offset = self.find_offset(V_y, ray_number, angle, tile, 'v')
                               
            #Extend actual ray
            if not H_hit:
                if angle < 180:
                    H_y -= self.tile_size
                else:
                    H_y += self.tile_size
                if angle >= 180:
                    H_x -= self.tile_size / math.tan(math.radians(angle))
                else:
                    H_x += self.tile_size / math.tan(math.radians(angle))                

            if not V_hit:
                if angle > 270 or angle < 90: # ->
                    V_x += self.tile_size
                else:
                    V_x -= self.tile_size
                if angle >= 270 or angle < 90: # <-
                    V_y -= self.tile_size * math.tan(math.radians(angle))
                else:
                    V_y += self.tile_size * math.tan(math.radians(angle))


        if V_hit and H_hit:
            H_hit, V_hit = False, False
            if H_distance < V_distance:
                end_pos = (H_x, H_y)
                other_pos = (V_x, V_y)
                texture_id = H_texture_id
                tile_len = H_distance
                offset = H_offset
                current_tile = self.current_htile
                H_hit = True
            else:
                end_pos = (V_x, V_y)
                other_pos = (H_x, H_y)
                texture_id = V_texture_id
                tile_len = V_distance
                offset = V_offset
                current_tile = self.current_vtile
                V_hit = True

        elif H_hit and not V_hit:
            end_pos = (H_x, H_y)
            other_pos = (V_x, V_y)
            texture_id = H_texture_id
            tile_len = H_distance
            offset = H_offset
            current_tile = self.current_htile

        elif V_hit and not H_hit:
            end_pos = (V_x, V_y)
            other_pos = (H_x, H_y)
            texture_id = V_texture_id
            tile_len = V_distance
            offset = V_offset
            current_tile = self.current_vtile

        else:
            end_pos = (SETTINGS.player_rect[0], SETTINGS.player_rect[1])
            other_pos = end_pos
            texture = None
            texture_id = None
            tile_len = None
            offset = 0
            current_tile = None

        if offset == SETTINGS.tile_size - 1 and passed_offset is not None:
            offset = passed_offset

        if V_hit:
            vh = 'v'
        else:
            vh = 'h'
            
        #Mode
        return self.control(end_pos, other_pos, ray_number, tile_len, player_rect, texture_id, offset, current_tile, vh)

    def get_ray_origin_for_player_position(self, angle, player_rect):
        # Horizontal
        if angle < 180:
            H_y = int(player_rect.center[1] / self.tile_size) * self.tile_size
        else:
            H_y = int(player_rect.center[1] / self.tile_size) * self.tile_size + self.tile_size

        # Vertical
        if angle > 270 or angle < 90:
            V_x = int(player_rect.center[0] / self.tile_size) * self.tile_size + self.tile_size
        else:
            V_x = int(player_rect.center[0] / self.tile_size) * self.tile_size

        return H_y, V_x

    def get_ray_origin_for_angle(self, V_x, H_y, angle, player_rect):
        H_x = player_rect.center[0] + (player_rect.center[1] - H_y) / math.tan(math.radians(angle))
        V_y = player_rect.center[1] + (player_rect.center[0] - V_x) * math.tan(math.radians(angle))
        return H_x, V_y

    def get_ray_origin(self, angle, player_rect):
        H_y, V_x = self.get_ray_origin_for_player_position(angle, player_rect)
        H_x, V_y = self.get_ray_origin_for_angle(V_x, H_y, angle, player_rect)
        return H_x, H_y, V_x, V_y

    def control(self, end_pos, other_pos, ray_number, tile_len, player_rect, texture_id, offset, current_tile, vh):
        if SETTINGS.mode == 1:
            if tile_len:
                wall_dist = tile_len * math.cos(math.radians(self.beta))
            else:
                wall_dist = None

            return self.render_screen(ray_number, wall_dist, texture_id, int(offset), current_tile, vh, end_pos, other_pos)

        else:
            self.draw_line(player_rect, end_pos)
            

    def render_screen(self, ray_number, wall_dist, texture_id, offset, current_tile, vh, end_pos, other_pos):
        if wall_dist:
            wall_height = int((self.tile_size / wall_dist) * (360 / math.tan(math.radians(SETTINGS.fov * 0.8))))
            texture = SETTINGS.tile_texture[texture_id]

            new_slice = Slice(
                tile_id = texture_id,
                location = (texture.slices[offset], 0),
                vh = vh,
                pos = end_pos,
                ray_number = ray_number,
                wall_width = self.wall_width,
                distance = wall_dist,
                height = wall_height,
                other_pos = other_pos,
                offset = offset
            )


        else:
            return None
            
        #Middle ray info
        if ray_number == int(self.res/2):
            SETTINGS.middle_slice_len = wall_dist
            SETTINGS.middle_slice = current_tile
            SETTINGS.middle_ray_pos = end_pos

        return new_slice
            

    def draw_line(self, player_rect, end_pos):
        SETTINGS.raylines.append((player_rect.center, end_pos))


