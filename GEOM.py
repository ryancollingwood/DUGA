import math
import SETTINGS
from numba import jit

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

    player_rect = SETTINGS.player_rect
    player_angle = SETTINGS.player_angle

    theta = tile_angle_relative_to_player(
        player_angle,
        player_rect.centerx, player_rect.centery,
        pos, x.rect.left, x.rect.right, x.rect.top, x.rect.bottom
    )

    if x.type == 'end':
        SETTINGS.end_angle = theta

    #theta = abs(theta)
    
    return theta


@jit(nopython=True)
def tile_angle_relative_to_player(
        player_angle,
        player_rect_centerx, player_rect_centery,
        pos, x_rect_left, x_rect_right, x_rect_top,  x_rect_bottom
):
    # find the position on each tile that is closest to middle_ray_pos
    xpos = max(x_rect_left, min(pos[0], x_rect_right)) - player_rect_centerx
    ypos = player_rect_centery - max(x_rect_top, min(pos[1], x_rect_bottom))
    theta = math.atan2(ypos, xpos)
    theta = math.degrees(theta)
    theta -= player_angle
    if theta < 0:
        theta += 360
    if theta > 180:
        theta -= 360
    return theta


@jit(nopython=True)
def get_camera_plane_for_angle(angle, player_rect_center, tile_size):
    # tan for right angle values result in undefined value
    # therefore add a tiny amount to the angle to mitigate this
    angle -= 0.001

    # Horizontal
    if angle < 180:
        H_y = int(player_rect_center[1] / tile_size) * tile_size
    else:
        H_y = int(player_rect_center[1] / tile_size) * tile_size + tile_size

    tan_radians_angle = math.tan(math.radians(angle))
    cos_radians_angle = math.cos(math.radians(angle))

    H_x = player_rect_center[0] + (player_rect_center[1] - H_y) / tan_radians_angle

    # Vertical
    if angle > 270 or angle < 90:
        V_x = int(player_rect_center[0] / tile_size) * tile_size + tile_size
    else:
        V_x = int(player_rect_center[0] / tile_size) * tile_size

    V_y = player_rect_center[1] + (player_rect_center[0] - V_x) * tan_radians_angle

    return H_x, H_y, V_x, V_y, angle, cos_radians_angle, tan_radians_angle


@jit(nopython=True)
def straight_line_distance(xpos, ypos):
    return math.sqrt(xpos * xpos + ypos * ypos)