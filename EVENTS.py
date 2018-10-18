from pygame import USEREVENT
import pygame

# respond to player input
# TODO make explicit events for player inputs: up, down, left, right, move_left, mouse_right
EVENT_PLAYER_INPUT = USEREVENT

# timer to execute every second - well there abouts
TIMER_PLAYTIME = USEREVENT + 1

# timer for NPC update - NOT YET IMPLEMENTED
EVENT_NPC_UPDATE = USEREVENT + 2

# event for raycasting caluclations are done
EVENT_RAY_CASTING_CALCULATED = USEREVENT + 3

# Has the player moved? Recalculated Rays
EVENT_PLAYER_LOCATION_CHANGED = USEREVENT + 4

# Has the plays view moved? Recalculated Rays
EVENT_PLAYER_VIEW_CHANGED = USEREVENT + 5


def add_event_single(event, values = {}):
    if not pygame.event.peek(event):
        add_event(event, values)

def add_event(event, values = {}):
    pygame.event.post(
        pygame.event.Event(event, values)
    )
