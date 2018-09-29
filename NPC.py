import SETTINGS
import SPRITES
import PATHFINDING
import ITEMS
import SOUND
import os
import random
import math
import pygame
#stats format in bottom of script
#pos is in tiles, face in degrees, frame_interval is seconds between frames, speed is pixels/second
import consts.raycast
from consts import npc_state
from consts import geom
import consts.tile
import gamedata.npcs
import gamedata.tiles
import gamestate.inventory
import gamestate.items
import gamestate.npcs
import gamestate.player
import gamestate.sprites


class Npc:

    def __init__(self, stats, sounds, texture):
        #Technical settings
        self.stats = stats #Used for creating new NPCs
        self.sounds = sounds
        self.ID = stats['id']
        self.map_pos = stats['pos']
        self.pos = [self.map_pos[0] * consts.tile.TILE_SIZE, self.map_pos[1] * consts.tile.TILE_SIZE]
        self.face = stats['face']
        self.frame_interval = stats['spf']
        self.dda_list = SETTINGS.walkable_area + [x for x in SETTINGS.all_solid_tiles if x.type == 'sprite']

        #Visual and rect settings
        self.rect = pygame.Rect((self.pos[0], self.pos[1]), (consts.tile.TILE_SIZE / 3, consts.tile.TILE_SIZE / 3))
        self.rect.center = (self.pos[0] + consts.tile.TILE_SIZE / 2, self.pos[1] + consts.tile.TILE_SIZE / 2)
        self.real_x = self.rect.x
        self.real_y = self.rect.y

        #Initialise boring variables
        self.timer = 0
        self.idle_timer = 0
        self.die_animation = False
        self.running_animation = None
        self.add = 0
        self.dist_from_player = None
        self.collide_list = SETTINGS.all_solid_tiles + gamestate.npcs.npc_list
        self.solid = True
        self.side = None
        self.in_canvas = False
        self.path = []
        self.path_progress = 0
        self.attack_move = False
        self.atckchance = 5
        self.movechance = 10
        self.knockback = 0
        self.postheta = 0
        self.mein_leben = False
        self.type = 'npc'
        self.player_touched = False

        #NPC Characteristics
        self.health = stats['health']    
        self.speed = stats['speed']
        self.OG_speed = self.speed
        self.mind = stats['mind']
        self.state = stats['state']
        self.OG_state = self.state
        self.atcktype = stats['atcktype']
        self.name = stats['name']
        
        if stats['dmg'] != 3.1415:
            self.dmg = stats['dmg']
        else:
            self.dmg = random.choice([1,2,3])
        self.atckrate = stats['atckrate']

        self.range = 5

        #make first level easier
        if SETTINGS.current_level == 0 and SETTINGS.levels_list == SETTINGS.glevels_list:
            self.health = int(self.health * 0.8)
            self.dmg = int(self.dmg * 0.8)
            
        #Make late levels harder >:)
        elif SETTINGS.current_level > 4 and SETTINGS.levels_list == SETTINGS.glevels_list:
            self.health += int(SETTINGS.current_level / 3)
            self.dmg += int(SETTINGS.current_level / 5)

        #Make NPC stronger if player is doing well
        if gamestate.player.player_health >= 90 or gamestate.player.player_armor >= 90:
            self.dmg += 2

        #Give NPC more health if player has lots of ammo - phew, long line.
        if gamestate.inventory.held_weapons['primary'] and gamestate.inventory.held_ammo[gamestate.inventory.held_weapons['primary'].ammo_type] >= gamestate.inventory.max_ammo[
            gamestate.inventory.held_weapons['primary'].ammo_type]:
            self.health = int(self.health * 1.5)

        #Npc actions
        self.dead = False
        self.moving = False
        self.attacking = False
        self.hurting = False
        self.player_in_view = False

        #Textures and animations
        self.texture_path = texture # Used for creating new NPCS
        self.texture = pygame.image.load(texture).convert_alpha()
        self.texturerect = self.texture.get_rect()
        
        self.stand_texture = [self.texture.subsurface(0,0,64,128).convert_alpha(), self.texture.subsurface(64,0,64,128).convert_alpha(), self.texture.subsurface(128,0,64,128).convert_alpha(), self.texture.subsurface(192,0,64,128).convert_alpha(), self.texture.subsurface(256,0,64,128).convert_alpha(), self.texture.subsurface(320,0,64,128).convert_alpha(), self.texture.subsurface(384,0,64,128).convert_alpha(), self.texture.subsurface(448,0,64,128).convert_alpha()]
        self.front_texture = [self.texture.subsurface(0,128,64,128).convert_alpha(), self.texture.subsurface(64,128,64,128).convert_alpha(), self.texture.subsurface(128,128,64,128).convert_alpha(), self.texture.subsurface(192,128,64,128).convert_alpha(), self.texture.subsurface(256,128,64,128).convert_alpha(), self.texture.subsurface(320,128,64,128).convert_alpha(), self.texture.subsurface(384,128,64,128).convert_alpha(), self.texture.subsurface(448,128,64,128).convert_alpha(), self.texture.subsurface(512,128,64,128).convert_alpha(), self.texture.subsurface(576,128,64,128).convert_alpha()]
        self.frontright_texture = [self.texture.subsurface(0,256,64,128).convert_alpha(), self.texture.subsurface(64,256,64,128).convert_alpha(), self.texture.subsurface(128,256,64,128).convert_alpha(), self.texture.subsurface(192,256,64,128).convert_alpha(), self.texture.subsurface(256,256,64,128).convert_alpha(), self.texture.subsurface(320,256,64,128).convert_alpha(), self.texture.subsurface(384,256,64,128).convert_alpha(), self.texture.subsurface(448,256,64,128).convert_alpha(), self.texture.subsurface(512,256,64,128).convert_alpha(), self.texture.subsurface(576,256,64,128).convert_alpha()]
        self.right_texture = [self.texture.subsurface(0,384,64,128).convert_alpha(), self.texture.subsurface(64,384,64,128).convert_alpha(), self.texture.subsurface(128,384,64,128).convert_alpha(), self.texture.subsurface(192,384,64,128).convert_alpha(), self.texture.subsurface(256,384,64,128).convert_alpha(), self.texture.subsurface(320,384,64,128).convert_alpha(), self.texture.subsurface(384,384,64,128).convert_alpha(), self.texture.subsurface(448,384,64,128).convert_alpha(), self.texture.subsurface(512,384,64,128).convert_alpha(), self.texture.subsurface(576,384,64,128).convert_alpha()]
        self.backright_texture = [self.texture.subsurface(0,512,64,128).convert_alpha(), self.texture.subsurface(64,512,64,128).convert_alpha(), self.texture.subsurface(128,512,64,128).convert_alpha(), self.texture.subsurface(192,512,64,128).convert_alpha(), self.texture.subsurface(256,512,64,128).convert_alpha(), self.texture.subsurface(320,512,64,128).convert_alpha(), self.texture.subsurface(384,512,64,128).convert_alpha(), self.texture.subsurface(448,512,64,128).convert_alpha(), self.texture.subsurface(512,512,64,128).convert_alpha(), self.texture.subsurface(576,512,64,128).convert_alpha()]
        self.back_texture = [self.texture.subsurface(0,640,64,128).convert_alpha(), self.texture.subsurface(64,640,64,128).convert_alpha(), self.texture.subsurface(128,640,64,128).convert_alpha(), self.texture.subsurface(192,640,64,128).convert_alpha(), self.texture.subsurface(256,640,64,128).convert_alpha(), self.texture.subsurface(320,640,64,128).convert_alpha(), self.texture.subsurface(384,640,64,128).convert_alpha(), self.texture.subsurface(448,640,64,128).convert_alpha(), self.texture.subsurface(512,640,64,128).convert_alpha(), self.texture.subsurface(576,640,64,128).convert_alpha()]
        
        self.backleft_texture = []
        self.left_texture = []
        self.frontleft_texture = []

        for frame in self.backright_texture:
            self.backleft_texture.append(pygame.transform.flip(frame, True, False))
        for frame in self.right_texture:
            self.left_texture.append(pygame.transform.flip(frame, True, False))
        for frame in self.frontright_texture:
            self.frontleft_texture.append(pygame.transform.flip(frame, True, False))

        self.die_texture = [self.texture.subsurface(0,768,64,128).convert_alpha(), self.texture.subsurface(64,768,64,128).convert_alpha(), self.texture.subsurface(128,768,64,128).convert_alpha(), self.texture.subsurface(192,768,64,128).convert_alpha(), self.texture.subsurface(256,768,64,128).convert_alpha(), self.texture.subsurface(320,768,64,128).convert_alpha(), self.texture.subsurface(384,768,64,128).convert_alpha(), self.texture.subsurface(448,768,64,128).convert_alpha(), self.texture.subsurface(512,768,64,128).convert_alpha(), self.texture.subsurface(576,768,64,128).convert_alpha(), self.texture.subsurface(640,768,64,128).convert_alpha()]
        self.hit_texture = [self.texture.subsurface(0,896,64,128).convert_alpha(), self.texture.subsurface(64,896,64,128).convert_alpha(), self.texture.subsurface(128,896,64,128).convert_alpha(), self.texture.subsurface(192,896,64,128).convert_alpha(), self.texture.subsurface(256,896,64,128).convert_alpha(), self.texture.subsurface(320,896,64,128).convert_alpha()]
        self.hurt_texture = [self.die_texture[0]]
        self.current_frame = 1
        self.update_timer = 0

        #Creating the sprite rect is awful, I know. Keeps it from entering walls.
        self.sprite = SPRITES.Sprite(self.front_texture[1], self.ID, [self.rect.centerx - int(
            consts.tile.TILE_SIZE / 12), self.rect.centery - int(consts.tile.TILE_SIZE / 10)], 'npc', self)

        #The position in SETTINGS.all_sprites of this NPC
        self.num = len(gamestate.sprites.all_sprites) - 1

    def think(self):
        self.map_pos = [int(self.rect.centerx / consts.tile.TILE_SIZE), int(self.rect.centery / consts.tile.TILE_SIZE)]
        if self.state == npc_state.ATTACKING or self.state == npc_state.FLEEING:
            self.speed = self.OG_speed * 2

        if not self.dead:
            self.timer += SETTINGS.dt
            self.update_timer += SETTINGS.dt
            if self.update_timer >= 2:
                self.update_timer = 0
            
        if not self.dead and self.health > 0 and not gamestate.player.player_states['dead']:
            self.render()

            if self.dist_from_player and self.dist_from_player <= consts.raycast.render * consts.tile.TILE_SIZE * 1.2:

                #PASSIVE
                if self.mind == 'passive':
                    # TODO alternate between idle and patroll
                    pass

                #HOSTILE
                elif self.mind == 'hostile':
                    if self.state != npc_state.ATTACKING and self.touched_by_player():
                        self.react_to_player(npc_state.ATTACKING)
                    else:
                        self.look_for_player(npc_state.ATTACKING)

                #SHY
                elif self.mind == 'shy':
                    if self.state == npc_state.IDLE:
                        self.look_for_player(npc_state.FLEEING)
                    elif self.state == npc_state.PATROLLING:
                        if self.state != npc_state.ATTACKING and self.touched_by_player():
                            self.react_to_player(npc_state.ATTACKING)
                        else:
                            self.look_for_player(npc_state.FLEEING)
                    else:
                        if self.state != npc_state.FLEEING and self.touched_by_player():
                            self.react_to_player(npc_state.FLEEING)

            # Act upon state
            if self.state == npc_state.ATTACKING:
                self.attack()
            elif self.state == npc_state.PATROLLING:
                self.move()
            elif self.state == npc_state.FLEEING:
                self.move()
            elif self.state == npc_state.IDLE:
                self.idle()

            #Run animations
            if self.hurting:
                self.animate('hurting')

                # if npc takes damage and is not fleeing
                # retaliate and fight back
                if self.state != npc_state.FLEEING:
                    self.state = npc_state.ATTACKING

            elif self.moving:
                self.animate('walking')

        if gamestate.player.player_states['dead']:
            self.face += 10
            if self.face >= 360:
                self.face -= 360
            self.render()
            
        elif self.health <= 0 and not self.dead:
            self.animate('dying')
            self.render()

    def look_for_player(self, state_if_spotted):
        if self.dead:
            return False

        if self.attacking:
            return True

        if not SETTINGS.ignore_player:
            if self.player_in_view:
                if self.detect_player():
                    self.react_to_player(state_if_spotted)
                    return True
                else:
                    print("player_in_view but didn't detect", self.mind, self.state)
        return False

    def react_to_player(self, new_state):
        self.path = []
        SOUND.play_sound(self.sounds['spot'], self.dist_from_player)
        self.state = new_state

        # TODO wake up friends, again perception checks needed
        max_allies = 3
        woken_allies = 0
        for npc in gamestate.npcs.npc_list:
            if npc.mind == "hostile":
                if npc.dist_from_player <= consts.tile.TILE_SIZE * 3:
                    # move to a method hunt_for_player
                    npc.path = PATHFINDING.pathfind(npc.map_pos, gamestate.player.player_map_pos)
                    npc.state = npc_state.ATTACKING
                    woken_allies += 1
                    if woken_allies >= max_allies:
                        break


    def touched_by_player(self):
        # TODO perhaps some perception modifier
        # depending on the state/mind?
        perception_distance = consts.tile.TILE_SIZE

        # using sides as render has calculated this for us
        if self.side == 'backright' or self.side == 'backleft':
            perception_distance = (consts.tile.TILE_SIZE / 2)
        elif self.side == 'back':
            # if npc back is shown to player can sneak right up
            perception_distance = (consts.tile.TILE_SIZE / 3)

        something_touched_me = self.dist_from_player <= perception_distance and not SETTINGS.ignore_player
        if something_touched_me:
            print("something_touched_me!", self.state, self.mind)
            pass
        else:
            # debug purposes
            if self.dist_from_player <= (consts.tile.TILE_SIZE * 2):
                print("nothing touched_me!", self.state, self.mind)
                pass

        self.player_touched = something_touched_me

        return something_touched_me

    def render(self):
        '''== Draw the NPC =='''
        if self.dead:
            self.solid = False
            
        xpos = gamestate.player.player_rect.centerx - self.rect.centerx
        ypos = gamestate.player.player_rect.centery - self.rect.centery
        
        self.dist_from_player = math.sqrt(xpos * xpos + ypos * ypos)
        
        if self.dist_from_player <= consts.raycast.render * consts.tile.TILE_SIZE:
            theta = math.atan2(-ypos, xpos) % (2*math.pi)
            theta = math.degrees(theta)
            self.postheta = theta
            theta -= self.face
            if theta < 0:
                theta += 360
            elif theta > 360:
                theta -= 360

            self.theta = theta

            self.sprite.update_pos([self.rect.x, self.rect.y])

            #What side is the NPC facing? (or not self.side is to make sure it finds the right angle from initialization) 
            if theta <= 22.5 or theta >= 337.5:
                self.player_in_view = True
                if (self.side != 'front' and not self.dead and not self.hurting and not self.attacking and self.in_canvas) or not self.side:
                    if self.moving:
                        self.sprite.texture = self.front_texture[self.current_frame]
                    else:
                        self.sprite.texture = self.stand_texture[0]
                self.side = 'front'

            elif theta <= 67.5 and theta >= 22.5:
                self.player_in_view = True
                if (self.side != 'frontleft' and not self.dead and not self.hurting and not self.attacking and self.in_canvas) or not self.side:
                    if self.moving:
                        self.sprite.texture = self.frontleft_texture[self.current_frame]
                    else:
                        self.sprite.texture = self.stand_texture[7]
                self.side = 'frontleft'
                
            elif theta <= 112.5 and theta >= 67.5:
                self.player_in_view = False
                if (self.side != 'left' and not self.dead and not self.hurting and not self.attacking and self.in_canvas) or not self.side:
                    if self.moving:
                        self.sprite.texture = self.left_texture[self.current_frame]
                    else:
                        self.sprite.texture = self.stand_texture[6]
                self.side = 'left'

            elif theta <= 157.5 and theta >= 112.5:
                self.player_in_view = False
                if (self.side != 'backleft' and not self.dead and not self.hurting and not self.attacking and self.in_canvas) or not self.side:
                    if self.moving:
                        self.sprite.texture = self.backleft_texture[self.current_frame]
                    else:
                        self.sprite.texture = self.stand_texture[5]
                self.side = 'backleft'
                
            elif theta <= 202.5 and theta >= 157.5:
                self.player_in_view = False
                if (self.side != 'back' and not self.dead and not self.hurting and not self.attacking and self.in_canvas) or not self.side:
                    if self.moving:
                        self.sprite.texture = self.back_texture[self.current_frame]
                    else:
                        self.sprite.texture = self.stand_texture[4]
                self.side = 'back'

            elif theta <= 247.5 and theta >= 202.5:
                self.player_in_view = False
                if (self.side != 'backright' and not self.dead and not self.hurting and not self.attacking and self.in_canvas) or not self.side:
                    if self.moving:
                        self.sprite.texture = self.backright_texture[self.current_frame]
                    else:
                        self.sprite.texture = self.stand_texture[3]
                self.side = 'backright'
                
            elif theta <= 292.5 and theta >= 247.5:
                self.player_in_view = False
                if (self.side != 'right' and not self.dead and not self.hurting and not self.attacking and self.in_canvas) or not self.side:
                    if self.moving:
                        self.sprite.texture = self.right_texture[self.current_frame]
                    else:
                        self.sprite.texture = self.stand_texture[2]
                self.side = 'right'

            elif theta <= 337.5 and theta >= 292.5:
                self.player_in_view = True
                if (self.side != 'frontright' and not self.dead and not self.hurting and not self.attacking and self.in_canvas) or not self.side:
                    if self.moving:
                        self.sprite.texture = self.frontright_texture[self.current_frame]
                    else:
                        self.sprite.texture = self.stand_texture[1]
                self.side = 'frontright'

        if gamestate.sprites.all_sprites[self.num] != self.sprite:
            gamestate.sprites.all_sprites[self.num] = self.sprite

        #Find out what x and y coordinates would change
        if self.face == geom.DEGREES_90:
            self.front_tile = (0, -1)
        elif self.face == geom.DEGREES_180:
            self.front_tile = (-1, 0)
        elif self.face == geom.DEGREES_270:
            self.front_tile = (0, 1)
        elif self.face == geom.DEGREES_0 or self.face == geom.DEGREES_360:
            self.front_tile = (1, 0)

    @staticmethod
    def round_up(a):
        return int(a + 0.5)            

    def detect_player(self):

        # if the player touched us we've detected
        if self.player_touched:
            self.player_touched = False
            return True

        if self.attacking:
            return True

        '''== Is player visible from NPC position? ==\ndetect_player(self) -> boolean'''
        own_tile = self.map_pos
        #front_tile = [own_tile[0] + self.front_tile[0], own_tile[1] + self.front_tile[1]]
        player_tile = gamestate.player.player_map_pos

        #DDA Algorithm
        x1,y1 = own_tile[0], own_tile[1]
        x2,y2 = player_tile[0], player_tile[1]

        #If the coords are negative, start from player instead of NPC
        if x1 > x2 or (x1 == x2 and y1 > y2):
            temp1,temp2 = x1,y1
            x1,y1 = x2,y2
            x2,y2 = temp1,temp2

        x,y = x1, y1
        dx = abs(x2-x1)
        dy = abs(y2-y1)
        length = dx if dx > dy else dy
        #Make sure, you won't divide by 0
        if length == 0:
            length = 0.001

        xinc = (x2-x1)/float(length)
        yinc = (y2-y1)/float(length)
        mapx = self.round_up(x)
        mapy = self.round_up(y)

        #Extend DDA algorithm
        for i in range(int(length)):
            if i > consts.raycast.render:
                break
            x += xinc
            y += yinc
            mapx = self.round_up(x)
            mapy = self.round_up(y)
            
            #If line of sight hits a wall
            next_wall = [tile for tile in self.dda_list if tile.map_pos == [mapx, mapy]]
            
            if not next_wall:
                break
            else:
                next_wall = next_wall[0]
            
            if gamedata.tiles.tile_visible[next_wall.ID]:
                if next_wall.type != consts.tile.HORIZONTAL_DOOR and next_wall.type != consts.tile.VERTICAL_DOOR:
                    break
                elif next_wall.type == consts.tile.HORIZONTAL_DOOR or next_wall.type == consts.tile.VERTICAL_DOOR:
                    if next_wall.solid:
                        break
            #if player is spotted
            if mapx == x2 and mapy == y2:
                return True

        # TODO this should also hook into some notion of NPC perception
        if self.dist_from_player <= consts.tile.TILE_SIZE * 2:
            return True

        return False

    def collide_update(self, x, y):
        #make sure the NPC doesn't walk inside stuff
        self.real_x += x * SETTINGS.dt
        self.real_y += y * SETTINGS.dt
        self.rect.x = self.real_x
        self.rect.y = self.real_y

        if self.collide_list[-1] != gamestate.player.player:
            self.collide_list.append(gamestate.player.player)
        else:
            self.collide_list[-1] = gamestate.player.player

        tile_hit_list = [s for s in self.collide_list if self.rect.colliderect(s)]
        
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

        for door in SETTINGS.all_doors:
            if door.get_dist(self.rect.center, 'npc') <= 50:
                door.sesam_luk_dig_op()
                break

    def move(self):
        #Make the NPC move according to current state.
        moving_up = False
        moving_down = False
        moving_right = False
        moving_left = False

        if self.path and self.rect.center != self.path[-1].rect.center and self.health > 0 and not self.hurting:
            self.moving = True

            #Redo path if tile is occupied by another NPC.
            if self.update_timer <= 0.5:
                for npc in gamestate.npcs.npc_list:
                    if npc.map_pos == self.path[-1].map_pos:
                        available_pos = [x for x in SETTINGS.walkable_area if abs(x.map_pos[0]-self.map_pos[0]) <= 3 and abs(x.map_pos[1]-self.map_pos[1]) <= 3]
                        self.path = PATHFINDING.pathfind(self.map_pos, random.choice(available_pos).map_pos)
                        self.path_progress = 0
                        break

            if self.rect.colliderect(self.path[self.path_progress].rect) and self.path[self.path_progress] != self.path[-1]:
                self.path_progress += 1
                
            else:
                #Move down
                if self.rect.centery < self.path[self.path_progress].rect.centery:
                    if abs(self.path[self.path_progress].rect.centery - self.rect.centery) >= self.speed * SETTINGS.dt:
                        self.collide_update(0, self.speed)
                        moving_down = True
                    else:
                        self.rect.centery = self.path[self.path_progress].rect.centery

                #Moving up
                elif self.rect.centery > self.path[self.path_progress].rect.centery:
                    if abs(self.path[self.path_progress].rect.centery - self.rect.centery) >= self.speed * SETTINGS.dt:
                        self.collide_update(0, -self.speed)
                        moving_up = True
                    else:
                        self.rect.centery = self.path[self.path_progress].rect.centery
                    
                #Move right
                if self.rect.centerx < self.path[self.path_progress].rect.centerx:
                    if abs(self.path[self.path_progress].rect.centerx - self.rect.centerx) >= self.speed * SETTINGS.dt:
                        self.collide_update(self.speed, 0)
                        moving_right = True
                    else:
                        self.rect.centerx = self.path[self.path_progress].rect.centerx

                #Move left
                elif self.rect.centerx > self.path[self.path_progress].rect.centerx:
                    if abs(self.rect.centerx - self.path[self.path_progress].rect.centerx) >= self.speed * SETTINGS.dt:
                        self.collide_update(-self.speed, 0)
                        moving_left = True
                    else:
                        self.rect.centerx = self.path[self.path_progress].rect.centerx

                if moving_up:
                    if not moving_right and not moving_left:
                        self.face = geom.DEGREES_90
                    elif moving_right:
                        self.face = geom.DEGREES_45
                    elif moving_left:
                        self.face = geom.DEGREES_135
                        
                elif moving_down:
                    if not moving_right and not moving_left:
                        self.face = geom.DEGREES_270
                    elif moving_right:
                        self.face = geom.DEGREES_315
                    elif moving_left:
                        self.face = geom.DEGREES_225

                elif moving_left:
                    self.face = geom.DEGREES_180
                    
                elif moving_right:
                    self.face = geom.DEGREES_0
                
        else:
            self.moving = False
            self.attack_move = False
            if self.timer >= self.frame_interval:
                self.path = []
                self.path_progress = 0

        if self.state == npc_state.PATROLLING:
            if self.path == []:
                if random.randint(0,3) == 3:
                    self.state = npc_state.IDLE
                    self.sprite.texture = self.stand_texture[4]
                else:
                    #Make the NPC not walk too far.
                    available_pos = [x for x in SETTINGS.walkable_area if abs(x.map_pos[0]-self.map_pos[0]) <= 3 and abs(x.map_pos[1]-self.map_pos[1]) <= 3]
                    self.path = PATHFINDING.pathfind(self.map_pos, random.choice(available_pos).map_pos)

        elif self.state == npc_state.FLEEING:
            if self.dist_from_player <= consts.tile.TILE_SIZE * 4:
                flee_pos = random.choice(SETTINGS.walkable_area)
                player_tile = [x for x in SETTINGS.walkable_area if x.map_pos == gamestate.player.player_map_pos]
                if player_tile:
                    player_tile = player_tile[0]
                else:
                    player_tile = PATHFINDING.find_near_position(gamestate.player.player_map_pos)
                    
                if self.player_in_view:
                    if self.detect_player() and player_tile:
                        if ((SETTINGS.walkable_area.index(flee_pos) < SETTINGS.walkable_area.index(player_tile) + int(SETTINGS.current_level_size[0] / 5)) or (SETTINGS.walkable_area.index(flee_pos) > SETTINGS.walkable_area.index(player_tile) - int(SETTINGS.current_level_size[0] / 5))) and self.path == []:
                            self.path_progress = 0
                            self.path = PATHFINDING.pathfind(self.map_pos, flee_pos.map_pos)

    def idle(self):
        #Make the NPC rotate randomly as it stands still.
        self.idle_timer += SETTINGS.dt
        if self.idle_timer >= 3:
            if random.randint(0,2) == 2:
                self.face += geom.DEGREES_45
            elif random.randint(0,2) == 2:
                self.face -= geom.DEGREES_45
            if self.face >= geom.DEGREES_360:
                self.face -= geom.DEGREES_360

            self.idle_timer = 0

            #Do only change to patrouling if it was that in the first place.
            if self.OG_state != npc_state.IDLE:
                if random.randint(0, 2) == 2:
                    self.state = npc_state.PATROLLING

        #Make NPC react to gunshot if close. Or just if the player is too close.
        if (self.dist_from_player <= consts.tile.TILE_SIZE * 4 and gamestate.player.mouse_btn_active and gamestate.inventory.current_gun) or self.dist_from_player <= self.rect.width:
            self.change_facing_direction()

    def attack(self):
        if self.attack_move:
            self.move()
        else:
            if self.atcktype == 'melee':
                #Move close to player and keep attacking
                if self.dist_from_player <= consts.tile.TILE_SIZE *0.7:
                    self.path = []
                    self.moving = False
                    if not self.attacking:
                        if self.timer >= self.frame_interval * self.atckrate:
                            self.attacking = True
                            self.timer = 0
                    else:
                        #Make the NPC not flinch when attacking
                        if self.hurting:
                            if random.randint(0,2) != 2 or self.attacking:
                                self.animate(npc_state.ATTACKING)
                                self.hurting = False
                                if random.randint(0,2) == 2:
                                    SOUND.play_sound(random.choice(self.sounds['damage']), self.dist_from_player)
                        else:
                            self.animate(npc_state.ATTACKING)

                else:
                    if self.dist_from_player > consts.tile.TILE_SIZE *0.7 and self.path == []:
                        self.path_progress = 0
                        self.path = PATHFINDING.pathfind(self.map_pos, gamestate.player.player_map_pos)
                        
                    elif self.path != []:
                        try:
                            if self.path[-1].map_pos != gamestate.player.player_map_pos:
                                if self.dist_from_player <= (consts.raycast.render / 2) * consts.tile.TILE_SIZE and random.randint(0, 5) == 5:
                                    self.path_progress = 0
                                    self.path = PATHFINDING.pathfind(self.map_pos, gamestate.player.player_map_pos)
                                elif random.randint(0,10) >= 8:
                                    self.path_progress = 0
                                    self.path = PATHFINDING.pathfind(self.map_pos, gamestate.player.player_map_pos)
                            else:
                                self.move()
                        except:
                            pass
                
            elif self.atcktype == 'hitscan':
                #Move somewhat close to player and change position after attacking
                if self.dist_from_player <= consts.tile.TILE_SIZE * self.range and (self.dist_from_player >= consts.tile.TILE_SIZE * 1.5 or (
                        gamestate.inventory.current_gun and gamestate.inventory.current_gun.guntype == 'melee')) and not self.attack_move:
                    self.path = []
                    self.moving = False
                    if not self.attacking:
                        if random.randint(0, self.atckchance) == 5 and self.detect_player():
                                self.attacking = True
                                self.atckchance += int(self.atckrate)
                                self.movechance = 10
                        else:
                            if random.randint(0, self.movechance) == 10:
                                move_pos = random.choice([x for x in SETTINGS.walkable_area if (x.map_pos[0] <= self.map_pos[0]+1 and x.map_pos[0] >= self.map_pos[0]-1) and (x.map_pos[1] <= self.map_pos[1]+1 and x.map_pos[1] >= self.map_pos[1]-1)])
                                self.path_progress = 0
                                self.path = PATHFINDING.pathfind(self.map_pos, move_pos.map_pos)
                                self.attacking = False
                                self.attack_move = True
                                #This variable is to make sure the NPC doesn't just walk around without attacking.
                                self.movechance += 3
                                self.atckchance = 5

                    #There is a chance the NPC will not flinch when shot while attacking
                    elif self.attacking:
                        if self.hurting:
                            if random.randint(0,5) >= 3:
                                self.animate(npc_state.ATTACKING)
                                self.hurting = False
                                if random.randint(0,2) == 2:
                                    SOUND.play_sound(random.choice(self.sounds['damage']), self.dist_from_player)
                        else:
                            self.animate(npc_state.ATTACKING)
                            
                #Move away from player if too close            
                elif self.dist_from_player < consts.tile.TILE_SIZE * 1.5 and self.health <= 6:
                    if self.rect.centerx > gamestate.player.player_rect.centerx:
                        self.collide_update(self.speed, 0)
                        self.animate('walking')
                    elif self.rect.centerx < gamestate.player.player_rect.centerx:
                        self.collide_update(-self.speed, 0)
                        self.animate('walking')
                    if self.rect.centery > gamestate.player.player_rect.centery:
                        self.collide_update(0, self.speed)
                        self.animate('walking')
                    elif self.rect.centery < gamestate.player.player_rect.centery:
                        self.collide_update(0, -self.speed)
                        self.animate('walking')
                    
                        
                else:
                    if not self.attack_move:
                        if self.dist_from_player >= consts.tile.TILE_SIZE * 2.5 and self.path == []:
                            self.path_progress = 0
                            self.path = PATHFINDING.pathfind(self.map_pos, gamestate.player.player_map_pos)

                        elif self.path != []:
                            try:
                                if self.path[-1].map_pos != gamestate.player.player_map_pos:
                                    if self.dist_from_player <= (consts.raycast.render / 2) * consts.tile.TILE_SIZE and random.randint(0, 5) == 5:
                                        self.path_progress = 0
                                        self.path = PATHFINDING.pathfind(self.map_pos, gamestate.player.player_map_pos)
                                    elif random.randint(0,10) == 10:
                                        self.path_progress = 0
                                        self.path = PATHFINDING.pathfind(self.map_pos, gamestate.player.player_map_pos)
                                else:
                                    self.move()
                            except:
                                pass

    def animate(self, animation):
        '''== Animate NPC ==\nanimation -> dying, walking, attacking, hurting'''
        if self.running_animation != animation:
            self.current_frame = 0
            self.running_animation = animation
            
        #walk animation
        if animation == 'walking':
            if self.side == 'front':
                self.sprite.texture = self.front_texture[self.current_frame]
            elif self.side == 'frontleft':
                self.sprite.texture = self.frontleft_texture[self.current_frame]
            elif self.side == 'left':
                self.sprite.texture = self.left_texture[self.current_frame]
            elif self.side == 'backleft':
                self.sprite.texture = self.backleft_texture[self.current_frame]
            elif self.side == 'back':
                self.sprite.texture = self.back_texture[self.current_frame]
            elif self.side == 'backright':
                self.sprite.texture = self.backright_texture[self.current_frame]
            elif self.side == 'right':
                self.sprite.texture = self.right_texture[self.current_frame]
            elif self.side == 'frontright':
                self.sprite.texture = self.frontright_texture[self.current_frame]

            if self.timer >= self.frame_interval:
                self.current_frame += 1
                self.timer = 0
                if self.current_frame == len(self.front_texture)-1:
                    self.current_frame = 0
        
        #die animation
        elif animation == 'dying':
            self.sprite.texture = self.die_texture[self.current_frame]
            if self.current_frame == 0 and not self.mein_leben:
                self.mein_leben = True
                SOUND.play_sound(random.choice(self.sounds['die']), self.dist_from_player)
            if self.timer >= self.frame_interval and self.current_frame < len(self.die_texture)-1:
                self.current_frame += 1
                self.timer = 0
            elif self.current_frame == len(self.die_texture)-1 and self.knockback == 0:
                self.dead = True
                self.drop_item(self.map_pos)
                SETTINGS.statistics['last enemies'] += 1
            elif self.knockback > 0:
                self.collide_update(-math.cos(math.radians(self.postheta))*self.knockback, 0)
                self.collide_update(0, math.sin(math.radians(self.postheta))*self.knockback)
                self.knockback = int(self.knockback*0.8)
                
        #hurt animation
        elif animation == 'hurting':
            self.sprite.texture = self.hurt_texture[0]
            self.moving = False
            if self.timer >= self.frame_interval*2:
                self.side = None
                self.hurting = False
                self.timer = 0
                SOUND.play_sound(random.choice(self.sounds['damage']), self.dist_from_player)

                if self.state == npc_state.IDLE or self.state == npc_state.PATROLLING or self.state == npc_state.FLEEING:
                    self.change_facing_direction()
        
        #attack animation
        elif animation == npc_state.ATTACKING:
            self.sprite.texture = self.hit_texture[self.current_frame]
            self.moving = False
            if self.timer >= self.frame_interval:
                self.current_frame += 1
                self.timer = 0
                if self.current_frame == len(self.hit_texture):
                    SOUND.play_sound(self.sounds['attack'], self.dist_from_player)
                    self.sprite.texture = self.stand_texture[0]
                    self.current_frame = 0
                    self.attacking = False
                    if random.randint(0,8) != 8: #A chance to miss
                        if gamestate.player.player_armor > 0:
                            gamestate.player.player_health -= int(self.dmg * 0.65)
                            if gamestate.player.player_armor >= self.dmg * 2:
                                gamestate.player.player_armor -= self.dmg * 2
                            else:
                                gamestate.player.player_armor = 0
                        else:
                            gamestate.player.player_health -= self.dmg

    def change_facing_direction(self):
        self.face = self.face + self.theta
        if self.face >= geom.DEGREES_360:
            self.face -= geom.DEGREES_360
        self.face = min(
            [
                geom.DEGREES_0, geom.DEGREES_90,
                geom.DEGREES_180, geom.DEGREES_270,
                geom.DEGREES_359
            ],
            key=lambda x: abs(x - self.face)
        )

    @staticmethod
    def drop_item(map_pos):
        # TODO: Move this into a loot manager or spawner controller
        texture = 'none.png'
        possible_drops = ['bullet', 'bullet', 'bullet',
                          'shell', 'shell',
                          'health',
                          'armor',
                          'ferromag', 'ferromag',]
        drop = random.choice(possible_drops)
        effect = random.randint(4, 12)
        if drop == 'bullet':
            texture = 'bullet.png'
        elif drop == 'shell':
            texture = 'shell.png'
        elif drop == 'health':
            texture = 'firstaid.png'
        elif drop == 'armor':
            texture = 'kevlar.png'
        elif drop == 'ferromag':
            texture = 'ferromag.png'
        else:
            print("Error: No texture with name ", drop)
        gamestate.items.all_items.append(ITEMS.Item(map_pos, os.path.join('graphics', 'items', texture), drop, effect))

#stats = {
#    'pos': [tile pos],
#    'face': degrees,
#    'spf': seconds per frame (float),
#    'dmg': damage on player,
#    'health' : health points,
#    'speed': pixels per second,
#    'mind': string -> hostile, passive, shy,
#    'state': string -> idle, patrouling,
#    'atcktype': string -> melee, hitscan,
#    'atckrate': chance of attacking - lower = faster
#    'id' : unique ID for npcs,
#    'filepath' : ('folder', 'folder', 'file.ext'),
#    'npc_name' : 'name' -> Used for connecting to a sound pack.
#    },

    
