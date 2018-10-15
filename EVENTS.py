from pygame import USEREVENT

# respond to player input
EVENT_PLAYER_INPUT = USEREVENT

# timer to execute every second - well there abouts
TIMER_PLAYTIME = USEREVENT + 1

# timer for NPC update - NOT YET IMPLEMENTED
EVENT_NPC_UPDATE = USEREVENT + 2

# event for raycasting caluclations are done
EVENT_RAY_CASTING_CALCULATED = USEREVENT + 3