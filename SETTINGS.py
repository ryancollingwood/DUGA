#Settings for DUGA
'''Game settings'''

current_level = 0
fps = 31
caption = "DUGA Beta v1.3"
mode = 1
volume = 1
music_volume = 1
fullscreen = False
menu_showing = True
#Below this point are the non-configurable game variables.
current_level_size = None
changing_level = False
quit_game = False
game_won = False
dt = 0
cfps = 0
statistics = {}
play_seconds = 0

'''Level settings'''
glevels_size = 4
glevels_amount = 100
#These are non-configurable.
levels_list = []
segments_list = []
clevels_list = []
glevels_list = []
tlevels_list = []
seed = None
playing_customs = False
playing_new = False
playing_tutorial = False


'''Canvas settings'''
canvas_target_width = 700    #700 #700
canvas_target_height = 550    #600 #550
# Below this point are the non-configurable canvas variables.
canvas_actual_width = 0
canvas_actual_height = 0
# What the height of the gameplay are less the HUD
canvas_game_area_height = canvas_target_height
canvas_aspect_ratio = 0
canvas_map_width = None
canvas_map_height = None
switch_mode = False
axes = (0, 0)
screen_shake = 0

#Below this point are the non-configurable raycasting variables.


'''Tile settings'''
from typing import List
from world.tile import Tile

#Below this point are the non-configurable tile variables.
rendered_tiles = []
all_tiles: List[Tile] = []
trigger_tiles: List[Tile] = []
all_solid_tiles: List[Tile] = []
walkable_area = []
dda_list = []
all_doors = []
end_angle = 0


'''Player settings'''
godmode = False



'''Texture settings'''
#Wall textures and sprites go here.

'''Weapon settings'''
#Settings for guns and ammo go here.
unlimited_ammo = False
#Below this point are non-configurable variables.

'''NPC settings'''
#NPC information goes here
ignore_player = False
#Below this point are non-configurable variables.


'''Inventory settings'''
#This is for scripts to access inventory data - Not configurable

'''Tile configurations'''
#Assign each kind of tile with a texture or sprite


#Create a new tile / sprite tile:
#1. Create texture and add it to TEXTURES.py in the marked area for tiles.
#2. Give the tile by ID the settings you want in dictionaries above.
#3. Make sure that all tiles has a texture or sprite. Invisible tiles can use null.png
#4. Note that Sprite tiles are not visible. The tile itself is not rendered.
#Note: A tile can be solid, but invisible, but not vice versa

#Create a new sprite (NPC):
#1. Create the texture and add it to TEXTURES.py in the marked area for NPC's
#2. Assign the sprite an ID and make sure the sprite is added to SETTINGS.all_sprites.
#3. Add the sprite (ID) to the texture_type dictionary above. Call it 'sprite'.
#4. Fill out the arguments to make a sprite (pos, path)

#Controls
#Overvej at lave justerbare controls

temp = []
