from collections import namedtuple
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
from duga_enum import DugaEnum


class NpcState(DugaEnum):
    ATTACKING = "attacking"
    FLEEING = "fleeing"
    IDLE = "idle"
    PATROLLING = "patrolling"


class NpcMind(DugaEnum):
    PASSIVE = "passive"
    HOSTILE = "hostile"
    SHY = "shy"


class NpcAnimation(DugaEnum):
    ATTACKING = "attack"
    WALKING = "walking"
    DYING = "dying"
    HURTING = "hurting"


class NpcSideName(DugaEnum):
    FRONT = "front"
    FRONT_LEFT = "frontleft"
    LEFT = "left"
    BACK_LEFT = "backleft"
    BACK = "back"
    BACK_RIGHT = "backright"
    RIGHT = "right"
    FRONT_RIGHT = "frontright"


class NpcSide(namedtuple("NpcSide", "name,degree_min,degree_max,player_in_view,stand_index")):
    # overriding equality to compare
    # the name value
    def __eq__(self, obj):
        return self.name == obj


class Npc:
    def __init__(self, stats, sounds, directional_sprite):
        # Technical settings
        self.stats = stats  # Used for creating new NPCs
        self.sounds = sounds
        self.ID = stats['id']
        self.map_pos = stats['pos']
        self.pos = [self.map_pos[0] * SETTINGS.tile_size, self.map_pos[1] * SETTINGS.tile_size]
        self.face = stats['face']
        self.frame_interval = stats['spf']
        self.dda_list = SETTINGS.walkable_area + [x for x in SETTINGS.all_solid_tiles if x.type == 'sprite']

        # Visual and rect settings
        self.rect = pygame.Rect((self.pos[0], self.pos[1]), (SETTINGS.tile_size / 3, SETTINGS.tile_size / 3))
        self.rect.center = (self.pos[0] + SETTINGS.tile_size / 2, self.pos[1] + SETTINGS.tile_size / 2)
        self.real_x = self.rect.x
        self.real_y = self.rect.y

        # Initialise boring variables
        self.timer = 0
        self.idle_timer = 0
        self.die_animation = False
        self.running_animation = None
        self.add = 0
        self.dist = None
        self.collide_list = SETTINGS.all_solid_tiles + SETTINGS.npc_list
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

        # NPC Characteristics
        self.health = stats['health']
        self.speed = stats['speed']
        self.OG_speed = self.speed
        self.mind = NpcMind[stats['mind']]
        self.state = NpcState[stats['state']]
        self.OG_state = self.state
        self.atcktype = stats['atcktype']
        self.name = stats['name']

        if stats['dmg'] != 3.1415:
            self.dmg = stats['dmg']
        else:
            self.dmg = random.choice([1, 2, 3])
        self.atckrate = stats['atckrate']

        self.range = 5

        # TODO move this elsewhere
        # make first level easier
        if SETTINGS.current_level == 0 and SETTINGS.levels_list == SETTINGS.glevels_list:
            self.health = int(self.health * 0.8)
            self.dmg = int(self.dmg * 0.8)

        # Make late levels harder >:)
        elif SETTINGS.current_level > 4 and SETTINGS.levels_list == SETTINGS.glevels_list:
            self.health += int(SETTINGS.current_level / 3)
            self.dmg += int(SETTINGS.current_level / 5)

        # Make NPC stronger if player is doing well
        if SETTINGS.player_health >= 90 or SETTINGS.player_armor >= 90:
            self.dmg += 2

        # Give NPC more health if player has lots of ammo - phew, long line.
        if SETTINGS.inventory['primary'] and SETTINGS.held_ammo[SETTINGS.inventory['primary'].ammo_type] >= \
                SETTINGS.max_ammo[SETTINGS.inventory['primary'].ammo_type]:
            self.health = int(self.health * 1.5)

        # Npc actions
        self.dead = False
        self.moving = False
        self.attacking = False
        self.hurting = False
        self.player_in_view = False

        # timers
        self.update_timer = 0

        # Textures and animations
        self.directional_sprite = SETTINGS.directional_sprites[directional_sprite]

        # Set theta and facing side
        self.theta = self.get_theta(0, 0)

        # Creating the sprite rect is awful, I know. Keeps it from entering walls.
        self.sprite = SPRITES.Sprite(self.directional_sprite.default(), self.ID,
                                     [self.rect.centerx - int(SETTINGS.tile_size / 12),
                                      self.rect.centery - int(SETTINGS.tile_size / 10)], 'npc', self)

        # The position in SETTINGS.all_sprites of this NPC
        self.num = len(SETTINGS.all_sprites) - 1

    def think(self) -> None:
        """
        Choose a state to transition to it (or stay on current state) and
        act upon the chosen state
        :return:
        """
        self.map_pos = [int(self.rect.centerx / SETTINGS.tile_size), int(self.rect.centery / SETTINGS.tile_size)]
        if self.state == NpcState.ATTACKING or self.state == NpcState.FLEEING:
            self.speed = self.OG_speed * 2

        if not self.dead:
            self.timer += SETTINGS.dt
            self.update_timer += SETTINGS.dt
            if self.update_timer >= 2:
                self.update_timer = 0

        if not self.dead and self.health > 0 and not SETTINGS.player_states['dead']:
            self.render()

            if self.dist and self.dist <= SETTINGS.render * SETTINGS.tile_size * 1.2:

                # PASSIVE
                if self.mind == NpcMind.PASSIVE:
                    if self.state == NpcState.IDLE:
                        self.idle()

                    elif self.state == NpcState.PATROLLING:
                        self.move()

                # HOSTILE
                elif self.mind == NpcMind.HOSTILE:
                    if self.state == NpcState.IDLE:
                        self.idle()
                        if not SETTINGS.ignore_player:
                            if self.player_in_view:
                                if self.detect_player:
                                    self.path = []
                                    SOUND.play_sound(self.sounds['spot'], self.dist)
                                    self.state = NpcState.ATTACKING

                    elif self.state == NpcState.PATROLLING:
                        if self.player_in_view and not SETTINGS.ignore_player and self.detect_player:
                            self.path = []
                            SOUND.play_sound(self.sounds['spot'], self.dist)
                            self.state = NpcState.ATTACKING
                        elif self.dist <= SETTINGS.tile_size / 2 and not SETTINGS.ignore_player:
                            state = NpcState.ATTACKING
                        else:
                            self.move()

                    elif self.state == NpcState.ATTACKING:
                        self.attack()


                # SHY
                elif self.mind == NpcMind.SHY:
                    if self.state == NpcState.IDLE:
                        self.idle()
                        if not SETTINGS.ignore_player:
                            if self.player_in_view:
                                if self.detect_player:
                                    self.path = []
                                    SOUND.play_sound(self.sounds['spot'], self.dist)
                                    self.state = NpcState.FLEEING
                            elif self.dist <= SETTINGS.tile_size / 2:
                                state = NpcState.ATTACKING

                    elif self.state == NpcState.PATROLLING:
                        if self.player_in_view:
                            if not SETTINGS.ignore_player:
                                if self.detect_player:
                                    self.path = []
                                    SOUND.play_sound(self.sounds['spot'], self.dist)
                                    self.state = NpcState.FLEEING
                        elif self.dist <= SETTINGS.tile_size / 2:
                            if not SETTINGS.ignore_player:
                                state = NpcState.ATTACKING
                        else:
                            self.move()

                    elif self.state == NpcState.FLEEING:
                        self.move()

            # Run animations
            if self.hurting:
                self.animate(NpcAnimation.HURTING)
            elif self.moving:
                self.animate(NpcAnimation.WALKING)

        if SETTINGS.player_states['dead']:
            self.face += 10
            if self.face >= 360:
                self.face -= 360
            self.render()

        elif self.health <= 0 and not self.dead:
            self.animate(NpcAnimation.DYING)
            self.render()

    def render(self) -> None:
        """
        == Draw the NPC ==
        :return:
        """
        if self.dead:
            self.solid = False

        xpos = SETTINGS.player_rect.centerx - self.rect.centerx
        ypos = SETTINGS.player_rect.centery - self.rect.centery

        self.dist = math.sqrt(xpos * xpos + ypos * ypos)

        if self.dist <= SETTINGS.render * SETTINGS.tile_size:
            theta = self.get_theta(xpos, ypos)

            self.set_side(self.directional_sprite.get_side_for_theta(theta))

            self.sprite.update_pos([self.rect.x, self.rect.y])

        if SETTINGS.all_sprites[self.num] != self.sprite:
            SETTINGS.all_sprites[self.num] = self.sprite

        # Find out what x and y coordinates would change
        if self.face == 90:
            self.front_tile = (0, -1)
        elif self.face == 180:
            self.front_tile = (-1, 0)
        elif self.face == 270:
            self.front_tile = (0, 1)
        elif self.face == 0 or self.face == 360:
            self.front_tile = (1, 0)

    def get_theta(self, xpos: float, ypos: float):
        """
        Calculate the theta, postheta, and side for the NPC
        :param xpos:
        :param ypos:
        :return:
        """
        theta = math.atan2(-ypos, xpos) % (2 * math.pi)
        theta = math.degrees(theta)

        self.postheta = theta
        theta -= self.face

        if theta < 0:
            theta += 360
        elif theta > 360:
            theta -= 360

        self.theta = theta
        self.set_side(self.directional_sprite.get_side_for_theta(theta))

        return theta

    def set_side(self, side: NpcSide):
        # this function assumes we only have one player
        # this and host of other will have to change if
        # that changes
        self.player_in_view = side.player_in_view

        # all of these conditions must be met
        # if we are going to change the sprite
        change_sprite_rules = [
            self.side != side.name,
            not self.dead,
            not self.hurting,
            not self.attacking,
            self.in_canvas
        ]

        if all(change_sprite_rules) or not self.side:
            self.side = side

            # self.sprite.texture = self.directional_sprite.animate(
            #    self.running_animation,
            #    self.side,
            #    self.sprite.current_frame
            # )

        return self.side

    def round_up(self, a):
        return int(a + 0.5)

    def detect_player(self) -> bool:
        """
        == Is player visible from NPC position? ==
        detect_player(self) -> boolean

        :return: bool
        """

        own_tile = self.map_pos
        # front_tile = [own_tile[0] + self.front_tile[0], own_tile[1] + self.front_tile[1]]
        player_tile = SETTINGS.player_map_pos

        # DDA Algorithm
        x1, y1 = own_tile[0], own_tile[1]
        x2, y2 = player_tile[0], player_tile[1]

        # If the coords are negative, start from player instead of NPC
        if x1 > x2 or (x1 == x2 and y1 > y2):
            temp1, temp2 = x1, y1
            x1, y1 = x2, y2
            x2, y2 = temp1, temp2

        x, y = x1, y1
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        length = dx if dx > dy else dy
        # Make sure, you won't divide by 0
        if length == 0:
            length = 0.001

        xinc = (x2 - x1) / float(length)
        yinc = (y2 - y1) / float(length)
        mapx = self.round_up(x)
        mapy = self.round_up(y)

        # Extend DDA algorithm
        for i in range(int(length)):
            if i > SETTINGS.render:
                break
            x += xinc
            y += yinc
            mapx = self.round_up(x)
            mapy = self.round_up(y)

            # If line of sight hits a wall
            next_wall = [tile for tile in self.dda_list if tile.map_pos == [mapx, mapy]]

            if not next_wall:
                break
            else:
                next_wall = next_wall[0]

            if SETTINGS.tile_visible[next_wall.ID]:
                if next_wall.type != 'hdoor' and next_wall.type != 'vdoor':
                    break
                elif next_wall.type == 'hdoor' or next_wall.type == 'vdoor':
                    if next_wall.solid:
                        break
            # if player is spotted
            if mapx == x2 and mapy == y2:
                return True
        if self.dist <= SETTINGS.tile_size / 3:
            return True

    def collide_update(self, x: float, y: float) -> None:
        """
        Make sure the NPC doesn't walk inside stuff
        :param x:
        :param y:
        :return:
        """

        self.real_x += x * SETTINGS.dt
        self.real_y += y * SETTINGS.dt
        self.rect.x = self.real_x
        self.rect.y = self.real_y

        if self.collide_list[-1] != SETTINGS.player:
            self.collide_list.append(SETTINGS.player)
        else:
            self.collide_list[-1] = SETTINGS.player

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

    def move(self) -> None:
        """
        Make the NPC move according to current state.
        :return:
        """

        moving_up = False
        moving_down = False
        moving_right = False
        moving_left = False

        if self.path and self.rect.center != self.path[-1].rect.center and self.health > 0 and not self.hurting:
            self.moving = True

            # Redo path if tile is occupied by another NPC.
            if self.update_timer <= 0.5:
                for npc in SETTINGS.npc_list:
                    if npc.map_pos == self.path[-1].map_pos:
                        available_pos = [x for x in SETTINGS.walkable_area if
                                         abs(x.map_pos[0] - self.map_pos[0]) <= 3 and abs(
                                             x.map_pos[1] - self.map_pos[1]) <= 3]
                        self.path = PATHFINDING.pathfind(self.map_pos, random.choice(available_pos).map_pos)
                        self.path_progress = 0
                        break

            if self.rect.colliderect(self.path[self.path_progress].rect) and self.path[self.path_progress] != self.path[
                -1]:
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
                        self.face = 90
                    elif moving_right:
                        self.face = 45
                    elif moving_left:
                        self.face = 135

                elif moving_down:
                    if not moving_right and not moving_left:
                        self.face = 270
                    elif moving_right:
                        self.face = 315
                    elif moving_left:
                        self.face = 225

                elif moving_left:
                    self.face = 180

                elif moving_right:
                    self.face = 0

        else:
            self.moving = False
            self.attack_move = False
            if self.timer >= self.frame_interval:
                self.path = []
                self.path_progress = 0

        if self.state == NpcState.PATROLLING:
            if self.path == []:
                if random.randint(0, 3) == 3:
                    self.state = NpcState.IDLE
                    # self.sprite.texture = self.stand_texture[4]
                else:
                    # Make the NPC not walk too far.
                    available_pos = [x for x in SETTINGS.walkable_area if
                                     abs(x.map_pos[0] - self.map_pos[0]) <= 3 and abs(
                                         x.map_pos[1] - self.map_pos[1]) <= 3]
                    self.path = PATHFINDING.pathfind(self.map_pos, random.choice(available_pos).map_pos)

        elif self.state == NpcState.FLEEING:
            if self.dist <= SETTINGS.tile_size * 4:
                flee_pos = random.choice(SETTINGS.walkable_area)
                player_tile = [x for x in SETTINGS.walkable_area if x.map_pos == SETTINGS.player_map_pos]
                if player_tile:
                    player_tile = player_tile[0]
                else:
                    player_tile = PATHFINDING.find_near_position(SETTINGS.player_map_pos)

                if self.player_in_view:
                    if self.detect_player and player_tile:
                        if ((SETTINGS.walkable_area.index(flee_pos) < SETTINGS.walkable_area.index(player_tile) + int(
                                    SETTINGS.current_level_size[0] / 5)) or (
                            SETTINGS.walkable_area.index(flee_pos) > SETTINGS.walkable_area.index(player_tile) - int(
                                    SETTINGS.current_level_size[0] / 5))) and self.path == []:
                            self.path_progress = 0
                            self.path = PATHFINDING.pathfind(self.map_pos, flee_pos.map_pos)

    def idle(self) -> None:
        """
        Make the NPC rotate randomly as it stands still.
        :return:
        """

        self.idle_timer += SETTINGS.dt
        if self.idle_timer >= 3:
            if random.randint(0, 2) == 2:
                self.face += 45
            elif random.randint(0, 2) == 2:
                self.face -= 45
            if self.face >= 360:
                self.face -= 360
            self.idle_timer = 0

            # Do only change to patrolling if it was that in the first place.
            if self.OG_state != NpcState.IDLE:
                if random.randint(0, 2) == 2:
                    self.state = NpcState.PATROLLING

        # Make NPC react to gunshot if close. Or just if the player is too close.
        if (self.dist <= SETTINGS.tile_size * 4 and SETTINGS.mouse_btn_active and SETTINGS.current_gun) or \
                        self.dist <= self.rect.width:

            self.face = self.face + self.theta
            if self.face >= 360:
                self.face -= 360
            self.face = min([0, 90, 180, 270, 359], key=lambda x: abs(x - self.face))

    def attack(self) -> None:
        """
        Attack current target (player). Includes moving into position for attack
        :return:
        """

        if self.attack_move:
            self.move()
        else:
            if self.atcktype == 'melee':
                # Move close to player and keep attacking
                if self.dist <= SETTINGS.tile_size * 0.7:
                    self.path = []
                    self.moving = False
                    if not self.attacking:
                        if self.timer >= self.frame_interval * self.atckrate:
                            self.attacking = True
                            self.timer = 0
                    else:
                        # Make the NPC not flinch when attacking
                        if self.hurting:
                            if random.randint(0, 2) != 2 or self.attacking:
                                self.animate(NpcAnimation.ATTACKING)
                                self.hurting = False
                                if random.randint(0, 2) == 2:
                                    SOUND.play_sound(random.choice(self.sounds['damage']), self.dist)
                        else:
                            self.animate(NpcAnimation.ATTACKING)

                else:
                    if self.dist > SETTINGS.tile_size * 0.7 and self.path == []:
                        self.path_progress = 0
                        self.path = PATHFINDING.pathfind(self.map_pos, SETTINGS.player_map_pos)

                    elif self.path != []:
                        try:
                            if self.path[-1].map_pos != SETTINGS.player_map_pos:
                                if self.dist <= (SETTINGS.render / 2) * SETTINGS.tile_size and random.randint(0,
                                                                                                              5) == 5:
                                    self.path_progress = 0
                                    self.path = PATHFINDING.pathfind(self.map_pos, SETTINGS.player_map_pos)
                                elif random.randint(0, 10) >= 8:
                                    self.path_progress = 0
                                    self.path = PATHFINDING.pathfind(self.map_pos, SETTINGS.player_map_pos)
                            else:
                                self.move()
                        except:
                            pass

            elif self.atcktype == 'hitscan':
                # Move somewhat close to player and change position after attacking
                if self.dist <= SETTINGS.tile_size * self.range and (self.dist >= SETTINGS.tile_size * 1.5 or (
                    SETTINGS.current_gun and SETTINGS.current_gun.guntype == 'melee')) and not self.attack_move:
                    self.path = []
                    self.moving = False
                    if not self.attacking:
                        if random.randint(0, self.atckchance) == 5 and self.detect_player:
                            self.attacking = True
                            self.atckchance += int(self.atckrate)
                            self.movechance = 10
                        else:
                            if random.randint(0, self.movechance) == 10:
                                move_pos = random.choice([x for x in SETTINGS.walkable_area if (
                                x.map_pos[0] <= self.map_pos[0] + 1 and x.map_pos[0] >= self.map_pos[0] - 1) and (
                                                          x.map_pos[1] <= self.map_pos[1] + 1 and x.map_pos[1] >=
                                                          self.map_pos[1] - 1)])
                                self.path_progress = 0
                                self.path = PATHFINDING.pathfind(self.map_pos, move_pos.map_pos)
                                self.attacking = False
                                self.attack_move = True
                                # This variable is to make sure the NPC doesn't just walk around without attacking.
                                self.movechance += 3
                                self.atckchance = 5

                    # There is a chance the NPC will not flinch when shot while attacking
                    elif self.attacking:
                        if self.hurting:
                            if random.randint(0, 5) >= 3:
                                self.animate(NpcAnimation.ATTACKING)
                                self.hurting = False
                                if random.randint(0, 2) == 2:
                                    SOUND.play_sound(random.choice(self.sounds['damage']), self.dist)
                        else:
                            self.animate(NpcAnimation.ATTACKING)

                # Move away from player if too close
                elif self.dist < SETTINGS.tile_size * 1.5 and self.health <= 6:
                    if self.rect.centerx > SETTINGS.player_rect.centerx:
                        self.collide_update(self.speed, 0)
                        self.animate(NpcAnimation.WALKING)
                    elif self.rect.centerx < SETTINGS.player_rect.centerx:
                        self.collide_update(-self.speed, 0)
                        self.animate(NpcAnimation.WALKING)
                    if self.rect.centery > SETTINGS.player_rect.centery:
                        self.collide_update(0, self.speed)
                        self.animate(NpcAnimation.WALKING)
                    elif self.rect.centery < SETTINGS.player_rect.centery:
                        self.collide_update(0, -self.speed)
                        self.animate(NpcAnimation.WALKING)

                else:
                    if not self.attack_move:
                        if self.dist >= SETTINGS.tile_size * 2.5 and self.path == []:
                            self.path_progress = 0
                            self.path = PATHFINDING.pathfind(self.map_pos, SETTINGS.player_map_pos)

                        elif self.path != []:
                            try:
                                if self.path[-1].map_pos != SETTINGS.player_map_pos:
                                    if self.dist <= (SETTINGS.render / 2) * SETTINGS.tile_size and random.randint(0,
                                                                                                                  5) == 5:
                                        self.path_progress = 0
                                        self.path = PATHFINDING.pathfind(self.map_pos, SETTINGS.player_map_pos)
                                    elif random.randint(0, 10) == 10:
                                        self.path_progress = 0
                                        self.path = PATHFINDING.pathfind(self.map_pos, SETTINGS.player_map_pos)
                                else:
                                    self.move()
                            except:
                                pass

    def animate(self, animation: NpcAnimation) -> None:
        """
        == Animate NPC ==
        animation -> dying, walking, attacking, hurting

        :param animation:
        :return:
        """

        if self.running_animation != animation:
            self.sprite.current_frame = 0
            self.running_animation = animation

        self.sprite.texture, next_frame = self.directional_sprite.animate(
            animation, self.side, self.sprite.current_frame
        )

        # walk animation
        if animation == NpcAnimation.WALKING:
            if self.timer >= self.frame_interval:
                self.sprite.current_frame = next_frame
                self.timer = 0

        # die animation
        elif animation == NpcAnimation.DYING:

            if self.sprite.current_frame == 0 and not self.mein_leben:
                self.mein_leben = True
                SOUND.play_sound(random.choice(self.sounds['die']), self.dist)
            if self.timer >= self.frame_interval and next_frame > self.sprite.current_frame:
                self.sprite.current_frame = next_frame
                self.timer = 0
            elif self.sprite.current_frame == next_frame and self.knockback == 0:
                self.dead = True
                self.drop_item()
                SETTINGS.statistics['last enemies'] += 1
            elif self.knockback > 0:
                self.collide_update(-math.cos(math.radians(self.postheta)) * self.knockback, 0)
                self.collide_update(0, math.sin(math.radians(self.postheta)) * self.knockback)
                self.knockback = int(self.knockback * 0.8)

        # hurt animation
        elif animation == NpcAnimation.HURTING:

            self.moving = False
            self.sprite.current_frame = next_frame

            if self.timer >= self.frame_interval * 2:
                self.side = None
                self.hurting = False
                self.timer = 0
                SOUND.play_sound(random.choice(self.sounds['damage']), self.dist)
                if self.state == NpcState.IDLE or self.state == NpcState.PATROLLING or self.state == NpcState.FLEEING:
                    self.face = self.face + self.theta
                    if self.face >= 360:
                        self.face -= 360
                    self.face = min([0, 90, 180, 270, 359], key=lambda x: abs(x - self.face))

        # attack animation
        elif animation == NpcAnimation.ATTACKING:
            self.moving = False
            if self.timer >= self.frame_interval:
                self.sprite.current_frame = next_frame
                self.timer = 0
                if self.sprite.current_frame == -1:
                    SOUND.play_sound(self.sounds['attack'], self.dist)
                    self.sprite.texture = self.directional_sprite.default()
                    self.sprite.current_frame = 0
                    self.attacking = False
                    if random.randint(0, 8) != 8:  # A chance to miss
                        if SETTINGS.player_armor > 0:
                            SETTINGS.player_health -= int(self.dmg * 0.65)
                            if SETTINGS.player_armor >= self.dmg * 2:
                                SETTINGS.player_armor -= self.dmg * 2
                            else:
                                SETTINGS.player_armor = 0
                        else:
                            SETTINGS.player_health -= self.dmg

    def drop_item(self) -> None:
        """
        Drop an item an add it to the game map
        :return:
        """
        # TODO: Move this out of NPC

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
        SETTINGS.all_items.append(ITEMS.Item(self.map_pos, os.path.join('graphics', 'items', texture), drop, effect))

# pos is in tiles, face in degrees, frame_interval is seconds between frames, speed is pixels/second

# stats = {
#    'pos': [tile pos],
#    'face': degrees,
#    'spf': seconds per frame (float),
#    'dmg': damage on player,
#    'health' : health points,
#    'speed': pixels per second,
#    'mind': string -> hostile, passive, shy,
#    'state': string -> idle, patrolling,
#    'atcktype': string -> melee, hitscan, # TODO: create attacktype enum
#    'atckrate': chance of attacking - lower = faster
#    'id' : unique ID for npcs,
#    'filepath' : ('folder', 'folder', 'file.ext'),
#    'npc_name' : 'name' -> Used for connecting to a sound pack.
#    },
