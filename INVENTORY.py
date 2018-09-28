#This class / script is not a part of the engine itself. This means it will not
#Be as easy to modify as the other parts. (As if they were easy)
import SETTINGS
import TEXT
import ITEMS
import pygame
import os

import consts.colours
import gamedata.items
import gamedata.tiles
import gamestate.inventory
import gamestate.items
import gamestate.player


class inventory:
    
    #ammo_dict is dict with the max amout of each type of ammo.
    def __init__(self, ammo_dict):
        self.bg = pygame.image.load(os.path.join('graphics', 'inventory.png')).convert_alpha()
        self.rect = self.bg.get_rect()
        self.rect.center = (int(SETTINGS.canvas_actual_width/2), int(SETTINGS.canvas_target_height/2))
        
        self.held_ammo = {}
        for x in ammo_dict:
            self.held_ammo[x] = 0

        gamestate.inventory.held_ammo = self.held_ammo
        gamestate.inventory.max_ammo = ammo_dict

        #Menu
        self.menu = pygame.Surface((160, 220)).convert()
        self.menu_rect = self.menu.get_rect()
        self.menudraw = False
        self.selected = None

        self.submenus = []
        self.submenu_rects = []

        for i in range(0, 10):
            if i == 0 or i == 9:
                self.submenus.append(self.menu.subsurface(0, 0, self.menu_rect.width, 30).convert())
                self.submenu_rects.append(self.submenus[i].get_rect())
            else:
                self.submenus.append(self.menu.subsurface(0, 0, self.menu_rect.width, 20).convert())
                self.submenu_rects.append(self.submenus[i].get_rect())
            
            if i % 2 == 0:
                self.submenus[i].fill((65,65,65))
            else:
                self.submenus[i].fill((55,55,55))
        
        #Close button
        self.closebtn = pygame.Surface((176, 64)).convert_alpha()
        self.closebtn_rect = self.closebtn.get_rect()
        self.closebtn_rect.topleft = (self.rect.x + 353, self.rect.y + 353)
        self.closebtn.fill((100,100,100,100))

        #Primary weapon
        self.primaryslot = pygame.Surface((272, 80)).convert_alpha()
        self.primaryslot_rect = self.primaryslot.get_rect()
        self.primaryslot_rect.topleft = (self.rect.x + 33, self.rect.y + 33)
        self.primaryslot.fill((100,100,100,100))

        #Secondary weapon
        self.secondslot = pygame.Surface((176, 81)).convert_alpha()
        self.secondslot_rect = self.secondslot.get_rect()
        self.secondslot_rect.topleft = (self.rect.x + 33, self.rect.y + 129)
        self.secondslot.fill((100,100,100,100))

        #Melee weapon
        self.meleeslot = pygame.Surface((176, 81)).convert_alpha()
        self.meleeslot_rect = self.meleeslot.get_rect()
        self.meleeslot_rect.topleft = (self.rect.x + 33, self.rect.y + 225)
        self.meleeslot.fill((100,100,100,100))

        #Ammo textures
        self.ammotexture1 = pygame.image.load(os.path.join(*[x for x in gamedata.items.item_types if x['type'] == 'bullet'][0]['filepath'])).subsurface(0, 112, 64, 16).convert_alpha()
        self.ammotexture2 = pygame.image.load(os.path.join(*[x for x in gamedata.items.item_types if x['type'] == 'shell'][0]['filepath'])).subsurface(0, 112, 64, 16).convert_alpha()
        self.ammotexture3 = pygame.image.load(os.path.join(*[x for x in gamedata.items.item_types if x['type'] == 'ferromag'][0]['filepath'])).subsurface(0, 112, 64, 16).convert_alpha()

        self.ammotexture1 = pygame.transform.scale(self.ammotexture1, (128, 32))
        self.ammotexture2 = pygame.transform.scale(self.ammotexture2, (128, 32))
        self.ammotexture3 = pygame.transform.scale(self.ammotexture3, (128, 32))
        

        #Ammo 1
        self.ammoslot1 = pygame.Surface((191,79)).convert_alpha()
        self.ammoslot1_rect = self.ammoslot1.get_rect()
        self.ammoslot1_rect.topleft = (self.rect.x + 320, self.rect.y + 33)
        self.ammoslot1.fill((100,100,100,100))

        #Ammo 2
        self.ammoslot2 = pygame.Surface((191,79)).convert_alpha()
        self.ammoslot2_rect = self.ammoslot2.get_rect()
        self.ammoslot2_rect.topleft = (self.rect.x + 320, self.rect.y + 129)
        self.ammoslot2.fill((100,100,100,100))

        #Ammo 3
        self.ammoslot3 = pygame.Surface((191,79)).convert_alpha()
        self.ammoslot3_rect = self.ammoslot3.get_rect()
        self.ammoslot3_rect.topleft = (self.rect.x + 320, self.rect.y + 225)
        self.ammoslot3.fill((100,100,100,100))

        #Ground weapon
        self.groundslot = pygame.Surface((272, 80)).convert_alpha()
        self.groundslot_rect = self.groundslot.get_rect()
        self.groundslot_rect.topleft = (self.rect.x + 33, self.rect.y + 336)
        self.groundslot.fill((100,100,100,75))

        #Stuff
        self.mousepos = pygame.mouse.get_pos()
        self.timer = 0
        self.closing = False
        self.text = [TEXT.Text(0, 0, 'NAME', consts.colours.WHITE, 'DUGAFONT.ttf', 18),
                     TEXT.Text(0, 0, 'DAMAGE: --', consts.colours.LIGHTGRAY, 'DUGAFONT.ttf', 15),
                     TEXT.Text(0, 0, 'SPREAD: --', consts.colours.LIGHTGRAY, 'DUGAFONT.ttf', 15),
                     TEXT.Text(0, 0, 'ACCURACY: --', consts.colours.LIGHTGRAY, 'DUGAFONT.ttf', 15),
                     TEXT.Text(0, 0, 'RANGE: --', consts.colours.LIGHTGRAY, 'DUGAFONT.ttf', 15),
                     TEXT.Text(0, 0, 'MAGAZINE SIZE: --', consts.colours.LIGHTGRAY, 'DUGAFONT.ttf', 15),
                     TEXT.Text(0, 0, 'RELOAD TIME: --', consts.colours.LIGHTGRAY, 'DUGAFONT.ttf', 15),
                     TEXT.Text(0, 0, 'FIRE RATE: --', consts.colours.LIGHTGRAY, 'DUGAFONT.ttf', 15),
                     TEXT.Text(0, 0, 'AMMO TYPE: --', consts.colours.LIGHTGRAY, 'DUGAFONT.ttf', 15),
                     TEXT.Text(0, 0, 'DROP', consts.colours.WHITE, 'DUGAFONT.ttf', 18)]
        
        self.ammotext = [TEXT.Text(480, 116, '-- / --', consts.colours.DARKGRAY, 'DUGAFONT.ttf', 24),
                         TEXT.Text(480, 212, '-- / --', consts.colours.DARKGRAY, 'DUGAFONT.ttf', 24),
                         TEXT.Text(480, 308, '-- / --', consts.colours.DARKGRAY, 'DUGAFONT.ttf', 24)]

    def draw(self, canvas):
        canvas.blit(self.bg, self.rect)
        self.timer += SETTINGS.dt

        #Ammo text
        if gamestate.inventory.held_ammo['bullet'] and not gamestate.inventory.inv_strings_updated:
            self.ammotext[0].update_string('%s / %s' % (
            gamestate.inventory.held_ammo['bullet'], gamestate.inventory.max_ammo['bullet']))
        if gamestate.inventory.held_ammo['shell'] and not gamestate.inventory.inv_strings_updated:
            self.ammotext[1].update_string('%s / %s' % (
            gamestate.inventory.held_ammo['shell'], gamestate.inventory.max_ammo['shell']))
        if gamestate.inventory.held_ammo['ferromag'] and not gamestate.inventory.inv_strings_updated:
            self.ammotext[2].update_string('%s / %s' % (
            gamestate.inventory.held_ammo['ferromag'], gamestate.inventory.max_ammo['ferromag']))
        for string in self.ammotext:
            string.draw(canvas)
        gamestate.inventory.inv_strings_updated = True
        

        #Mouse on close button
        if self.closebtn_rect.collidepoint(pygame.mouse.get_pos()):
            canvas.blit(self.closebtn, self.closebtn_rect)
            if pygame.mouse.get_pressed()[0]:
                self.timer = 0
                self.closing = True
                
        #Mouse on primary
        elif self.primaryslot_rect.collidepoint(pygame.mouse.get_pos()) and (not self.menudraw or self.selected == 'primary'):
            canvas.blit(self.primaryslot, self.primaryslot_rect)
            self.selected = 'primary'
            if pygame.mouse.get_pressed()[0] and gamestate.inventory.held_weapons['primary']:
                self.menudraw = True
                self.mousepos = pygame.mouse.get_pos()
                
        #Mouse on secondary
        elif self.secondslot_rect.collidepoint(pygame.mouse.get_pos()) and (not self.menudraw or self.selected == 'secondary'):
            canvas.blit(self.secondslot, self.secondslot_rect)
            self.selected = 'secondary'
            if pygame.mouse.get_pressed()[0] and gamestate.inventory.held_weapons['secondary']:
                self.menudraw = True
                self.mousepos = pygame.mouse.get_pos()
            
        #Mouse on melee
        elif self.meleeslot_rect.collidepoint(pygame.mouse.get_pos()) and (not self.menudraw or self.selected == 'melee'):
            canvas.blit(self.meleeslot, self.meleeslot_rect)
            self.selected = 'melee'
            if pygame.mouse.get_pressed()[0] and gamestate.inventory.held_weapons['melee']:
                self.menudraw = True
                self.mousepos = pygame.mouse.get_pos()

        #Mouse on ground weapon slot
        elif self.groundslot_rect.collidepoint(pygame.mouse.get_pos()) and (not self.menudraw or self.selected == 'ground') and not (self.submenu_rects[-1].collidepoint(pygame.mouse.get_pos()) and self.menudraw):
            canvas.blit(self.groundslot, self.groundslot_rect)
            self.selected = 'ground'
            if pygame.mouse.get_pressed()[0] and gamestate.inventory.ground_weapon:
                self.menudraw = True
                self.mousepos = pygame.mouse.get_pos()
            

        #Mouse on ammo1 - run function
        elif self.ammoslot1_rect.collidepoint(pygame.mouse.get_pos()):
            self.ammo_selection(1, canvas)

        #Mouse on ammo2 - run function
        elif self.ammoslot2_rect.collidepoint(pygame.mouse.get_pos()):
            self.ammo_selection(2, canvas)

        #Mouse on ammo3 - run function
        elif self.ammoslot3_rect.collidepoint(pygame.mouse.get_pos()):
            self.ammo_selection(3, canvas)

        #Mouse on menu
        elif self.menu_rect.collidepoint(pygame.mouse.get_pos()) and self.menudraw:
            self.menudraw = True
            
        else:
            self.menudraw = False
            self.selected = None

        #Draw items - high layer
        if gamestate.inventory.held_weapons['primary']:
            canvas.blit(gamestate.inventory.held_weapons['primary'].subitemtexture, (self.primaryslot_rect.x, self.primaryslot_rect.y + 5))
        if gamestate.inventory.held_weapons['secondary']:
            canvas.blit(gamestate.inventory.held_weapons['secondary'].subitemtexture, (self.secondslot_rect.x - self.secondslot_rect.width / 4, self.secondslot_rect.y))
        if gamestate.inventory.held_weapons['melee']:
            canvas.blit(gamestate.inventory.held_weapons['melee'].subitemtexture, (self.meleeslot_rect.x - self.secondslot_rect.width / 4, self.meleeslot_rect.y))
        if gamestate.inventory.ground_weapon:
            canvas.blit(gamestate.inventory.ground_weapon.subitemtexture, (self.groundslot_rect.x, self.groundslot_rect.y + 5))
        #Ammo
        if gamestate.inventory.held_ammo['bullet']:
            canvas.blit(self.ammotexture1, (self.ammoslot1_rect.x - self.ammoslot1_rect.width/8, self.ammoslot1_rect.y + 20))
        if gamestate.inventory.held_ammo['shell']:
            canvas.blit(self.ammotexture2, (self.ammoslot2_rect.x - self.ammoslot2_rect.width/8, self.ammoslot2_rect.y + 20))
        if gamestate.inventory.held_ammo['ferromag']:
            canvas.blit(self.ammotexture3, (self.ammoslot3_rect.x - self.ammoslot3_rect.width/8, self.ammoslot3_rect.y + 20))

        #Draw menu top layer
        if (self.menudraw and gamestate.inventory.ground_weapon) or (self.menudraw and gamestate.inventory.held_weapons[self.selected]):
            self.draw_menu(canvas)

        #Close menu without shooting
        if self.closing and self.timer >= 0.2:
            gamestate.player.player_states['invopen'] = False
            self.closing = False
            self.timer = 0
            gamestate.inventory.inv_strings_updated = False


    def draw_menu(self, canvas):
        if self.selected != 'ground':
            self.menu_rect.topleft = self.mousepos

            #Draw menu
            i = 0
            for menu in self.submenus:
                if i == 0:
                    self.submenu_rects[i].topleft = (self.mousepos[0], self.mousepos[1])
                else:
                    self.submenu_rects[i].topleft = (self.mousepos[0], self.mousepos[1]+i*20+10)
                canvas.blit(menu, self.submenu_rects[i])            
                i += 1

            #Update weapon stats  -  updates strings, even though it is not needed. Might want to change later, if needed.
            if gamestate.inventory.held_weapons[self.selected]:
                self.text[0].update_string('%s' % gamestate.inventory.held_weapons[self.selected].name)
                self.text[1].update_string('DAMAGE            : %s' % gamestate.inventory.held_weapons[self.selected].dmg)
                self.text[2].update_string('SPREAD              : %s' % gamestate.inventory.held_weapons[self.selected].accuracy)
                self.text[3].update_string('ACCURACY    : %s / 100' % gamestate.inventory.held_weapons[self.selected].hit_percent)
                self.text[4].update_string('RANGE                 : %s' % gamestate.inventory.held_weapons[self.selected].range)
                self.text[5].update_string('MAG SIZE      : %s' % gamestate.inventory.held_weapons[self.selected].mag_size)
                self.text[6].update_string('REL TIME      : %s' % gamestate.inventory.held_weapons[self.selected].rlspeed)
                self.text[7].update_string('FIR RATE      : %s' % gamestate.inventory.held_weapons[self.selected].firerate)
                self.text[8].update_string('AMMO TYP  : %s' % gamestate.inventory.held_weapons[self.selected].ammo_type)
                self.text[9].update_string('DROP')            

            #Update text
            x = 0
            for string in self.text:
                if x == 0:
                    string.update_pos(self.mousepos[0]+5, self.mousepos[1]+8)
                elif x == 9:
                    string.update_pos(self.mousepos[0]+55, self.mousepos[1]+x*20+15)
                else:
                    string.update_pos(self.mousepos[0]+5, self.mousepos[1]+x*20+12)
                string.draw(canvas)
                x += 1

        else:
            self.menu_rect.bottomleft = self.mousepos

            #Draw menu
            i = 0
            for menu in self.submenus:
                if i == 0:
                    self.submenu_rects[i].topleft = (self.mousepos[0], self.mousepos[1] - self.menu_rect.height)
                else:
                    self.submenu_rects[i].topleft = (self.mousepos[0], self.mousepos[1]+i*20+10 - self.menu_rect.height)
                canvas.blit(menu, self.submenu_rects[i])            
                i += 1
                
            self.text[0].update_string('%s' % gamestate.inventory.ground_weapon.name)
            self.text[1].update_string('DAMAGE            : %s   %s' % (
            gamestate.inventory.ground_weapon.dmg, self.compare_weapons('dmg')))
            self.text[2].update_string('SPREAD              : %s   %s' % (
            gamestate.inventory.ground_weapon.accuracy, self.compare_weapons('spr')))
            self.text[3].update_string('ACCURACY    : %s / 100   %s' % (
            gamestate.inventory.ground_weapon.hit_percent, self.compare_weapons('acc')))
            self.text[4].update_string('RANGE                 : %s   %s' % (
            gamestate.inventory.ground_weapon.range, self.compare_weapons('ran')))
            self.text[5].update_string('MAG SIZE      : %s   %s' % (
            gamestate.inventory.ground_weapon.mag_size, self.compare_weapons('mag')))
            self.text[6].update_string('REL TIME      : %s   %s' % (
            gamestate.inventory.ground_weapon.rlspeed, self.compare_weapons('rel')))
            self.text[7].update_string('FIR RATE      : %s   %s' % (
            gamestate.inventory.ground_weapon.firerate, self.compare_weapons('fir')))
            self.text[8].update_string('AMMO TYP  : %s' % gamestate.inventory.ground_weapon.ammo_type)
            self.text[9].update_string('SWAP')

            #Update text
            x = 0
            for string in self.text:
                if x == 0:
                    string.update_pos(self.mousepos[0]+5, self.mousepos[1]+8 - self.menu_rect.height)
                elif x == 9:
                    string.update_pos(self.mousepos[0]+55, self.mousepos[1]+x*20+15 - self.menu_rect.height)
                else:
                    string.update_pos(self.mousepos[0]+5, self.mousepos[1]+x*20+12 - self.menu_rect.height)
                string.draw(canvas)
                x += 1

        #Drop weapon
        if self.submenu_rects[-1].collidepoint(pygame.mouse.get_pos()):
            self.submenus[-1].fill((45,45,45))
            if pygame.mouse.get_pressed()[0] and self.timer >= 0.5:
                self.timer = 0
                #Find a place to drop item
                if [x for x in SETTINGS.all_tiles if x.map_pos == [gamestate.player.player_map_pos[0] + 1, gamestate.player.player_map_pos[1]] and not gamedata.tiles.tile_solid[x.ID]] and not [x for x in
                                                                                                                                                                                                 gamestate.items.all_items
                                                                                                                                                                                                 if x.map_pos == [
                        gamestate.player.player_map_pos[0] + 1, gamestate.player.player_map_pos[1]]]:
                    itempos = [gamestate.player.player_map_pos[0] + 1, gamestate.player.player_map_pos[1]]
                elif [x for x in SETTINGS.all_tiles if x.map_pos == [gamestate.player.player_map_pos[0] - 1, gamestate.player.player_map_pos[1]] and not gamedata.tiles.tile_solid[x.ID]] and not [x for x in
                                                                                                                                                                                                   gamestate.items.all_items
                                                                                                                                                                                                   if x.map_pos == [
                        gamestate.player.player_map_pos[0] - 1, gamestate.player.player_map_pos[1]]]:
                    itempos = [gamestate.player.player_map_pos[0] - 1, gamestate.player.player_map_pos[1]]
                elif [x for x in SETTINGS.all_tiles if x.map_pos == [gamestate.player.player_map_pos[0], gamestate.player.player_map_pos[1] + 1] and not gamedata.tiles.tile_solid[x.ID]] and not [x for x in
                                                                                                                                                                                                   gamestate.items.all_items
                                                                                                                                                                                                   if x.map_pos == [
                        gamestate.player.player_map_pos[0], gamestate.player.player_map_pos[1] + 1]]:
                    itempos = [gamestate.player.player_map_pos[0], gamestate.player.player_map_pos[1] + 1]
                elif [x for x in SETTINGS.all_tiles if x.map_pos == [gamestate.player.player_map_pos[0], gamestate.player.player_map_pos[1] - 1] and not gamedata.tiles.tile_solid[x.ID]] and not [x for x in
                                                                                                                                                                                                   gamestate.items.all_items
                                                                                                                                                                                                   if x.map_pos == [
                        gamestate.player.player_map_pos[0], gamestate.player.player_map_pos[1] - 1]]:
                    itempos = [gamestate.player.player_map_pos[0], gamestate.player.player_map_pos[1] - 1]
                else:
                    itempos = gamestate.player.player_map_pos
                if self.selected == 'ground':
                    self.selected = gamestate.inventory.ground_weapon.guntype
                gamestate.items.all_items.append(ITEMS.Item(itempos, gamestate.inventory.held_weapons[self.selected].itemtexture, gamestate.inventory.held_weapons[self.selected].guntype, gamestate.inventory.held_weapons[self.selected]))

                if gamestate.inventory.held_weapons[self.selected].ammo_type:
                    gamestate.inventory.held_ammo[gamestate.inventory.held_weapons[self.selected].ammo_type] += gamestate.inventory.current_gun.current_mag
                    gamestate.inventory.held_weapons[self.selected].current_mag = 0
                if self.selected == gamestate.inventory.current_gun or gamestate.inventory.next_gun:
                    gamestate.inventory.current_gun = None
                    gamestate.inventory.next_gun = None
                    
                gamestate.inventory.held_weapons[self.selected] = None
                gamestate.inventory.inv_strings_updated = False

        else:
            self.submenus[-1].fill((55,55,55))


    def ammo_selection(self, slot, canvas):
        bulletlist, shelllist, ferrolist = [], [], []
        
        if gamestate.inventory.held_weapons['primary']:
            if gamestate.inventory.held_weapons['primary'].ammo_type == 'bullet':
                bulletlist.append([self.primaryslot, self.primaryslot_rect])
            elif gamestate.inventory.held_weapons['primary'].ammo_type == 'shell':
                shelllist.append([self.primaryslot, self.primaryslot_rect])
            elif gamestate.inventory.held_weapons['primary'].ammo_type == 'ferromag':
                ferrolist.append([self.primaryslot, self.primaryslot_rect])

        if gamestate.inventory.held_weapons['secondary']:
            if gamestate.inventory.held_weapons['secondary'].ammo_type == 'bullet':
                bulletlist.append([self.secondslot, self.secondslot_rect])
            elif gamestate.inventory.held_weapons['secondary'].ammo_type == 'shell':
                shelllist.append([self.secondslot, self.secondslot_rect])
            elif gamestate.inventory.held_weapons['secondary'].ammo_type == 'ferromag':
                ferrolist.append([self.secondslot, self.secondslot_rect])
                
        if slot == 1:
            canvas.blit(self.ammoslot1, self.ammoslot1_rect)
            if gamestate.inventory.held_ammo['bullet']:
                for i in bulletlist:
                    canvas.blit(i[0], i[1])

        elif slot == 2:
            canvas.blit(self.ammoslot2, self.ammoslot2_rect)
            if gamestate.inventory.held_ammo['shell']:
                for i in shelllist:
                    canvas.blit(i[0], i[1])

        elif slot == 3:
            canvas.blit(self.ammoslot3, self.ammoslot3_rect)
            if gamestate.inventory.held_ammo['ferromag']:
                for i in ferrolist:
                    canvas.blit(i[0], i[1])
                    

    def compare_weapons(self, comp):
        stat = None
        if comp == 'dmg':
            stat = 'dmg'
        elif comp == 'spr':
            stat = 'spread'
        elif comp == 'acc':
            stat = 'hitchance'
        elif comp == 'ran':
            stat = 'range'
        elif comp == 'mag':
            stat = 'magsize'
        elif comp == 'rel':
            stat = 'rlspeed'
        elif comp == 'fir':
            stat = 'firerate'

        if gamestate.inventory.ground_weapon.stats[stat] > gamestate.inventory.held_weapons[
            gamestate.inventory.ground_weapon.guntype].stats[stat]:
            if stat != 'rlspeed' and stat != 'firerate':
                return '+'
            else:
                return '-'
        elif gamestate.inventory.ground_weapon.stats[stat] < gamestate.inventory.held_weapons[
            gamestate.inventory.ground_weapon.guntype].stats[stat]:
            if stat != 'rlspeed' and stat != 'firerate':
                return '-'
            else:
                return '+'
        else:
            return '='
            
            
            


            
                
            


#Ammo types: bullet, shell, ferromag
#gun types: primary, secondary, melee
