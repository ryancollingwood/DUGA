 #This is the player script. This is where the movement and collision detection of the player is.

import SETTINGS
import EFFECTS
import INVENTORY
import SOUND
import pygame
import math
import os

import consts.colours
import gamestate.rendering
import consts.player
import consts.geom
import gamedata.npcs
import gamestate.inventory
import gamestate.player


class Player:

    def __init__(self, pos):
        self.max_speed = consts.player.player_speed
        self.speed = 0
        self.angle = consts.player.player_angle
        self.health = gamestate.player.player_health

        self.real_x = pos[0]
        self.real_y = pos[1]

        self.color = consts.colours.BLUE
        self.sprite = pygame.Surface([consts.geom.tile_size / 12, consts.geom.tile_size / 12])
        self.sprite.fill(self.color)
        self.rect = self.sprite.get_rect()
        self.rect.x = self.real_x
        self.rect.y = self.real_y
        gamestate.player.player_rect = self.rect
        self.last_pos_tile = None

        self.mouse = pygame.mouse
        self.sensitivity = consts.player.sensitivity
        self.gun = 0
        self.gunsprites_aim = []
        self.gunsprites_shoot = []

        gamestate.player.player = self
        self.collide_list = SETTINGS.all_solid_tiles + gamedata.npcs.npc_list
        self.update_collide_list = False
        self.solid = True
        self.dead = False
        self.last_call = 0
        self.type = 'player'
        self.hurt_sound = pygame.mixer.Sound(os.path.join('sounds', 'other', 'damage.ogg'))
        self.change_level = pygame.mixer.Sound(os.path.join('sounds', 'other', 'next_level.ogg'))

        self.current_level = SETTINGS.current_level

        #input variables
        self.mouse2 = 0
        self.inventory = 0
        self.esc_pressed = False
        self.dont_open_menu = False


    def direction(self, offset, distance):
        if distance == 0:
            direction = [math.cos(math.radians(self.angle + offset)), -math.sin(math.radians(self.angle + offset))]
        else:
            direction = [(math.cos(math.radians(self.angle + offset))) * distance, (-math.sin(math.radians(self.angle + offset))) * distance]
        return direction

    def control(self, canvas):
        #Make sure the collide list is complete
        if len(self.collide_list) != len(SETTINGS.all_solid_tiles + gamedata.npcs.npc_list):
            self.collide_list = SETTINGS.all_solid_tiles + gamedata.npcs.npc_list
        elif self.current_level != SETTINGS.current_level:
            self.collide_list = SETTINGS.all_solid_tiles + gamedata.npcs.npc_list
            self.current_level = SETTINGS.current_level
        elif self.update_collide_list:
            self.collide_list = SETTINGS.all_solid_tiles + gamedata.npcs.npc_list
            self.update_collide_list = False

        #Update health
        if self.health != gamestate.player.player_health and gamestate.player.player_states['heal']:
            self.health = gamestate.player.player_health

        key = pygame.key.get_pressed()

        #Movement controls (WASD)
        if not gamestate.player.player_states['dead']:
            #Inventory open
            if not gamestate.player.player_states['invopen']:

                if gamestate.player.aiming:
                    self.sensitivity = consts.player.sensitivity / 3
                    self.max_speed = consts.player.player_speed / 3
                    if self.speed > self.max_speed:
                        self.speed = self.max_speed
                else:
                    self.sensitivity = consts.player.sensitivity
                    self.max_speed = consts.player.player_speed

                if key[pygame.K_a] or key[pygame.K_d] or key[pygame.K_w] or key[pygame.K_s]:
                    if self.speed < self.max_speed:
                        self.speed += 50
                        if self.speed > self.max_speed:
                            self.speed = self.max_speed

                else:
                    if self.speed > 0:
                        if self.last_call == 0:
                            self.move(self.direction(90, self.speed * 0.8))
                        elif self.last_call == 1:
                            self.move(self.direction(-90, self.speed * 0.8))
                        elif self.last_call == 2:
                            self.move(self.direction(0, self.speed))
                        elif self.last_call == 3:
                            self.move(self.direction(0, -self.speed * 0.5))

                        self.speed -= 80

                        if self.speed < 1:
                            self.speed = 0

                if key[pygame.K_a]:
                    self.move(self.direction(90, self.speed * 0.8))
                    self.last_call = 0
                if key[pygame.K_d]:
                    self.move(self.direction(-90, self.speed * 0.8))
                    self.last_call = 1
                if key[pygame.K_w]:
                    self.move(self.direction(0, self.speed))
                    self.last_call = 2
                if key[pygame.K_s]:
                    self.move(self.direction(0, -self.speed * 0.5))
                    self.last_call = 3

                gamestate.player.player_states['cspeed'] = self.speed


        #Shoot gun (Mouse input)
                if pygame.mouse.get_pressed()[2] and self.mouse2 < 1:
                    gamestate.player.mouse2_btn_active = True
                    self.mouse2 += 1
                elif self.mouse2 >= 1:
                    gamestate.player.mouse2_btn_active = False
                if not pygame.mouse.get_pressed()[2]:
                    self.mouse2 = 0

                if pygame.mouse.get_pressed()[0] and not gamestate.player.player_states['dead']:
                    gamestate.player.mouse_btn_active = True
                else:
                    gamestate.player.mouse_btn_active = False

                if key[pygame.K_r]:
                    gamestate.player.reload_key_active = True
                else:
                    gamestate.player.reload_key_active = False

        #Change gun
                if key[pygame.K_1] and gamestate.inventory.held_weapons['primary']:
                    gamestate.inventory.next_gun = gamestate.inventory.held_weapons['primary']
                elif key[pygame.K_2] and gamestate.inventory.held_weapons['secondary']:
                    gamestate.inventory.next_gun = gamestate.inventory.held_weapons['secondary']
                elif key[pygame.K_3] and gamestate.inventory.held_weapons['melee']:
                    gamestate.inventory.next_gun = gamestate.inventory.held_weapons['melee']

        #Keep angle in place
                if self.angle >= 360:
                    self.angle = 0
                elif self.angle < 0:
                    self.angle = 359

        #Interact
                if key[pygame.K_e]:
                    if gamestate.rendering.middle_slice:
                        if gamestate.rendering.middle_slice_len <= consts.geom.tile_size *1.5 and (
                                gamestate.rendering.middle_slice.type == 'vdoor' or gamestate.rendering.middle_slice.type == 'hdoor'):
                            gamestate.rendering.middle_slice.sesam_luk_dig_op()
                        elif gamestate.rendering.middle_slice_len <= consts.geom.tile_size and gamestate.rendering.middle_slice.type == 'end' and not gamestate.player.player_states['fade']:
                            gamestate.player.player_states['fade'] = True
                            SETTINGS.changing_level = True
                            SOUND.play_sound(self.change_level, 0)



                madd = self.mouse.get_rel()[0] * self.sensitivity
                if madd > 38:
                    madd = 38
                elif madd < -38:
                    madd = -38
                self.angle -= madd
                consts.player.player_angle = self.angle

        #Open inventory
            if key[pygame.K_i] and self.inventory < 1:
                if gamestate.player.player_states['invopen']:
                    gamestate.player.player_states['invopen'] = False
                    gamestate.inventory.inv_strings_updated = False
                else:
                    gamestate.player.player_states['invopen'] = True

                self.inventory += 1
            elif not key[pygame.K_i]:
                self.inventory = 0

        #Use escape to close inventory
            if key[pygame.K_ESCAPE] and gamestate.player.player_states['invopen']:
                gamestate.player.player_states['invopen'] = False
                gamestate.inventory.inv_strings_updated = False
                self.dont_open_menu = True

            elif not key[pygame.K_ESCAPE] and not gamestate.player.player_states['invopen']:
                self.dont_open_menu = False

        #Show menu
            if key[pygame.K_ESCAPE] and not self.dont_open_menu:
                self.esc_pressed = True

            elif self.esc_pressed and not self.dont_open_menu:
                SETTINGS.menu_showing = True
                self.esc_pressed = False

        #Is the player dead or taking damage?
        if self.health > gamestate.player.player_health:
            SETTINGS.statistics['last dtaken'] += (self.health - gamestate.player.player_health)
            self.health = gamestate.player.player_health
            gamestate.player.player_states['hurt'] = True
            SOUND.play_sound(self.hurt_sound, 0)
        if gamestate.player.player_health <= 0 and not SETTINGS.godmode:
            self.dead = True
            gamestate.player.player_states['dead'] = True
        if gamestate.player.player_health < 0:
            gamestate.player.player_health = 0


        if SETTINGS.menu_showing or gamestate.player.player_states['invopen']:
            pygame.event.set_grab(False)
            self.mouse.set_visible(True)
    #     elif key[pygame.K_q]:
    #         pygame.event.set_grab(True)
    #         self.mouse.set_visible(False)
        else:
            pygame.event.set_grab(True)
            self.mouse.set_visible(False)

    ##        #Change to map view (DEV)
    ##        if key[pygame.K_m]:
    ##            SETTINGS.switch_mode = True
    ##
    ##
    ##        #Change FOV (DEV)
    ##        if key[pygame.K_UP]:
    ##            SETTINGS.fov += 2
    ##        elif key[pygame.K_DOWN]:
    ##            SETTINGS.fov -= 2
    ##
    ##        #Screen shake (DEV)
    ##        if key[pygame.K_p]:
    ##            SETTINGS.screen_shake = 20
    ##            SETTINGS.player_hurt = True

    #======================================================

    def move(self, pos):
        if SETTINGS.cfps > 5:
            if pos[0] != 0:
                self.update(pos[0], 0)
            if pos[1] != 0:
                self.update(0, pos[1])

    def update(self, x, y):
        self.real_x += x * SETTINGS.dt
        self.real_y += y * SETTINGS.dt
        self.rect.x = self.real_x
        self.rect.y = self.real_y
        gamestate.player.player_rect = self.rect
        tile_hit_list = pygame.sprite.spritecollide(self, self.collide_list, False)

        #Actually there are not only tiles in the list. NPCs as well.
        for tile in tile_hit_list:
            if tile.solid:
                if x > 0:
                    self.rect.right = tile.rect.left
                    self.real_x = self.rect.x
                if x < 0:
                    self.rect.left = tile.rect.right
                    self.real_x = self.rect.x
                if y > 0:
                    self.rect.bottom = tile.rect.top
                    self.real_y = self.rect.y
                if y < 0:
                    self.rect.top = tile.rect.bottom
                    self.real_y = self.rect.y

        gamestate.player.player_map_pos = [int(self.rect.centerx / consts.geom.tile_size), int(self.rect.centery / consts.geom.tile_size)]

        #check if player is out of bounds and teleport them back.
        generator_check_list = [x for x in SETTINGS.walkable_area if x.map_pos == gamestate.player.player_map_pos]
        if generator_check_list:
            pos = generator_check_list[0].map_pos
        else:
            pos = []

        check_list = SETTINGS.walkable_area + SETTINGS.all_solid_tiles
        out_generator = [x for x in check_list if x.map_pos == gamestate.player.player_map_pos]
        if out_generator:
            pos2 = out_generator[0].map_pos
        else:
            pos2 = []


        if gamestate.player.player_map_pos == pos:
            gamestate.player.last_player_map_pos = gamestate.player.player_map_pos
            self.last_pos_tile = generator_check_list[0]

        elif gamestate.player.player_map_pos != pos2 and gamestate.player.last_player_map_pos:
            if self.last_pos_tile:
                gamestate.player.player_map_pos = gamestate.player.last_player_map_pos
                self.rect.center = self.last_pos_tile.rect.center
                gamestate.player.player_rect = self.rect
                self.real_x = self.rect.x
                self.real_y = self.rect.y


    def draw(self, canvas):
        pointer = self.direction(0, 10)
        p1 = pointer[0] + self.rect.center[0]
        p2 = pointer[1] + self.rect.center[1]
        canvas.blit(self.sprite, (self.rect.x/4, self.rect.y/4))
        pygame.draw.line(canvas, self.color, (self.rect.center[0]/4, self.rect.center[1]/4), (p1/4, p2/4))

