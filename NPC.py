import SETTINGS
import SPRITES
import PATHFINDING
import ITEMS
import SOUND
import os
import random
import math
import pygame
# stats format in bottom of script
# pos is in tiles, face in degrees, frame_interval is seconds between frames, speed is pixels/second
import consts.raycast
from consts import npc_state
from consts.npc_side import SIDE_RIGHT, SIDE_LEFT
from consts.npc_side import SIDE_FRONT, SIDE_FRONT_LEFT, SIDE_FRONT_RIGHT
from consts.npc_side import SIDE_BACK, SIDE_BACK_LEFT, SIDE_BACK_RIGHT
from consts import geom
import consts.tile
import gamestate.inventory
import gamestate.items
import gamestate.npcs
import gamestate.player
import gamestate.sprites
from typing import List


class Npc:
    
    def __init__(self, stats, sounds, texture):
        # Technical settings
        self.front_tile = (1, 0)
        self.stats = stats  # Used for creating new NPCs
        self.sounds = sounds
        self.ID = stats['id']
        self.map_pos = stats['pos'] #List[int]
        self.pos = [self.map_pos[0] * consts.tile.TILE_SIZE, self.map_pos[1] * consts.tile.TILE_SIZE]
        self.face = stats['face']
        self.frame_interval = stats['spf']
        
        # Visual and rect settings
        self.rect = pygame.Rect((self.pos[0], self.pos[1]), (consts.tile.TILE_SIZE / 3, consts.tile.TILE_SIZE / 3))
        self.rect.center = (self.pos[0] + consts.tile.TILE_SIZE / 2, self.pos[1] + consts.tile.TILE_SIZE / 2)
        self.real_x = self.rect.x
        self.real_y = self.rect.y

        # todo move this caluclation to a function
        self.OG_map_pos = self.calculate_map_pos_from_rect()

        
        # Initialise boring variables
        self.timer = 0
        self.idle_timer = 0
        self.alive_turn = 0 # make this number of "turns" rather than absolute timer
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
        self.theta = 0
        self.mein_leben = False
        self.type = 'npc'
        self.last_seen_player_turn = None
        self.last_seen_player_position = None
        # debug maybe later messaging system?
        self.messages = []
        
        # NPC Characteristics
        self.health = stats['health']
        self.speed = stats['speed']
        self.OG_speed = self.speed
        self.mind = stats['mind']
        self.state = stats['state']
        self.OG_state = self.state
        self.atcktype = stats['atcktype']
        self.name = stats['name']
        self.perception_range = int(consts.tile.TILE_SIZE * random.choice([4, 5, 6]))
        self.OG_perception_range = self.perception_range
        self.max_perception_range = (consts.raycast.render * consts.tile.TILE_SIZE) - consts.tile.TILE_SIZE
        self.call_for_help_turns = 40 * random.choice(list(range(1, 4)))
        self.search_turns = (self.call_for_help_turns * random.choice([3, 3, 3, 4, 4, 5]))
        
        if stats['dmg'] != 3.1415:
            self.dmg = stats['dmg']
        else:
            self.dmg = random.choice([1, 2, 3])
        
        # TODO surely some interplay between attackrate and range?
        self.atckrate = stats['atckrate']
        self.range = 5
        
        # make first level easier
        if SETTINGS.current_level == 0 and SETTINGS.levels_list == SETTINGS.glevels_list:
            self.health = int(self.health * 0.8)
            self.dmg = int(self.dmg * 0.8)
        
        # Make late levels harder >:)
        elif SETTINGS.current_level > 4 and SETTINGS.levels_list == SETTINGS.glevels_list:
            self.health += int(SETTINGS.current_level / 3)
            self.dmg += int(SETTINGS.current_level / 5)
        
        # Make NPC stronger if player is doing well
        if gamestate.player.player_health >= 90 or gamestate.player.player_armor >= 90:
            self.dmg += 2
        
        # Give NPC more health if player has lots of ammo - phew, long line.
        if gamestate.inventory.held_weapons['primary'] and gamestate.inventory.held_ammo[
            gamestate.inventory.held_weapons['primary'].ammo_type] >= gamestate.inventory.max_ammo[
            gamestate.inventory.held_weapons['primary'].ammo_type]:
            self.health = int(self.health * 1.5)
        
        # Npc actions
        self.dead = False
        self.moving = False
        self.attacking = False
        self.hurting = False
        self.player_in_view = False
        
        # Textures and animations
        self.texture_path = texture  # Used for creating new NPCS
        self.texture = pygame.image.load(texture).convert_alpha()
        self.texturerect = self.texture.get_rect()
        
        self.stand_texture = [self.texture.subsurface(0, 0, 64, 128).convert_alpha(),
                              self.texture.subsurface(64, 0, 64, 128).convert_alpha(),
                              self.texture.subsurface(128, 0, 64, 128).convert_alpha(),
                              self.texture.subsurface(192, 0, 64, 128).convert_alpha(),
                              self.texture.subsurface(256, 0, 64, 128).convert_alpha(),
                              self.texture.subsurface(320, 0, 64, 128).convert_alpha(),
                              self.texture.subsurface(384, 0, 64, 128).convert_alpha(),
                              self.texture.subsurface(448, 0, 64, 128).convert_alpha()]
        self.front_texture = [self.texture.subsurface(0, 128, 64, 128).convert_alpha(),
                              self.texture.subsurface(64, 128, 64, 128).convert_alpha(),
                              self.texture.subsurface(128, 128, 64, 128).convert_alpha(),
                              self.texture.subsurface(192, 128, 64, 128).convert_alpha(),
                              self.texture.subsurface(256, 128, 64, 128).convert_alpha(),
                              self.texture.subsurface(320, 128, 64, 128).convert_alpha(),
                              self.texture.subsurface(384, 128, 64, 128).convert_alpha(),
                              self.texture.subsurface(448, 128, 64, 128).convert_alpha(),
                              self.texture.subsurface(512, 128, 64, 128).convert_alpha(),
                              self.texture.subsurface(576, 128, 64, 128).convert_alpha()]
        self.frontright_texture = [self.texture.subsurface(0, 256, 64, 128).convert_alpha(),
                                   self.texture.subsurface(64, 256, 64, 128).convert_alpha(),
                                   self.texture.subsurface(128, 256, 64, 128).convert_alpha(),
                                   self.texture.subsurface(192, 256, 64, 128).convert_alpha(),
                                   self.texture.subsurface(256, 256, 64, 128).convert_alpha(),
                                   self.texture.subsurface(320, 256, 64, 128).convert_alpha(),
                                   self.texture.subsurface(384, 256, 64, 128).convert_alpha(),
                                   self.texture.subsurface(448, 256, 64, 128).convert_alpha(),
                                   self.texture.subsurface(512, 256, 64, 128).convert_alpha(),
                                   self.texture.subsurface(576, 256, 64, 128).convert_alpha()]
        self.right_texture = [self.texture.subsurface(0, 384, 64, 128).convert_alpha(),
                              self.texture.subsurface(64, 384, 64, 128).convert_alpha(),
                              self.texture.subsurface(128, 384, 64, 128).convert_alpha(),
                              self.texture.subsurface(192, 384, 64, 128).convert_alpha(),
                              self.texture.subsurface(256, 384, 64, 128).convert_alpha(),
                              self.texture.subsurface(320, 384, 64, 128).convert_alpha(),
                              self.texture.subsurface(384, 384, 64, 128).convert_alpha(),
                              self.texture.subsurface(448, 384, 64, 128).convert_alpha(),
                              self.texture.subsurface(512, 384, 64, 128).convert_alpha(),
                              self.texture.subsurface(576, 384, 64, 128).convert_alpha()]
        self.backright_texture = [self.texture.subsurface(0, 512, 64, 128).convert_alpha(),
                                  self.texture.subsurface(64, 512, 64, 128).convert_alpha(),
                                  self.texture.subsurface(128, 512, 64, 128).convert_alpha(),
                                  self.texture.subsurface(192, 512, 64, 128).convert_alpha(),
                                  self.texture.subsurface(256, 512, 64, 128).convert_alpha(),
                                  self.texture.subsurface(320, 512, 64, 128).convert_alpha(),
                                  self.texture.subsurface(384, 512, 64, 128).convert_alpha(),
                                  self.texture.subsurface(448, 512, 64, 128).convert_alpha(),
                                  self.texture.subsurface(512, 512, 64, 128).convert_alpha(),
                                  self.texture.subsurface(576, 512, 64, 128).convert_alpha()]
        self.back_texture = [self.texture.subsurface(0, 640, 64, 128).convert_alpha(),
                             self.texture.subsurface(64, 640, 64, 128).convert_alpha(),
                             self.texture.subsurface(128, 640, 64, 128).convert_alpha(),
                             self.texture.subsurface(192, 640, 64, 128).convert_alpha(),
                             self.texture.subsurface(256, 640, 64, 128).convert_alpha(),
                             self.texture.subsurface(320, 640, 64, 128).convert_alpha(),
                             self.texture.subsurface(384, 640, 64, 128).convert_alpha(),
                             self.texture.subsurface(448, 640, 64, 128).convert_alpha(),
                             self.texture.subsurface(512, 640, 64, 128).convert_alpha(),
                             self.texture.subsurface(576, 640, 64, 128).convert_alpha()]
        
        self.backleft_texture = []
        self.left_texture = []
        self.frontleft_texture = []
        
        for frame in self.backright_texture:
            self.backleft_texture.append(pygame.transform.flip(frame, True, False))
        for frame in self.right_texture:
            self.left_texture.append(pygame.transform.flip(frame, True, False))
        for frame in self.frontright_texture:
            self.frontleft_texture.append(pygame.transform.flip(frame, True, False))
        
        self.die_texture = [self.texture.subsurface(0, 768, 64, 128).convert_alpha(),
                            self.texture.subsurface(64, 768, 64, 128).convert_alpha(),
                            self.texture.subsurface(128, 768, 64, 128).convert_alpha(),
                            self.texture.subsurface(192, 768, 64, 128).convert_alpha(),
                            self.texture.subsurface(256, 768, 64, 128).convert_alpha(),
                            self.texture.subsurface(320, 768, 64, 128).convert_alpha(),
                            self.texture.subsurface(384, 768, 64, 128).convert_alpha(),
                            self.texture.subsurface(448, 768, 64, 128).convert_alpha(),
                            self.texture.subsurface(512, 768, 64, 128).convert_alpha(),
                            self.texture.subsurface(576, 768, 64, 128).convert_alpha(),
                            self.texture.subsurface(640, 768, 64, 128).convert_alpha()]
        self.hit_texture = [self.texture.subsurface(0, 896, 64, 128).convert_alpha(),
                            self.texture.subsurface(64, 896, 64, 128).convert_alpha(),
                            self.texture.subsurface(128, 896, 64, 128).convert_alpha(),
                            self.texture.subsurface(192, 896, 64, 128).convert_alpha(),
                            self.texture.subsurface(256, 896, 64, 128).convert_alpha(),
                            self.texture.subsurface(320, 896, 64, 128).convert_alpha()]
        self.hurt_texture = [self.die_texture[0]]
        self.current_frame = 1
        self.update_timer = 0
        
        # Creating the sprite rect is awful, I know. Keeps it from entering walls.
        self.sprite = SPRITES.Sprite(self.front_texture[1], self.ID, [self.rect.centerx - int(
            consts.tile.TILE_SIZE / 12), self.rect.centery - int(consts.tile.TILE_SIZE / 10)], 'npc', self)
        
        # The position in SETTINGS.all_sprites of this NPC
        self.num = len(gamestate.sprites.all_sprites) - 1

    def calculate_map_pos_from_rect(self):
        return [
            int(self.rect.centerx / consts.tile.TILE_SIZE),
            int(self.rect.centery / consts.tile.TILE_SIZE)
        ]

    def add_message(self, *args):
        message = [*args]
        if message not in self.messages:
            self.messages.append(message)
    
    def print_messages(self):
        if len(self.messages) > 0:
            print(id(self), self.name, ":", self.mind, self.state)
            for item in self.messages:
                print(id(self), item)
            self.messages = []


    def think(self):

        self.map_pos = self.calculate_map_pos_from_rect()

        if self.state == npc_state.ATTACKING or self.state == npc_state.FLEEING:
            self.speed = self.OG_speed * 2

        # not calling is_alive because we need
        # to render the dying frames
        if not self.dead:
            self.timer += SETTINGS.dt
            self.update_timer += SETTINGS.dt
            self.alive_turn += 1

            if self.update_timer >= 2:
                self.update_timer = 0

                self.update_perception_range()

                if self.state == npc_state.SEARCHING:
                    self.add_message("Searching - last player pos", self.last_seen_player_position, " - my position", self.map_pos)

                self.print_messages()

        if self.is_alive() and not gamestate.player.player_states['dead']:
            self.render()

            if self.dist_from_player and self.dist_from_player <= consts.raycast.render * consts.tile.TILE_SIZE * 1.2:

                # PASSIVE
                if self.mind == 'passive':
                    self.look_for_player(npc_state.IDLE, npc_state.ATTACKING)

                # HOSTILE
                elif self.mind == 'hostile':
                    self.look_for_player(npc_state.ATTACKING)

                # SHY
                elif self.mind == 'shy':
                    self.look_for_player(npc_state.FLEEING, npc_state.ATTACKING)

                else:
                    self.add_message("No Instructions for Mind!", self.mind)


            # Act upon state
            if self.state == npc_state.ATTACKING:
                self.attack()
            elif self.state == npc_state.PATROLLING:
                self.move()
            elif self.state == npc_state.FLEEING:
                self.move()
            elif self.state == npc_state.IDLE:
                self.idle()
            elif self.state == npc_state.SEARCHING:
                self.move()
            else:
                self.add_message("Unknown State", self.state)

            # Run animations
            if self.hurting:
                self.animate('hurting')

                # if npc takes damage and is not fleeing
                # retaliate and fight back
                if self.state != npc_state.FLEEING:
                    # todo call a method to make this transition
                    self.set_state(npc_state.ATTACKING)

            elif self.moving:
                self.animate('walking')

        if gamestate.player.player_states['dead']:
            self.face += geom.DEGREES_10
            if self.face >= geom.DEGREES_360:
                self.face -= geom.DEGREES_360
            self.render()

        elif self.health <= 0 and not self.dead:
            self.animate('dying')
            self.render()

    def update_perception_range(self):

        # if we are in combat then we can skip
        if self.attacking:
            return

        # prevent div by zero errors
        perception_range_denominator = self.dist_from_player
        if perception_range_denominator is None:
            perception_range_denominator = 1.0
        elif perception_range_denominator < 1.0:
            perception_range_denominator = 1.0

        if self.player_in_view and self.is_within_renderable_distance():
            ratio = self.perception_range / perception_range_denominator
            delta = int(self.OG_perception_range * ratio)
            self.perception_range += delta

            if self.perception_range > self.max_perception_range:
                self.perception_range = self.max_perception_range
                self.add_message("perception range at max", self.perception_range)
            else:
                self.add_message("increasing perception range", self.perception_range)
        else:
            delta = int(self.perception_range * 0.10)

            if self.perception_range != self.OG_perception_range:
                self.perception_range -= delta
                if self.perception_range < self.OG_perception_range:
                    self.add_message("perception range reset", self.perception_range)
                    self.perception_range = self.OG_perception_range
                else:
                    self.add_message("shrinking perception range", self.perception_range)

    def look_for_player(self, state_if_spotted, state_if_startled = None):
        if state_if_startled is None:
            state_if_startled = state_if_spotted
        
        if not self.is_alive():
            return False

        if not self.is_ignoring_player():
            if self.detect_player():
                if self.dist_from_player < self.perception_range:
                    self.react_to_player(state_if_startled)
                else:
                    self.react_to_player(state_if_spotted)
                return True
            else:
                # TODO configureable search time
                if self.search_for_player():
                    self.add_message("searching for player", self.mind,
                                     self.state)
                else:
                    self.add_message("not searching for player", self.mind, self.state)
                    if self.state == npc_state.SEARCHING:
                        self.reset_to_original_state()
        return False

    def is_searching_for_player(self):
        result = False
        if self.last_seen_player_turn is None:
            return result

        time_delta = self.alive_turn - self.last_seen_player_turn
        result = time_delta < self.search_turns

        # todo customisable/random additional search time
        self.add_message("is_searching_for_player:", result)


        return result

    def reset_to_original_state(self):
        # TODO rules before switching
        if self.attacking:
            self.add_message("won't reset_to_original_state busy attacking")
            return False
        
        self.add_message(
            "reseting state to ", self.OG_state,
            " and returning to ", self.OG_map_pos
        )

        self.set_state(self.OG_state)
        self.set_path(self.OG_map_pos)
        
        return True

    def has_a_path(self):
        return len(self.path) > 0

    def is_at_destination_rect_center(self):
        return self.has_a_path() and (self.rect.center == self.path[-1].rect.center)

    def is_at_destination(self):
        return self.path[self.path_progress] == self.path[-1]

    def search_for_player(self):
        
        conditions = [
            not self.is_ignoring_player(),
            self.state != npc_state.FLEEING,
            self.last_seen_player_turn is not None,
            self.last_seen_player_position is not None,
            self.mind != "shy"
        ]

        can_search = all(conditions)

        # if passive maybe sometime we don't go
        # looking for the player
        if self.mind == "passive" and can_search:
            if random.choice(list(range(1, 8))) > 5:
                self.add_message("could go searching, but I'm lazy")
                can_search = False

        if can_search:
            if self.is_searching_for_player():

                if not self.has_a_path() or self.state != npc_state.SEARCHING:
                    self.set_state(npc_state.SEARCHING)
                    self.add_message("looking for player in last position", self.last_seen_player_position)
                    self.set_path_to_player()
                else:
                    self.add_message("looking for player, already have a path", self.path[-1].map_pos, self.last_seen_player_position)
                return True
        
        return False
    
    def seen_player(self):
        self.last_seen_player_position = gamestate.player.player_map_pos
        self.last_seen_player_turn = self.alive_turn
        self.add_message("seen player at ", self.last_seen_player_position)

    def set_state(self, new_state):
        # if we have not changed state
        # then our current path is possibly
        # not what we want to be
        if self.state != new_state:
            self.set_path([])
            self.add_message("changing state from", self.state, "to", new_state)
            self.state = new_state
    
    def can_call_for_help(self):
        call_for_help = self.last_seen_player_turn is None
        if not call_for_help:
            call_for_help = (self.alive_turn - self.last_seen_player_turn) > self.call_for_help_turns
        return call_for_help
    
    def do_call_for_help(self, number_of_allies):
        if self.can_call_for_help():
            SOUND.play_sound(self.sounds['spot'], self.dist_from_player)
            self.seen_player()
            self.add_message("calling for backup")
            self.call_allies(id(self), number_of_allies, "hostile", npc_state.SEARCHING, self.last_seen_player_position)
            
            return True
        
        return False

    def react_to_player(self, new_state):

        self.set_state(new_state)

        # if we didn't call for help
        # still update the last_seen vars
        if not self.do_call_for_help(number_of_allies = 2):
            self.seen_player()
            
    
    @staticmethod
    def call_allies(caller, max_allies, mind_filter, new_state, target_pos):
        woken_allies = 0
        for npc in gamestate.npcs.npc_list:
            # todo better rules
            if npc.mind == mind_filter and id(npc) != caller and not npc.attacking:
                if npc.dist_from_player <= (npc.get_perception_distance() * 1.5):
                    npc.add_message("woken up as an ally")
                    # call seen_player so that search checks pass
                    npc.seen_player()
                    npc.set_state(new_state)
                    npc.set_path(target_pos)
                    woken_allies += 1
                    if woken_allies >= max_allies:
                        break
    
    def get_perception_distance(self):
        # TODO perhaps some perception modifier depending on the state/mind? and recency of seen player
        perception_distance = self.perception_range
        
        # using sides as render has calculated this for us
        if self.side == SIDE_BACK_RIGHT or self.side == SIDE_BACK_LEFT:
            perception_distance = (perception_distance / 2)
        elif self.side == SIDE_BACK:
            # if npc back is shown to player can sneak right up
            perception_distance = (perception_distance / 3)
        
        return perception_distance


    def is_within_renderable_distance(self):
        return self.dist_from_player <= consts.raycast.render * consts.tile.TILE_SIZE


    def render(self):
        '''== Draw the NPC =='''
        if not self.is_alive():
            self.solid = False
        
        xpos = gamestate.player.player_rect.centerx - self.rect.centerx
        ypos = gamestate.player.player_rect.centery - self.rect.centery
        
        self.dist_from_player = math.sqrt(xpos * xpos + ypos * ypos)
        
        if self.is_within_renderable_distance():

            theta = math.atan2(-ypos, xpos) % (2 * math.pi)
            theta = math.degrees(theta)
            self.postheta = theta
            theta -= self.face
            if theta < geom.DEGREES_0:
                theta += geom.DEGREES_360
            elif theta > geom.DEGREES_360:
                theta -= geom.DEGREES_360

            self.sprite.update_pos([self.rect.x, self.rect.y])

            self.set_theta_and_side(theta)
        
        if gamestate.sprites.all_sprites[self.num] != self.sprite:
            gamestate.sprites.all_sprites[self.num] = self.sprite
        
        # Find out what x and y coordinates would change
        if self.face == geom.DEGREES_90:
            self.front_tile = (0, -1)
        elif self.face == geom.DEGREES_180:
            self.front_tile = (-1, 0)
        elif self.face == geom.DEGREES_270:
            self.front_tile = (0, 1)
        elif self.face == geom.DEGREES_0 or self.face == geom.DEGREES_360:
            pass

    def set_side(self, side):
        # this function assumes we only have one player
        # this and host of other will have to change if
        # that changes
        self.player_in_view = side.player_in_view

        # all of these conditions must be met
        # if we are going to change the sprite
        change_sprite_rules = [
            self.side != side.name,
            self.is_alive(),
            not self.hurting,
            not self.attacking,
            self.in_canvas
        ]

        if all(change_sprite_rules) or not self.side:
            if not self.attacking:
                if self.moving:
                    self.sprite.texture = self.get_direction_texture(side.name)[self.current_frame]
                else:
                    self.sprite.texture = self.stand_texture[side.stand_index]

        self.side = side.name

        return self.side

    def set_theta_and_side(self, theta):
        self.theta = theta

        # What side is the NPC facing?
        # (or not self.side is to make sure it finds the right angle from initialization)
        for side in [
            SIDE_FRONT, SIDE_FRONT_LEFT, SIDE_LEFT, SIDE_BACK_LEFT,
            SIDE_BACK, SIDE_BACK_RIGHT, SIDE_RIGHT, SIDE_FRONT_RIGHT,
        ]:
            # need OR for SIDE_FRONT, as the degree_min is numerically
            # larger than the degree_max value
            if (side.degree_min < side.degree_max and side.degree_min <= theta <= side.degree_max) or \
                    (side.degree_min > side.degree_max and (theta >= side.degree_min or theta <= side.degree_max)):

                self.set_side(side)
                break
        
        return self.side
    
    def is_ignoring_player(self):
        
        if SETTINGS.ignore_player:
            return True
        
        # TODO additional additional explicit conditions
        if self.attacking:
            return False
        
        return False
    
    def detect_player(self):

        if self.attacking:
            return True

        if self.is_ignoring_player():
            self.add_message("ignoring player")
            return False

        if self.dist_from_player < (consts.tile.TILE_SIZE / 2):
            self.add_message("Player is on top of me")
            return True

        '''== Is player visible from NPC position? ==\ndetect_player(self) -> boolean'''
        perception_distance = self.get_perception_distance()
        has_los = PATHFINDING.has_line_of_sight(self.map_pos, gamestate.player.player_map_pos)

        if has_los:
            if self.dist_from_player <= perception_distance:
                self.add_message("player in LOS within perception did I see", has_los)
                return True
            else:
                self.add_message("player in LOS but my eyesight let me down", self.state, self.mind, perception_distance, self.dist_from_player)
                return False
        else:
            if self.dist_from_player <= consts.tile.TILE_SIZE * 2:
                self.add_message("player is close but I don't have LOS", self.state, self.mind, perception_distance, self.dist_from_player)

        # it should be False here
        return False
    
    def collide_update(self, x, y):
        # make sure the NPC doesn't walk inside stuff
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
    
    def set_path(self, destination_map_pos: List[int]):
        if len(destination_map_pos) > 0:
            self.path = PATHFINDING.pathfind(self.map_pos, destination_map_pos)
        else:
            self.path = []
        
        self.path_progress = 0

    def set_path_to_player(self):
        destination_map_pos = self.last_seen_player_position
        if destination_map_pos is None:
            # magical gps!
            destination_map_pos = gamestate.player.player_map_pos

        self.set_path(destination_map_pos)

        # now if our destination has changed it's because
        # the player is probably in a solid-ish block
        if self.has_a_path():
            if self.path[-1].map_pos != destination_map_pos:
                # TODO some sort of tolerance based on our attackrange
                self.last_seen_player_position = self.path[-1].map_pos


    def is_alive(self):
        return self.health > 0 and not self.dead

    def move(self):
        # Make the NPC move according to current state.
        moving_up = False
        moving_down = False
        moving_right = False
        moving_left = False

        can_move_conditions = [
            self.has_a_path(),
            not self.is_at_destination_rect_center(),
            self.is_alive(),
            not self.hurting
        ]
        
        if all(can_move_conditions):
            self.moving = True
            
            # Redo path if tile is occupied by another NPC.
            if self.update_timer <= 0.5:
                for npc in gamestate.npcs.npc_list:
                    if npc.map_pos == self.path[-1].map_pos:
                        available_pos = [x for x in SETTINGS.walkable_area if
                                         abs(x.map_pos[0] - self.map_pos[0]) <= 3 and abs(
                                             x.map_pos[1] - self.map_pos[1]) <= 3]
                        self.set_path(random.choice(available_pos).map_pos)
                        break
            
            if self.rect.colliderect(self.path[self.path_progress].rect) and not self.is_at_destination():
                self.path_progress += 1
            
            else:
                # Move down
                if self.rect.centery < self.path[self.path_progress].rect.centery:
                    if abs(self.path[self.path_progress].rect.centery - self.rect.centery) >= self.speed * SETTINGS.dt:
                        self.collide_update(0, self.speed)
                        moving_down = True
                    else:
                        self.rect.centery = self.path[self.path_progress].rect.centery
                
                # Moving up
                elif self.rect.centery > self.path[self.path_progress].rect.centery:
                    if abs(self.path[self.path_progress].rect.centery - self.rect.centery) >= self.speed * SETTINGS.dt:
                        self.collide_update(0, -self.speed)
                        moving_up = True
                    else:
                        self.rect.centery = self.path[self.path_progress].rect.centery
                
                # Move right
                if self.rect.centerx < self.path[self.path_progress].rect.centerx:
                    if abs(self.path[self.path_progress].rect.centerx - self.rect.centerx) >= self.speed * SETTINGS.dt:
                        self.collide_update(self.speed, 0)
                        moving_right = True
                    else:
                        self.rect.centerx = self.path[self.path_progress].rect.centerx
                
                # Move left
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
                # TODO make a reset_path method
                self.set_path([])

                if self.state == npc_state.SEARCHING:
                    self.add_message("searching but stopped moving", self.map_pos, " player", self.last_seen_player_position)
        
        if self.state == npc_state.PATROLLING:
            self.loiter()
        elif self.state == npc_state.SEARCHING:
            if not self.has_a_path() and self.map_pos == self.last_seen_player_position:
                self.wander_nearby()
        elif self.state == npc_state.FLEEING:
            if self.dist_from_player <= consts.tile.TILE_SIZE * 4:
                flee_pos = random.choice(SETTINGS.walkable_area)
                player_tile = [x for x in SETTINGS.walkable_area if x.map_pos == self.last_seen_player_position]
                if player_tile:
                    player_tile = player_tile[0]
                else:
                    player_tile = PATHFINDING.find_tile_near_position(self.last_seen_player_position)
                
                if self.player_in_view:
                    if self.detect_player() and player_tile:
                        if ((SETTINGS.walkable_area.index(flee_pos) < SETTINGS.walkable_area.index(player_tile) + int(
                                SETTINGS.current_level_size[0] / 5)) or (
                                    SETTINGS.walkable_area.index(flee_pos) > SETTINGS.walkable_area.index(
                                    player_tile) - int(SETTINGS.current_level_size[0] / 5))) and not self.has_a_path():
                            self.set_path(flee_pos.map_pos)

    def loiter(self):
        if not self.has_a_path():
            if random.randint(0, 3) == 3:
                self.add_message("loitering")
                self.set_state(npc_state.IDLE)
            else:
                self.wander_nearby()

    def wander_nearby(self):
        if not self.has_a_path():
            self.add_message("wandering")
            # Make the NPC not walk too far.
            available_tile = PATHFINDING.find_walkable_tile_near_position(self.map_pos, 3)
            if available_tile:
                self.set_path(available_tile.map_pos)

    def idle(self):
        # Make the NPC rotate randomly as it stands still.
        self.idle_timer += SETTINGS.dt
        
        if self.idle_timer >= 3:
            if random.randint(0, 2) == 2:
                self.face += geom.DEGREES_45
            elif random.randint(0, 2) == 2:
                self.face -= geom.DEGREES_45
            if self.face >= geom.DEGREES_360:
                self.face -= geom.DEGREES_360
            
            self.idle_timer = 0
            
            # Do only change to patrouling if it was that in the first place.
            if self.OG_state != npc_state.IDLE:
                if random.randint(0, 2) == 2:
                    self.set_state(npc_state.PATROLLING)
        
        # Make NPC react to gunshot if close. Or just if the player is too close.
        # TODO move this elsewhere
        player_shot_near_conditions = [
            self.dist_from_player <= self.get_perception_distance() * 4,
            gamestate.player.mouse_btn_active,
            gamestate.inventory.current_gun
        ]
        if all(player_shot_near_conditions) or self.dist_from_player <= self.rect.width:
            self.change_facing_direction()
    
    def attack(self):
        if self.attack_move:
            self.move()
        else:
            if self.atcktype == 'melee':
                # Move close to player and keep attacking
                if self.dist_from_player <= consts.tile.TILE_SIZE * 0.7:
                    self.set_path([])
                    self.moving = False
                    if not self.attacking:
                        if self.timer >= self.frame_interval * self.atckrate:
                            self.attacking = True
                            self.timer = 0
                    else:
                        # Make the NPC not flinch when attacking
                        if self.hurting:
                            if random.randint(0, 2) != 2 or self.attacking:
                                self.animate(npc_state.ATTACKING)
                                self.hurting = False
                                if random.randint(0, 2) == 2:
                                    SOUND.play_sound(random.choice(self.sounds['damage']), self.dist_from_player)
                        else:
                            self.animate(npc_state.ATTACKING)
                
                else:
                    if self.dist_from_player > consts.tile.TILE_SIZE * 0.7 and not self.has_a_path():
                        self.set_path_to_player()

                    elif self.has_a_path():
                        try:
                            if self.path[-1].map_pos != self.last_seen_player_position:
                                near_conditions = [
                                    self.dist_from_player <= (consts.raycast.render / 2) * consts.tile.TILE_SIZE,
                                    random.randint(0, 5) == 5
                                ]
                                if all(near_conditions):
                                    self.set_path_to_player()
                                elif random.randint(0, 10) >= 8:
                                    self.set_path_to_player()
                            else:
                                self.move()
                        except:
                            pass
            
            elif self.atcktype == 'hitscan':
                # Move somewhat close to player and change position after attacking
                if self.dist_from_player <= consts.tile.TILE_SIZE * self.range and (
                        self.dist_from_player >= consts.tile.TILE_SIZE * 1.5 or (
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
                                
                                move_tile = PATHFINDING.find_walkable_tile_near_position(self.map_pos)
                                self.set_path(move_tile.map_pos)
                                self.attacking = False
                                self.attack_move = True
                                # This variable is to make sure the NPC doesn't just walk around without attacking.
                                self.movechance += 3
                                self.atckchance = 5
                    
                    # There is a chance the NPC will not flinch when shot while attacking
                    elif self.attacking:
                        if self.hurting:
                            if random.randint(0, 5) >= 3:
                                self.animate(npc_state.ATTACKING)
                                self.hurting = False
                                if random.randint(0, 2) == 2:
                                    SOUND.play_sound(random.choice(self.sounds['damage']), self.dist_from_player)
                        else:
                            self.animate(npc_state.ATTACKING)
                
                # Move away from player if too close
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
                        if self.dist_from_player >= consts.tile.TILE_SIZE * 2.5 and not self.has_a_path():
                            self.set_path_to_player()

                        elif self.has_a_path():
                            try:
                                if self.path[-1].map_pos != self.last_seen_player_position:
                                    near_conditions = [
                                        self.dist_from_player <= (consts.raycast.render / 2) * consts.tile.TILE_SIZE,
                                        random.randint(0, 5) == 5
                                    ]
                                    if all(near_conditions):
                                        self.set_path_to_player()
                                    elif random.randint(0, 10) == 10:
                                        self.set_path_to_player()
                                else:
                                    self.move()
                            except:
                                pass
    
    def get_direction_texture(self, direction = None):
        if direction is None:
            direction = self.side
        
        if direction == SIDE_FRONT:
            return self.front_texture
        elif direction == SIDE_FRONT_LEFT:
            return self.frontleft_texture
        elif direction == SIDE_LEFT:
            return self.left_texture
        elif direction == SIDE_BACK_LEFT:
            return self.backleft_texture
        elif direction == SIDE_BACK:
            return self.back_texture
        elif direction == SIDE_BACK_RIGHT:
            return self.backright_texture
        elif direction == SIDE_RIGHT:
            return self.right_texture
        elif direction == SIDE_FRONT_RIGHT:
            return self.frontright_texture
        
        # TODO probably some sort of warning/exception for unknown side
        # self.add_message("unknown direction in get_direction_texture", direction)
        return self.front_texture
    
    def animate(self, animation):
        '''== Animate NPC ==\nanimation -> dying, walking, attacking, hurting'''
        if self.running_animation != animation:
            self.current_frame = 0
            self.running_animation = animation
        
        # walk animation
        if animation == 'walking':
            self.sprite.texture = self.get_direction_texture()[self.current_frame]
            
            if self.timer >= self.frame_interval:
                self.current_frame += 1
                self.timer = 0
                if self.current_frame == len(self.front_texture) - 1:
                    self.current_frame = 0

        # die animation
        elif animation == 'dying':
            self.sprite.texture = self.die_texture[self.current_frame]
            if self.current_frame == 0 and not self.mein_leben:
                self.mein_leben = True
                SOUND.play_sound(random.choice(self.sounds['die']), self.dist_from_player)
            if self.timer >= self.frame_interval and self.current_frame < len(self.die_texture) - 1:
                self.current_frame += 1
                self.timer = 0
            elif self.current_frame == len(self.die_texture) - 1 and self.knockback == 0:
                self.dead = True
                self.drop_item(self.map_pos)
                SETTINGS.statistics['last enemies'] += 1
                self.add_message("bye")
                self.print_messages()
            elif self.knockback > 0:
                self.collide_update(-math.cos(math.radians(self.postheta)) * self.knockback, 0)
                self.collide_update(0, math.sin(math.radians(self.postheta)) * self.knockback)
                self.knockback = int(self.knockback * 0.8)


        # hurt animation
        elif animation == 'hurting':
            self.sprite.texture = self.hurt_texture[0]
            self.moving = False
            if self.timer >= self.frame_interval * 2:
                self.side = None
                self.hurting = False
                self.timer = 0
                SOUND.play_sound(random.choice(self.sounds['damage']), self.dist_from_player)

                change_direction_conditions = [
                    self.state == npc_state.IDLE,
                    self.state == npc_state.PATROLLING,
                    self.state == npc_state.FLEEING,
                    self.state == npc_state.SEARCHING,
                ]

                if any(change_direction_conditions):
                    self.change_facing_direction()

        # attack animation
        elif animation == npc_state.ATTACKING:
            # at the moment the only attack animation
            # is directly facing the player
            self.set_side(SIDE_FRONT)

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
                    if random.randint(0, 8) != 8:  # A chance to miss
                        if gamestate.player.damage_player(self.dmg, self.atcktype, self.map_pos):
                            self.add_message("Did damage to player")
                            self.seen_player()
                        else:
                            self.add_message("tried to attack but I don't have LOS?")
    
    def change_facing_direction(self):
        self.face = self.face + self.sprite.theta
        if self.face >= geom.DEGREES_360:
            self.face -= geom.DEGREES_360
        self.face = min(
            [
                geom.DEGREES_0, geom.DEGREES_90,
                geom.DEGREES_180, geom.DEGREES_270,
                geom.DEGREES_359
            ],
            key = lambda x: abs(x - self.face)
        )

        self.set_theta_and_side(self.face)
    
    @staticmethod
    def drop_item(map_pos):
        # TODO: Move this into a loot manager or spawner controller
        texture = 'none.png'
        possible_drops = ['bullet', 'bullet', 'bullet',
                          'shell', 'shell',
                          'health',
                          'armor',
                          'ferromag', 'ferromag', ]
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

# stats = {
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

    
