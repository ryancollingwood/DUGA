import SPRITES
import SOUND
import pygame
import os

import consts.geom
import consts.tile
import gamestate.inventory
import gamestate.player
import gamestate.sprites


class Item:

    def __init__(self, pos, sprite, item_type, effect):
        '''Item that can be picked up by the player\npos -> tile pos | sprite -> texture path | item_type -> health, armor, *ammo*, gun\neffect -> relative'''
        self.pos = (pos[0] * consts.tile.TILE_SIZE, pos[1] * consts.tile.TILE_SIZE)
        self.map_pos = pos
        self.item_type = item_type
        self.rect = pygame.Rect(self.pos[0], self.pos[1], int(consts.tile.TILE_SIZE), int(consts.tile.TILE_SIZE))
        self.rect.center = (self.pos[0] + consts.tile.TILE_SIZE / 2, self.pos[1] + consts.tile.TILE_SIZE / 2)
        self.sprite = SPRITES.Sprite(pygame.image.load(sprite), hash(item_type), self.rect.center, 'sprite')
        self.effect = effect
        self.sound = pygame.mixer.Sound(os.path.join('sounds', 'other', 'blub.ogg'))
        
    def update(self):
        remove = False
        if self.rect:
            if gamestate.player.player_rect.colliderect(self.rect):
                if self.item_type == 'health':
                    if gamestate.player.player_health < 100:
                        gamestate.player.player_health += self.effect
                        if gamestate.player.player_health > 100:
                            gamestate.player.player_health = 100
                        gamestate.player.player_states['heal'] = True
                        remove = True
                    
                elif self.item_type == 'armor':
                    if gamestate.player.player_armor < 100:
                        gamestate.player.player_armor += self.effect
                        if gamestate.player.player_armor > 100:
                            gamestate.player.player_armor = 100
                        gamestate.player.player_states['armor'] = True
                        remove = True

                elif self.item_type == 'bullet' or self.item_type == 'shell' or self.item_type == 'ferromag':
                    if gamestate.inventory.held_ammo[self.item_type] < gamestate.inventory.max_ammo[self.item_type]:
                        gamestate.inventory.held_ammo[self.item_type] += self.effect
                        if gamestate.inventory.held_ammo[self.item_type] > gamestate.inventory.max_ammo[self.item_type]:
                            gamestate.inventory.held_ammo[self.item_type] = gamestate.inventory.max_ammo[self.item_type]
                        #Same effect as armor
                        gamestate.player.player_states['armor'] = True
                        remove = True

                elif self.item_type == 'primary':
                    if not gamestate.inventory.held_weapons['primary']:
                        gamestate.inventory.held_weapons['primary'] = self.effect
                        gamestate.inventory.next_gun = self.effect
                        gamestate.player.player_states['armor'] = True
                        remove = True
                    else:
                        gamestate.inventory.ground_weapon = self.effect

                elif self.item_type == 'secondary':
                    if not gamestate.inventory.held_weapons['secondary']:
                        gamestate.inventory.held_weapons['secondary'] = self.effect
                        gamestate.inventory.next_gun = self.effect
                        gamestate.player.player_states['armor'] = True
                        remove = True
                    else:
                        gamestate.inventory.ground_weapon = self.effect

                elif self.item_type == 'melee':
                    if not gamestate.inventory.held_weapons['melee']:
                        gamestate.inventory.held_weapons['melee'] = self.effect
                        gamestate.inventory.next_gun = self.effect
                        gamestate.player.player_states['armor'] = True
                        remove = True
                    else:
                        gamestate.inventory.ground_weapon = self.effect
                            
                #Remove sprite and rect
                if self.sprite in gamestate.sprites.all_sprites and remove:
                    SOUND.play_sound(self.sound, 0)
                    gamestate.sprites.all_sprites.remove(self.sprite)
                    self.rect = None
