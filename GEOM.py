import math

import SETTINGS


def sort_distance(x):
    if x == None:
        return 0
    else:
        return x.distance


def sort_atan(x):
    if SETTINGS.middle_ray_pos:
        pos = SETTINGS.middle_ray_pos
    elif SETTINGS.player_rect:
        pos = SETTINGS.player_rect.center
    else:
        return None
        
    #find the position on each tile that is closest to middle_ray_pos
    xpos = max(x.rect.left, min(pos[0], x.rect.right)) - SETTINGS.player_rect.centerx
    ypos = SETTINGS.player_rect.centery - max(x.rect.top, min(pos[1], x.rect.bottom))
    theta = math.atan2(ypos, xpos)
    theta = math.degrees(theta)
    theta -= SETTINGS.player_angle

    if theta < 0:
        theta += 360
    if theta > 180:
        theta -= 360

    if x.type == 'end':
        SETTINGS.end_angle = theta

    #theta = abs(theta)
    
    return theta