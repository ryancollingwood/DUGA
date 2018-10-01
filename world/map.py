import math
import random

import SETTINGS
import consts.tile
import gamedata.tiles
import gamestate.player
from .tile import Tile


#This is the script that controls the game maps. It makes the array and the tiles.
class Map:
    '''== Create the map ==\narray -> Level to be loaded'''
    def __init__(self, array):
        self.array = array
        self.tile_size = consts.tile.TILE_SIZE
        self.width = len(self.array[0])-1
        self.height = len(self.array)-1
        SETTINGS.current_level_size = (self.width, self.height)

        for row in range(len(self.array)):
            for column in range(len(self.array[row])):
                SETTINGS.all_tiles.append(
                    Tile(self.array[row][column], [column * self.tile_size, row * self.tile_size], [column, row]))

        for tile in SETTINGS.all_tiles:
            if gamedata.tiles.tile_solid[tile.ID]:
                SETTINGS.all_solid_tiles.append(tile)
            if tile.type == consts.tile.TRIGGER:
                SETTINGS.trigger_tiles.append(tile)

        #Add a tile that is always outside the walkable area (air)
        SETTINGS.all_tiles.append(
            Tile(0, [column + 1 * self.tile_size, row + 1 * self.tile_size], [column + 1, row + 1]))

    @staticmethod
    def draw(canvas):
        for tile in SETTINGS.all_solid_tiles:
            if gamedata.tiles.tile_visible[tile.ID]:
                tile.draw(canvas)

    @staticmethod
    def move_inaccessible_entities():
        wa = []
        for i in SETTINGS.walkable_area:
            if i.type != consts.tile.HORIZONTAL_DOOR and i.type != consts.tile.VERTICAL_DOOR:
                wa.append(i.map_pos)

        move_items = [x for x in SETTINGS.levels_list[SETTINGS.current_level].items if list(x[0]) not in wa]
        move_npcs = [x for x in SETTINGS.levels_list[SETTINGS.current_level].npcs if list(x[0]) not in wa]

        item_positions = [x[0] for x in SETTINGS.levels_list[SETTINGS.current_level].items if list(x[0]) in wa]
        npc_positions = [x[0] for x in SETTINGS.levels_list[SETTINGS.current_level].npcs if list(x[0]) in wa]

        possible_item_positions = [x for x in wa if tuple(wa) not in item_positions]
        temp_possible_npc_positions = [x for x in wa if tuple(wa) not in npc_positions]
        possible_npc_positions = []
        #Remove npc positions too close to the player
        for pos in temp_possible_npc_positions:
            x = abs(gamestate.player.player_map_pos[0] - pos[0])
            y = abs(gamestate.player.player_map_pos[1] - pos[1])

            if math.sqrt(x**2 + y**2) >= 8: #Length of vector between player and NPC
                possible_npc_positions.append(pos)

        for i in range(len(move_items)):
            #print("Moved item from ", move_items[i][0])
            index = SETTINGS.levels_list[SETTINGS.current_level].items.index(move_items[i]) #Get item index
            SETTINGS.levels_list[SETTINGS.current_level].items[index] = ((random.choice(possible_item_positions)), move_items[i][1]) #Choose new location for item
            possible_item_positions.remove(list(SETTINGS.levels_list[SETTINGS.current_level].items[index][0])) #Remove possible location
            #print("to ", SETTINGS.levels_list[SETTINGS.current_level].items[index][0])

        for i in range(len(move_npcs)):
            #print("Moved NPC from ", move_npcs[i][0])
            index = SETTINGS.levels_list[SETTINGS.current_level].npcs.index(move_npcs[i])
            SETTINGS.levels_list[SETTINGS.current_level].npcs[index] = ((random.choice(possible_npc_positions)), move_npcs[i][1], move_npcs[i][2])
            possible_npc_positions.remove(list(SETTINGS.levels_list[SETTINGS.current_level].npcs[index][0]))
            #print("to ", SETTINGS.levels_list[SETTINGS.current_level].npcs[index][0])

        #print("This level has %s items and %s NPC's" % (len(SETTINGS.levels_list[SETTINGS.current_level].items), len(SETTINGS.levels_list[SETTINGS.current_level].npcs)))