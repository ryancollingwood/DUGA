from pygame import USEREVENT

# timer to execute every second - well there abouts
TIMER_PLAYTIME = USEREVENT + 2

# timer for updating gamestate: npcs, items
TIMER_GAME_STATE_UPDATE = USEREVENT + 3

# timer for updating game visuals: raycasted walls, npcs, sprites
TIMER_GAME_VISUAL_UPDATE = USEREVENT + 4

# timer for NPC update - NOT YET IMPLEMENTED
EVENT_NPC_UPDATE = USEREVENT + 5