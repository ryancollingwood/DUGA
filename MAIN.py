#This is the MAIN script of DUGA. This is where the main loop is located and this is where all resources are loaded.
#All the classes will be located at the bottom of this script.

import pygame
import math
import os
import pickle
import logging
import sys
#-- Engine imports--
import SETTINGS
import PLAYER
import TEXTURES
import MAP
import LEVELS
import PATHFINDING
import TEXT
#-- Game imports --
import EFFECTS
import HUD
import INVENTORY
import ENTITIES
import GENERATION
import MENU
import MUSIC
import TUTORIAL
import consts.colours
import consts.geom
import consts.player
import consts.raycast
import consts.tile
import gamedata.items
import gamedata.npcs
import gamedata.textures
import gamedata.tiles
import gamestate.inventory
import gamestate.items
import gamestate.npcs
import gamestate.player
import gamestate.rendering
import gamestate.sprites
import render.raycast
from render.gamecanvas import GameCanvas

SECONDS_IN_MINUTE = 60
MILLISECONDS_IN_SECOND = 1000.0

FOV_MIN = 10
FOV_MAX = 100

pygame.init()
pygame.font.init()
pygame.display.set_mode((1,1))

#Load resources
class Load:

    def load_resources(self):
        ID = 0
        current_texture = 0
        self.timer = 0
        for texture in gamedata.textures.all_textures:
            if gamedata.tiles.texture_type[ID] == 'sprite':
                gamedata.textures.texture_list.append(pygame.image.load(texture))
            else:
                gamedata.textures.texture_list.append(Texture(texture, ID))
            ID += 1
        #Update the dictionary in SETTINGS
        for texture in gamedata.textures.texture_list:
            gamedata.tiles.tile_texture.update({current_texture : texture})
            current_texture += 1

        #Mixer goes under here as well
        pygame.mixer.init()

        #Load custom settings
        with open(os.path.join('data', 'settings.dat'), 'rb') as settings_file:
            settings = pickle.load(settings_file)
            
        consts.raycast.fov = settings['fov']
        consts.player.sensitivity = settings['sensitivity']
        SETTINGS.volume = settings['volume']
        SETTINGS.music_volume = settings['music volume']
        consts.raycast.resolution = settings['graphics'][0]
        consts.raycast.render = settings['graphics'][1]
        SETTINGS.fullscreen = settings['fullscreen']

        #Load statistics
        with open(os.path.join('data', 'statistics.dat'), 'rb') as stats_file:
            stats = pickle.load(stats_file)

        SETTINGS.statistics = stats

    def get_canvas_size(self):
        SETTINGS.canvas_map_width = len(SETTINGS.levels_list[SETTINGS.current_level].array[0]) * consts.tile.TILE_SIZE
        SETTINGS.canvas_map_height = len(SETTINGS.levels_list[SETTINGS.current_level].array) * consts.tile.TILE_SIZE
        SETTINGS.canvas_actual_width = SETTINGS.canvas_target_width
        SETTINGS.canvas_actual_height = SETTINGS.canvas_target_height
        SETTINGS.canvas_aspect_ratio = SETTINGS.canvas_actual_width / SETTINGS.canvas_actual_height
        gamestate.player.player_map_pos = SETTINGS.levels_list[SETTINGS.current_level].player_pos
        gamestate.player.player_pos[0] = int((SETTINGS.levels_list[SETTINGS.current_level].player_pos[0] * consts.tile.TILE_SIZE) + consts.tile.TILE_SIZE / 2)
        gamestate.player.player_pos[1] = int((SETTINGS.levels_list[SETTINGS.current_level].player_pos[1] * consts.tile.TILE_SIZE) + consts.tile.TILE_SIZE / 2)
        if len(gamedata.items.gun_list) != 0:
            for gun in gamedata.items.gun_list:
                gun.re_init()

    def load_entities(self):
        ENTITIES.load_guns()
        ENTITIES.load_npc_types()
        ENTITIES.load_item_types()

    def load_custom_levels(self):
        if not os.stat(os.path.join('data', 'customLevels.dat')).st_size == 0:
            with open(os.path.join('data', 'customLevels.dat'), 'rb') as file:
                custom_levels = pickle.load(file)
                
            for level in custom_levels:
                SETTINGS.clevels_list.append(LEVELS.Level(level))

        with open(os.path.join('data', 'tutorialLevels.dat'), 'rb') as file:
            tutorial_levels = pickle.load(file)

        for level in tutorial_levels:
            SETTINGS.tlevels_list.append(LEVELS.Level(level))

    def load_new_level(self):    
        #Remove old level info
        gamestate.npcs.npc_list = []
        gamestate.items.all_items = []
        SETTINGS.walkable_area = []
        SETTINGS.all_tiles = []
        SETTINGS.all_doors = []
        SETTINGS.all_solid_tiles = []
        gamestate.sprites.all_sprites = []
        
        #Retrieve new level info
        self.get_canvas_size()
        gameMap.__init__(SETTINGS.levels_list[SETTINGS.current_level].array)
        gamestate.player.player_rect.center = (SETTINGS.levels_list[SETTINGS.current_level].player_pos[0] * consts.tile.TILE_SIZE, SETTINGS.levels_list[SETTINGS.current_level].player_pos[1] * consts.tile.TILE_SIZE)
        gamestate.player.player_rect.centerx += consts.tile.TILE_SIZE / 2
        gamestate.player.player_rect.centery += consts.tile.TILE_SIZE / 2
        gamePlayer.real_x = gamestate.player.player_rect.centerx
        gamePlayer.real_y = gamestate.player.player_rect.centery

        if consts.raycast.shade and SETTINGS.levels_list[SETTINGS.current_level].shade:
            consts.raycast.shade_rgba = SETTINGS.levels_list[SETTINGS.current_level].shade_rgba
            consts.raycast.shade_visibility = SETTINGS.levels_list[SETTINGS.current_level].shade_visibility

        if SETTINGS.current_level > 0:
            SETTINGS.changing_level = False
            gamestate.player.player_states['fade'] = True
        else:
            gamestate.player.player_states['fade'] = True
            gamestate.player.player_states['black'] = True

        gamestate.player.player_states['title'] = True
                
        SETTINGS.walkable_area = list(PATHFINDING.pathfind(gamestate.player.player_map_pos, SETTINGS.all_tiles[-1].map_pos))
        gameMap.move_inaccessible_entities()
        ENTITIES.spawn_npcs()
        ENTITIES.spawn_items()

#Texturing
class Texture:
    
    def __init__(self, file_path, ID):
        self.slices = []
        self.texture = pygame.image.load(file_path).convert()
        self.rect = self.texture.get_rect()
        self.ID = ID

        self.create_slices()

    def create_slices(self): # Fills list - Nothing else
        row = 0
        for row in range(self.rect.width):
            self.slices.append(row)
            row += 1

from consts import geom

def sort_distance(x):
    if x is None:
        return 0
    else:
        return x.distance

def sort_atan(x):
    if gamestate.rendering.middle_ray_pos:
        pos = gamestate.rendering.middle_ray_pos
    else:
        pos = gamestate.player.player_rect.center
        
    #find the position on each tile that is closest to middle_ray_pos
    xpos = max(x.rect.left, min(pos[0], x.rect.right)) - gamestate.player.player_rect.centerx
    ypos = gamestate.player.player_rect.centery - max(x.rect.top, min(pos[1], x.rect.bottom))
    theta = math.atan2(ypos, xpos)
    theta = math.degrees(theta)
    theta -= consts.player.player_angle

    if theta < geom.DEGREES_0:
        theta += geom.DEGREES_360
    if theta > geom.DEGREES_180:
        theta -= geom.DEGREES_360

    if x.type == 'end':
        SETTINGS.end_angle = theta

    theta = abs(theta)
    
    return(theta)

def render_screen(canvas):
    '''render_screen(canvas) -> Renders everything but NPC\'s'''
    SETTINGS.rendered_tiles = []

    #Get sprite positions
    for sprite in gamestate.sprites.all_sprites:
        sprite.get_pos(canvas)

    #Sort zbuffer and solid tiles
    gamestate.rendering.zbuffer = sorted(gamestate.rendering.zbuffer, key=sort_distance, reverse=True)
    SETTINGS.all_solid_tiles = sorted(SETTINGS.all_solid_tiles, key=lambda x: (x.type, sort_atan(x), x.distance))

    #Calculate which tiles are visible
    for tile in SETTINGS.all_solid_tiles:
        if tile.distance and gamedata.tiles.tile_visible[tile.ID]:
            if sort_atan(tile) <= consts.raycast.fov:
                if tile.distance < consts.raycast.render * consts.tile.TILE_SIZE:
                    SETTINGS.rendered_tiles.append(tile)
                            
            elif tile.distance <= consts.tile.TILE_SIZE * 1.5:
                SETTINGS.rendered_tiles.append(tile)
                

    #Render all items in zbuffer
    for item in gamestate.rendering.zbuffer:
        if item == None:
            pass
        elif item.type == 'slice':
            canvas.blit(item.tempslice, (item.xpos, item.rect.y))
            if item.vh == 'v':
                #Make vertical walls slightly darker
                canvas.blit(item.darkslice, (item.xpos, item.rect.y))
            if consts.raycast.shade:
                canvas.blit(item.shade_slice, (item.xpos, item.rect.y))
                
        else:
            if item.new_rect.right > 0 and item.new_rect.x < SETTINGS.canvas_actual_width and item.distance < (
                    consts.raycast.render * consts.tile.TILE_SIZE):
                item.draw(canvas)
                
    #Draw weapon if it is there
    if gamestate.inventory.current_gun:
        gamestate.inventory.current_gun.draw(gameCanvas.canvas)
    elif gamestate.inventory.next_gun:
        gamestate.inventory.next_gun.draw(gameCanvas.canvas)

    #Draw Inventory and effects
    if gamestate.player.player_states['invopen']:
        gameInv.draw(gameCanvas.canvas)
    EFFECTS.render(gameCanvas.canvas)

    gamestate.rendering.zbuffer = []

    #Draw HUD and canvas
    gameCanvas.window.blit(canvas, (SETTINGS.axes))
    gameHUD.render(gameCanvas.window)

    #Draw tutorial strings
    if SETTINGS.levels_list == SETTINGS.tlevels_list:
            tutorialController.control(gameCanvas.window)

def update_game():
    if gamestate.npcs.npc_list:
        for npc in gamestate.npcs.npc_list:
            if not npc.dead:
                npc.think()

    gamestate.inventory.ground_weapon = None
    for item in gamestate.items.all_items:
        item.update()

    if (SETTINGS.changing_level and gamestate.player.player_states['black']) or gamestate.player.player_states['dead']:
        if SETTINGS.current_level < len(SETTINGS.levels_list)-1 and SETTINGS.changing_level:
            SETTINGS.current_level += 1
            SETTINGS.statistics['last levels']
            gameLoad.load_new_level()
        
        elif (SETTINGS.current_level == len(SETTINGS.levels_list) - 1 or gamestate.player.player_states['dead']) and gameLoad.timer < 4 and not gamestate.player.player_states['fade']:
            if not gamestate.player.player_states['dead'] and SETTINGS.current_level == len(SETTINGS.levels_list)-1 and text.string != 'YOU  WON':
                text.update_string('YOU  WON')
            elif gamestate.player.player_states['dead'] and text.string != 'GAME  OVER':
                text.update_string('GAME  OVER')
            text.draw(gameCanvas.window)
            if not SETTINGS.game_won:
                gameLoad.timer = 0
            SETTINGS.game_won = True
            gameLoad.timer += SETTINGS.dt
            
        #Reset for future playthroughs
        elif SETTINGS.game_won and gameLoad.timer >= 4:
            gameLoad.timer = 0
            SETTINGS.game_won = False
            menuController.current_type = 'main'
            menuController.current_menu = 'score'
            calculate_statistics()
            SETTINGS.menu_showing = True
            SETTINGS.current_level = 0

def calculate_statistics():
    #Update 'all' stats
    SETTINGS.statistics['all enemies'] += SETTINGS.statistics['last enemies']
    SETTINGS.statistics['all ddealt'] += SETTINGS.statistics['last ddealt']
    SETTINGS.statistics['all dtaken'] += SETTINGS.statistics['last dtaken']
    SETTINGS.statistics['all shots'] += SETTINGS.statistics['last shots']
    SETTINGS.statistics['all levels'] += SETTINGS.statistics['last levels']

    #Update 'best' stats
    if SETTINGS.statistics['best enemies'] < SETTINGS.statistics['last enemies']:
        SETTINGS.statistics['best enemies'] = SETTINGS.statistics['last enemies']
    if SETTINGS.statistics['best ddealt'] < SETTINGS.statistics['last ddealt']:
        SETTINGS.statistics['best ddealt'] = SETTINGS.statistics['last ddealt']
    if SETTINGS.statistics['best dtaken'] < SETTINGS.statistics['last dtaken']:
        SETTINGS.statistics['best dtaken'] = SETTINGS.statistics['last dtaken']
    if SETTINGS.statistics['best shots'] < SETTINGS.statistics['last shots']:
        SETTINGS.statistics['best shots'] = SETTINGS.statistics['last shots']
    if SETTINGS.statistics['best levels'] < SETTINGS.statistics['last levels']:
        SETTINGS.statistics['best levels'] = SETTINGS.statistics['last levels']
    #'last' statistics will be cleared when starting new game in menu.
    with open(os.path.join('data', 'statistics.dat'), 'wb') as saved_stats:
        pickle.dump(SETTINGS.statistics, saved_stats)
    


#Main loop
def main_loop():
    game_exit = False
    clock = pygame.time.Clock()
    logging.basicConfig(filename = os.path.join('data', 'CrashReport.log'), level=logging.WARNING)

#    allfps = []
    
    while not game_exit:
        gamestate.rendering.zbuffer = []
        if SETTINGS.play_seconds >= SECONDS_IN_MINUTE:
            SETTINGS.statistics['playtime'] += 1
            SETTINGS.play_seconds = 0
        else:
            SETTINGS.play_seconds += SETTINGS.dt
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT or SETTINGS.quit_game:
                game_exit = True

##                b = 0
##                for x in allfps:
##                    b += x
##                print(b/len(allfps))
                menuController.save_settings()
                calculate_statistics()
                pygame.quit()
                sys.exit(0)

        try:
            #Music
            musicController.control_music()
            
            if SETTINGS.menu_showing and menuController.current_type == 'main':
                gameCanvas.window.fill(consts.colours.WHITE)
                menuController.control()

                #Load custom maps
                if SETTINGS.playing_customs:
                    SETTINGS.levels_list = SETTINGS.clevels_list
                    gameLoad.get_canvas_size()
                    gameLoad.load_new_level()

                #Load generated maps
                elif SETTINGS.playing_new:
                    mapGenerator.__init__()
                    mapGenerator.generate_levels(SETTINGS.glevels_amount, SETTINGS.glevels_size)
                    SETTINGS.levels_list = SETTINGS.glevels_list
                    gameLoad.get_canvas_size()
                    gameLoad.load_new_level()

                #Or.. If they are playing the tutorial
                elif SETTINGS.playing_tutorial:
                    SETTINGS.levels_list = SETTINGS.tlevels_list
                    gameLoad.get_canvas_size()
                    gameLoad.load_new_level()

            elif SETTINGS.menu_showing and menuController.current_type == 'game':
                menuController.control()
                
            else:
                #Update logic
                gamePlayer.control(gameCanvas.canvas)
                
                if consts.raycast.fov >= FOV_MAX:
                    consts.raycast.fov = FOV_MAX
                elif consts.raycast.fov <= FOV_MIN:
                    consts.raycast.fov = FOV_MIN

                if SETTINGS.switch_mode:
                    gameCanvas.change_mode()

                #Render - Draw
                gameRaycast.calculate()
                gameCanvas.draw()
                
                
                if SETTINGS.mode == 1:
                    render_screen(gameCanvas.canvas)

                    #BETA
                  #  beta.draw(gameCanvas.window)
                
                elif SETTINGS.mode == 0:
                    gameMap.draw(gameCanvas.window)                
                    gamePlayer.draw(gameCanvas.window)

                    for x in gamestate.rendering.raylines:
                        pygame.draw.line(gameCanvas.window, consts.colours.RED, (x[0][0] / 4, x[0][1] / 4), (x[1][0] / 4, x[1][1] / 4))
                    gamestate.rendering.raylines = []

                    for i in gamestate.npcs.npc_list:
                        if i.rect and i.dist <= consts.raycast.render * consts.tile.TILE_SIZE * 1.2:
                            pygame.draw.rect(gameCanvas.window, consts.colours.RED, (i.rect[0] / 4, i.rect[1] / 4, i.rect[2] / 4, i.rect[3] / 4))
                        elif i.rect:
                            pygame.draw.rect(gameCanvas.window, consts.colours.DARKGREEN, (i.rect[0] / 4, i.rect[1] / 4, i.rect[2] / 4, i.rect[3] / 4))

                update_game()

        except Exception as e:
            menuController.save_settings()
            calculate_statistics()
            logging.warning("DUGA has crashed. Please send this report to MaxwellSalmon, so he can fix it.")
            logging.exception("Error message: ")
            pygame.quit()
            sys.exit(0)

        #Update Game
        pygame.display.update()
        delta_time = clock.tick(SETTINGS.fps)
        SETTINGS.dt = delta_time / MILLISECONDS_IN_SECOND
        SETTINGS.cfps = int(clock.get_fps())
        #pygame.display.set_caption(SETTINGS.caption % SETTINGS.cfps)

       # allfps.append(clock.get_fps())

#Probably temporary object init
#SETTINGS.current_level = 5 #temporary
if __name__ == '__main__':
    gameLoad = Load()
    gameLoad.load_resources()
    gameLoad.load_entities()
    gameLoad.load_custom_levels()

    mapGenerator = GENERATION.Generator()
    mapGenerator.generate_levels(1,2)
    SETTINGS.levels_list = SETTINGS.glevels_list

    gameLoad.get_canvas_size()

    #Setup and classes

    text = TEXT.Text(0, 0,"YOU  WON", consts.colours.WHITE, "DUGAFONT.ttf", 48)
    beta = TEXT.Text(5, 5,"DUGA  BETA  BUILD  V. 1.3", consts.colours.WHITE, "DUGAFONT.ttf", 20)
    text.update_pos(SETTINGS.canvas_actual_width/2 - text.layout.get_width()/2, SETTINGS.canvas_target_height/2 - text.layout.get_height()/2)

    #Classes for later use
    gameMap = MAP.Map(SETTINGS.levels_list[SETTINGS.current_level].array)
    gameCanvas = GameCanvas(SETTINGS.canvas_map_width, SETTINGS.canvas_map_height)
    gamePlayer = PLAYER.Player(gamestate.player.player_pos)
    gameRaycast = render.raycast.Raycast(gameCanvas.canvas, gameCanvas.window)
    gameInv = INVENTORY.inventory({'bullet': 150, 'shell':25, 'ferromag' : 50})
    gameHUD = HUD.hud()

    #More loading - Level specific
    gameLoad.load_new_level()

    #Controller classes
    menuController = MENU.Controller(gameCanvas.window)
    musicController = MUSIC.Music()
    tutorialController = TUTORIAL.Controller()

    #Run at last
    main_loop()

